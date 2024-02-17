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
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
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


def get_plan(html_str: str, state: ArticleLinkReWOO):
    prompt_template = get_article_link_plan_template()
    prompt = prompt_template.format(html_chunk=html_str)
    # Find all matches in the sample text
    matches = re.findall(regex_pattern, prompt)
    return {"steps": matches, "plan_string": prompt, "html_str": html_str}


def _get_current_task(state: ArticleLinkReWOO):
    if state["results"] is None:
        return 1
    if len(state["results"]) == len(state["steps"]):
        return None
    else:
        return len(state["results"]) + 1


def tool_execution(state: ArticleLinkReWOO):
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


solve_prompt = """Make an informed decision about which of the following links are links to blog-like article web pages.
To decide this, you need to consider the text contained in the link, the URL of the link, and the context in which the link is found.
The information for each link is provided as a tuple, where each tuple item corresponds to the following:
1. The anchor text of the link.
2. The href of the link.
3. Whether the anchor is nested inside an <article> tag.
4. Whether the anchor is nested inside an <li> tag.
5. Whether the href ends with .html.

Use your judgement to decide which of the links are likely to be blog-like article web pages.
Bear in mind there may be no links to news articles at all.
Be careful to not include links that don't point to news articles in your response.
Do not modify the link text in any way for example by removing or adding words.

Now solve the question or task according to provided Evidence above. Respond with the answer
directly with no extra words.

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
    article_link_tuples = eval(state["results"]["#E2"])
    prompt = solve_prompt.format(
        link_tuples=article_link_tuples,
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
    return {"result": ArticleLinks(links=confirmed_links)}


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

    response = httpx.get(
        "https://www.nytimes.com/international/section/business/energy-environment"
    )
    from v2.soup_helpers import create_soup

    soup = create_soup(response.text)
    graph = StateGraph(ArticleLinkReWOO)
    graph.add_node("plan", functools.partial(get_plan, str(soup)))
    graph.add_node("tool", tool_execution)
    graph.add_node("solve", solve2)
    graph.add_edge("plan", "tool")
    graph.add_edge("solve", END)
    graph.add_conditional_edges("tool", _route)
    graph.set_entry_point("plan")

    app = graph.compile()
    state = app.invoke({})
    print("HI")
