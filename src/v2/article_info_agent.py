from datetime import datetime

from bs4 import BeautifulSoup, Tag
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from consts import ROOT_DIR

TEMPLATE_DIR = ROOT_DIR / "src" / "v2" / "templates"


class ArticleMetadata(BaseModel):
    url: str = Field(
        description="The URL of the article",
    )
    scrape_time: datetime = Field(description="The time the article was last scraped")


class ArticleInfo(BaseModel):
    title: str = Field(
        description="The title of the article",
    )
    published_at: datetime = Field(
        description="The date the article was published",
    )


class ArticleInfoAgent:
    """Once a new article link is found, this agent is responsible for finding the
    traces for the article page itself.
    """

    SYSTEM_MESSAGE = SystemMessagePromptTemplate.from_template_file(
        TEMPLATE_DIR / "html_expert.txt", input_variables=[]
    )

    def __init__(self) -> None:
        self.chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)

    def _get_desired_information(self) -> str:
        properties = ArticleInfo.schema()["properties"]
        descs = []
        for property in properties.values():
            descs.append(property["description"])
        desired_information = " ".join(descs[:-1]) + f" and {descs[-1]}"
        return desired_information.lower()

    def _create_initial_prompt(self, html_chunk: str, format_instructions: str):
        desired_information = self._get_desired_information()
        initial_instructions_template = HumanMessagePromptTemplate.from_template_file(
            TEMPLATE_DIR / "article_info_desired_info.txt",
            input_variables=[
                "format_instructions",
                "html_chunk",
                "desired_information",
            ],
        )
        initial_chat_prompt = ChatPromptTemplate.from_messages(
            [self.SYSTEM_MESSAGE, initial_instructions_template]
        )
        initial_messages = initial_chat_prompt.format_prompt(
            html_chunk=html_chunk,
            format_instructions=format_instructions,
            desired_information=desired_information,
        ).to_messages()
        return initial_messages

    def _run_llm_loop(self, html_chunk: str) -> ArticleInfo:
        """The main loop for finding article links.

        Args:
            html_chunk (str): The HTML chunk to search for article links.

        Returns:
            _type_: _description_
        """
        parser = PydanticOutputParser(pydantic_object=ArticleInfo)
        print("Creating prompts...")
        initial_messages = self._create_initial_prompt(
            html_chunk, parser.get_format_instructions()
        )
        print(initial_messages)
        print("Invoking initial messages...")
        response = self.chat.invoke(initial_messages)
        print(response)
        model = parser.invoke(response)
        print(model)
        return model

    def find_article_info(self, soup: BeautifulSoup) -> list[str]:
        chunks = self._split_into_chunks(soup)
        article_info: list[ArticleInfo] = []
        for chunk in chunks:
            article_info_model = self._run_llm_loop(chunk)
            article_info.append(article_info_model)
        return article_info

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
