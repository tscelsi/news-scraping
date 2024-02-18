import functools
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiometer
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, ConfigDict, Field

from api.v2.trace.repository import TraceRepository
from consts import HEADERS
from exceptions import BaseException
from models import PyObjectId
from v2.client import get
from v2.client.helpers import get_domain
from v2.html_parser import find_anchor_tags_from_traces, find_text_from_traces
from v2.models.article import Article
from v2.soup_helpers import create_soup

logger = logging.getLogger(__name__)
URL = str


class ScraperError(BaseException):
    pass


class RegistryInitialisationError(Exception):
    pass


class Scraper(BaseModel):
    """The core v2 scraping engine class."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
    )
    sourceId: PyObjectId
    domain: Optional[str] = Field(
        default=None, description="The domain of the website being scraped"
    )
    articles: list[Article] = []
    max_at_once: int = 10
    max_per_second: int = 10

    def _set_domain(self, url: str):
        if not self.domain:
            self.domain = get_domain(url)

    def _get_from_registry(self, key: str, registry: dict) -> Any:
        entry = registry.get(key)
        if not entry:
            raise RegistryInitialisationError(f"No traces found in registry for {key}")
        return entry

    def _maybe_add_prefix_to_href(self, href: str):
        if href.startswith("http"):
            return href
        # assume https
        href = href.lstrip("/")
        return f"https://{self.domain}/{href}"

    async def get_article_info(self, url: URL) -> Article | None:
        """Gets the article content and creates an article object. All errors should
        be caught and should return None on error"""
        self._set_domain(url)
        try:
            response = await get(url, headers=HEADERS, follow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            trace_obj = TraceRepository.read_by(
                {"sourceId": self.sourceId, "type": "article_title"}
            )
            article_title = find_text_from_traces(soup, trace_obj.traces)
            return Article(
                domain=self.domain,
                url=url,
                title=article_title,
                scrape_time=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Error getting article info for {url}")
            logger.exception(e)
            # swallow exception so we don't exit the scrape run
            return None

    async def get_article_links(self, url: str) -> list[str]:
        """List articles from the page found at <url>."""
        self._set_domain(url)
        response = await get(url, headers=HEADERS, follow_redirects=True)
        body_soup = create_soup(response.text)
        trace_obj = TraceRepository.read_by(
            {"sourceId": self.sourceId, "type": "article_links"}
        )
        article_links = find_anchor_tags_from_traces(body_soup, trace_obj.traces)
        return list(
            set(
                [self._maybe_add_prefix_to_href(x.attrs["href"]) for x in article_links]
            )
        )

    async def run(self, url: str) -> list[Article]:
        """Full run of scrape, from article link acquisition to article information
        retrieval.

        Args:
            url (str): The URL to initially retrieve article links from.

        Returns:
            Awaitable[list[Article]]: A list of article information.
        """
        self._set_domain(url)
        logger.info(f"{self.domain};getting article urls...")
        # this may raise, we want it to. We can't continue without it.
        article_urls = await self.get_article_links(url)
        logger.info(
            f"{self.domain};got {len(article_urls)} article urls. Beginning article text retrieval..."
        )
        logger.debug(f"{self.domain};{article_urls}")
        jobs = [functools.partial(self.get_article_info, url) for url in article_urls]
        articles = await aiometer.run_all(
            jobs,
            max_at_once=self.max_at_once,
            max_per_second=self.max_per_second,
        )
        articles = [x for x in articles if x is not None]
        logger.info(
            f"{self.domain};found text for {len(articles)} articles. Updating in db..."
        )
        logger.debug(f"{self.domain};{articles}")
        return articles
