from bs4 import Tag
from html_parser import find_tags_from_traces
from httpx import AsyncClient
from soup_helpers import create_soup_with_body_as_root

REGISTRY = {
    "https://www.news.com.au/": [
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "article",
            "article",
            "a",
        ],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "article",
            "h4",
            "a",
        ],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "article",
            "a",
        ],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "article",
            "h4",
            "a",
        ],
        ["body", "div", "section", "section", "div", "div", "div", "article", "a"],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "div",
            "article",
            "a",
        ],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "div",
            "div",
            "article",
            "span",
            "a",
        ],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "div",
            "div",
            "article",
            "h4",
            "a",
        ],
        ["body", "div", "section", "section", "div", "div", "a"],
        [
            "body",
            "div",
            "section",
            "section",
            "div",
            "div",
            "div",
            "div",
            "div",
            "div",
            "article",
            "a",
        ],
    ]
}


class RegistryInitialisationError(Exception):
    pass


class ArticleListScraper:
    def __init__(self, url: str):
        self.url = url
        self.traces = self._init_traces(url)

    def _init_traces(self, url: str):
        traces = REGISTRY.get(url, [])
        if not traces:
            raise RegistryInitialisationError(f"No traces found in registry for {url}")
        return traces

    async def run(self) -> list[Tag]:
        """Retrieves a list of articles from a web page."""
        async with AsyncClient() as client:
            response = await client.get(self.url)
            response.raise_for_status()
            html = response.text
            body_soup = create_soup_with_body_as_root(html)
            article_links = find_tags_from_traces(body_soup, self.traces)
            return article_links
