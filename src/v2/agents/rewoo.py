import functools
import re
from typing import Any, Dict, List, TypedDict

import Levenshtein
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from consts import SRC_DIR
from v2.agents.tools.article_links_tools import (
    extract_anchor_information,
    list_anchor_tag_info,
)

TEMPLATE_DIR = SRC_DIR / "v2" / "templates"
regex_pattern = r"(?:\s*Plan:\s*(.+?)\s*(#E\d+)\s*=\s*(\w+)\s*\[(.+)\](?=\s*Plan:))*\s*Plan:\s*(.+?)\s*(#E\d+)\s*=\s*(\w+)\s*\[(.+)\]$"
model = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)


class ArticleLinks(BaseModel):
    links: list[str] = Field(
        description="A list of all the links pointing to articles in the html",
    )


class ArticleLinkReWOO(TypedDict):
    task: str
    plan_string: str
    steps: List
    results: dict
    result: ArticleLinks
    candidate_links: list[tuple[str, str]]
    html_str: str


def get_rewoo_prompt_template():
    with open(TEMPLATE_DIR / "ReWOO" / "plan_prompt.txt", "r") as f:
        return ChatPromptTemplate.from_messages([("user", f.read())])


def get_article_link_plan_template():
    with open(TEMPLATE_DIR / "ReWOO" / "article_link_plan_template.txt", "r") as f:
        return f.read()


def _get_planner() -> RunnableSerializable[Dict, Any]:
    prompt_template = get_rewoo_prompt_template()
    planner = prompt_template | model
    return planner


def init(html_str: str, state: ArticleLinkReWOO):
    return {"html_str": html_str}


def _get_current_task(state: ArticleLinkReWOO):
    if state["results"] is None:
        return 1
    if len(state["results"]) == len(state["steps"]):
        return None
    else:
        return len(state["results"]) + 1


def tool_execution(state: ArticleLinkReWOO):  # -> dict[str, dict]:
    """Worker node that executes the tools of a given plan."""
    _step = _get_current_task(state)
    _, step_name, tool, tool_input = state["steps"][_step - 1]
    _results = state["results"] or {}
    for k, v in _results.items():
        tool_input = tool_input.replace(k, v)
    if tool == "ListAnchors":
        result = list_anchor_tag_info.run(tool_input)
    elif tool == "ExtractAnchorInformation":
        result = extract_anchor_information.run(
            {"html_str": state["html_str"], "anchors_str": tool_input}
        )
    else:
        raise ValueError
    _results[step_name] = str(result)
    return {"results": _results}


"""3. Whether the anchor is nested inside an <article> tag - NOT AS IMPORTANT
4. Whether the anchor is nested inside an <li> tag - NOT AS IMPORTANT
5. Whether the href ends with .html - IMPORTANT"""

solve_prompt = """Make an informed decision about which of the following links are links to blog-like article web pages.
To decide this, you need to consider all the information provided to you for each link.
The information for each link is provided as a tuple, where each tuple item corresponds respectively to:
1. The anchor text of the link
2. The href of the link

Use your judgement to decide which of the links are likely to be blog-like article web pages.
Bear in mind there may be no links to news articles at all.
Be careful to not include links that don't point to news articles in your response.
Do not modify the link text in any way for example by removing or adding words.

Now solve the question or task according to provided Evidence above.

Links: {link_tuples}
{format_instructions}
Response:"""


def get_index(link: str, iterable: list) -> int | None:
    try:
        return iterable.index(link)
    except ValueError:
        return None


def get_corresponding_link(link_tuples: list[tuple[str, str]], candidate_link: str):
    anchor_texts = [x[0] for x in link_tuples]
    hrefs = [x[1] for x in link_tuples]
    for href in hrefs:
        if href in candidate_link:
            return href
        elif candidate_link in href:
            return href
    for anchor_text in anchor_texts:
        if anchor_text in candidate_link:
            return hrefs[anchor_texts.index(anchor_text)]
        elif candidate_link in anchor_text:
            return hrefs[anchor_texts.index(anchor_text)]
    # if the link is not found in the anchor text or href, we use a fuzzy match to check
    # that something isn't just slighty off. It must be a pretty close match to qualify.
    best_match = max(
        link_tuples, key=lambda x: Levenshtein.ratio(x[0], candidate_link) * 0.5
    )
    if Levenshtein.ratio(best_match[0], candidate_link) > 0.8:
        return best_match[1]
    return None


def solve2(state: ArticleLinkReWOO):
    """Provide the solver with the original html, and the result of the final tool."""
    parser = PydanticOutputParser(pydantic_object=ArticleLinks)
    # 1. get anchor tags
    anchors_str = list_anchor_tag_info.run(state["html_str"])
    # 2. extract anchor information
    article_link_tuples = extract_anchor_information.run(
        {"html_str": state["html_str"], "anchors_str": anchors_str}
    )
    prompt = solve_prompt.format(
        link_tuples=[(x[0], x[1]) for x in article_link_tuples],
        format_instructions=parser.get_format_instructions(),
    )
    result = model.invoke(prompt)
    parsed_output = parser.invoke(result.content)
    confirmed_links = []
    for link in parsed_output.links:
        # check that the link returned exists either in the textual content of anchor or the href
        # if not, omit. If it's the textual content, replace with the href
        corresponding_link = get_corresponding_link(article_link_tuples, link)
        if corresponding_link:
            confirmed_links.append(corresponding_link)
    return {
        "result": ArticleLinks(links=confirmed_links),
        "candidate_links": article_link_tuples,
    }


def _route(state):
    _step = _get_current_task(state)
    if _step is None:
        # We have executed all tasks
        return "solve"
    else:
        # We are still executing tasks, loop back to the "tool" node
        return "tool"


if __name__ == "__main__":
    import httpx

    response = httpx.get("https://www.aljazeera.com/us-canada/")
    from v2.soup_helpers import create_soup

    soup = create_soup(response.text)
    graph = StateGraph(ArticleLinkReWOO)
    graph.add_node("init", functools.partial(init, str(soup)))
    graph.add_node("solve", solve2)
    graph.add_edge("init", "solve")
    graph.add_edge("solve", END)
    graph.set_entry_point("init")
    # graph.add_node("tool", tool_execution)
    # graph.add_conditional_edges("tool", _route)

    app = graph.compile()
    state = app.invoke({})
    print("HI")
