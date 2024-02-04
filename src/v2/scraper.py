from typing import Any, Optional

import httpx
from bs4 import Tag
from pydantic import BaseModel, Field

from exceptions import BaseException
from v2.html_parser import find_anchor_tags_from_traces
from v2.models.article import Article
from v2.registry.article_links import ARTICLE_LINKS_REGISTRY
from v2.soup_helpers import create_soup_with_body_as_root

URL = str


class ScraperError(BaseException):
    pass


class RegistryInitialisationError(Exception):
    pass


class Scraper(BaseModel):
    """The core abstract scraping engine class. The general idea is to populate the classes
    articles list with Article objects. Usually, this is done by calling get_article() on
    each URL returned by list_articles(). However, this also allows for list_articles to populate
    the articles list directly. The engine will only call get_articles if there are no articles in
    the article list after list_articles() has been called.
    """

    domain: Optional[str] = Field(description="The domain of the website being scraped")
    articles: list[Article] = []

    def _maybe_set_domain(self, url: str):
        try:
            self.domain = url.split("//")[1].split("/")[0]
        except IndexError:
            pass

    def _get_from_registry(self, key: str, registry: dict) -> Any:
        entry = registry.get(key)
        if not entry:
            raise RegistryInitialisationError(f"No traces found in registry for {key}")
        return entry

    async def get_article_info(self, url: URL, prefix: str) -> Article | None:
        """Gets the article content and creates an article object. All errors should
        be caught and should return None on error"""
        raise NotImplementedError("Please implement get_articles()")

    async def get_article_links(self, url: str) -> list[Tag]:
        """List articles from the page found at <url>."""
        self._maybe_set_domain(url)
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        html = response.text
        body_soup = create_soup_with_body_as_root(html)
        article_link_traces = self._get_from_registry(
            url.strip("/"), ARTICLE_LINKS_REGISTRY
        )
        article_links = find_anchor_tags_from_traces(body_soup, article_link_traces)
        # TODO: check if href is a valid URL, may need to concat domain to href
        return [x.attrs["href"] for x in article_links]
