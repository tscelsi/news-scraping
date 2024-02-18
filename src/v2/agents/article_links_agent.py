import functools

from bs4 import BeautifulSoup
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from consts import HEADERS
from v2.agents.rewoo import ArticleLinkReWOO, init, solve2
from v2.client import get
from v2.html_parser import get_unique_anchor_traces
from v2.soup_helpers import create_soup


class ArticleLinks(BaseModel):
    links: list[str] = Field(
        description="A list of all the links pointing to articles in the html",
    )


class ArticleLinksAgent:
    """This agent is responsible for finding news article links in a web page."""

    def __init__(self) -> None:
        self.chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)

    def find_article_links(self, soup: BeautifulSoup) -> ArticleLinks:
        """Create a ReWOO Agent to find the article links in the given HTML.

        Args:
            soup (BeautifulSoup): The HTML to be parsed.

        Returns:
            ArticleLinks: A list of the links the ReWOO agent believes point to articles in the HTML.
        """
        graph = StateGraph(ArticleLinkReWOO)
        graph.add_node("init", functools.partial(init, str(soup)))
        graph.add_node("solve", solve2)
        graph.add_edge("init", "solve")
        graph.add_edge("solve", END)
        graph.set_entry_point("init")
        app = graph.compile()
        state = app.invoke({})
        self.candidate_links = state["candidate_links"]
        return state["result"]

    def _create_scraping_traces(
        self, soup: BeautifulSoup
    ) -> tuple[list[list[str]], ArticleLinks]:
        """Generate the traces (i.e. unique paths from the root of the HTML to article
        links) for the given HTML page."""
        article_links = self.find_article_links(soup)
        traces = get_unique_anchor_traces(article_links.links, soup)
        return traces, article_links

    async def run(self, url: str) -> tuple[list[list[str]], ArticleLinks]:
        """Run the agent on the given URL."""
        response = await get(url, headers=HEADERS, follow_redirects=True)
        soup = create_soup(response.text)
        traces, article_links = self._create_scraping_traces(soup)
        return traces, article_links
