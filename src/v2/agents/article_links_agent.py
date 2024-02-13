from asyncache import cached
from bs4 import BeautifulSoup, Tag
from cachetools import LRUCache
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from consts import SRC_DIR
from v2.client import get
from v2.html_parser import get_unique_anchor_traces
from v2.registry import JsonFileRegistry
from v2.soup_helpers import create_soup_for_article_link_retrieval

MAX_REVISIONS = 3
TEMPLATE_DIR = SRC_DIR / "v2" / "templates"


class ArticleLinks(BaseModel):
    links: list[str] = Field(
        description="A list of all the links pointing to articles in the html",
    )


class ArticleLinksAgent:
    """This agent is responsible for finding news article links in a web page.

    It finds an initial set and then revises that set if it has doubts.
    """

    SYSTEM_MESSAGE = SystemMessagePromptTemplate.from_template_file(
        TEMPLATE_DIR / "html_expert.txt", input_variables=[]
    )
    article_link_trace_registry: JsonFileRegistry = JsonFileRegistry(
        "article_link_traces"
    )

    def __init__(self) -> None:
        self.chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)

    def _create_initial_prompt(self, html_chunk: str, format_instructions: str):
        initial_instructions_template = HumanMessagePromptTemplate.from_template_file(
            TEMPLATE_DIR / "article_links_desired_info.txt",
            input_variables=["format_instructions", "html_chunk"],
        )
        initial_chat_prompt = ChatPromptTemplate.from_messages(
            [self.SYSTEM_MESSAGE, initial_instructions_template]
        )
        initial_messages = initial_chat_prompt.format_prompt(
            html_chunk=html_chunk, format_instructions=format_instructions
        ).to_messages()
        return initial_messages

    def _create_revision_prompt(
        self,
        html_chunk: str,
        format_instructions: str,
        article_links_model: ArticleLinks,
    ):
        revision_instructions_template = HumanMessagePromptTemplate.from_template_file(
            TEMPLATE_DIR / "revise_desired_info.txt",
            input_variables=["html_chunk", "format_instructions", "article_links"],
        )
        revision_chat_prompt = ChatPromptTemplate.from_messages(
            [self.SYSTEM_MESSAGE, revision_instructions_template]
        )
        revision_messages = revision_chat_prompt.format_prompt(
            html_chunk=html_chunk,
            article_links=article_links_model.links,
            format_instructions=format_instructions,
        ).to_messages()
        return revision_messages

    @cached(LRUCache(maxsize=128))
    def _run_llm_loop(self, html_chunk: str) -> ArticleLinks:
        """The main loop for finding article links.

        Args:
            html_chunk (str): The HTML chunk to search for article links.

        Returns:
            _type_: _description_
        """
        parser = PydanticOutputParser(pydantic_object=ArticleLinks)
        print("Creating prompts...")
        initial_messages = self._create_initial_prompt(
            html_chunk, parser.get_format_instructions()
        )
        print(initial_messages)
        print("Invoking initial messages...")
        response = self.chat.invoke(initial_messages)
        print(response)
        initial_model = parser.invoke(response)
        print(initial_model)
        # iters = 0
        final_model = initial_model
        # while iters < MAX_REVISIONS:
        #     revision_messages = self._create_revision_prompt(
        #         html_chunk, parser.get_format_instructions(), final_model
        #     )
        #     print(revision_messages)
        #     print(f"Invoking revision messages {iters + 1}...")
        #     response = self.chat.invoke(revision_messages)
        #     print(response)
        #     revised_model = parser.invoke(response)
        #     print(revised_model)
        #     if revised_model.links == initial_model.links:
        #         print("No new links found. Returning...")
        #         return revised_model
        #     final_model = revised_model
        #     iters += 1
        return final_model

    def find_article_links(self, soup: BeautifulSoup) -> list[str]:
        chunks = self._split_into_chunks(soup)
        article_links: list[str] = []
        for chunk in chunks:
            article_link_model = self._run_llm_loop(chunk)
            article_links.extend(article_link_model.links)
        return article_links

    def _split_into_chunks(self, soup: BeautifulSoup) -> list[str]:
        """Split the HTML into chunks for ingestion by the LLM.

        Each chunk is created by taking a node from the HTML. If that node
        is less than the MAX_CHARS, then it is a chunk. If it is still larger than
        MAX_CHARS, then we call _split_into_chunks on it.
        """
        MAX_CHARS = 50000
        chunks = []
        for child in [child for child in soup.contents if isinstance(child, Tag)]:
            if len(str(child)) < MAX_CHARS:
                chunks.append(str(child))
            else:
                chunks.extend(self._split_into_chunks(child))
        return chunks

    def _create_scraping_traces(
        self, soup: BeautifulSoup
    ) -> tuple[list[list[str]], list[str]]:
        """Generate the traces (i.e. unique paths from the root of the HTML to article
        links) for the given HTML page."""
        article_links = self.find_article_links(soup)
        traces = get_unique_anchor_traces(article_links, soup)
        return traces, article_links

    async def run(self, url: str) -> tuple[list[list[str]], list[str]]:
        """Run the agent on the given URL."""
        response = await get(url)
        soup = create_soup_for_article_link_retrieval(response.text)
        traces, article_links = self._create_scraping_traces(soup)
        return traces, article_links
