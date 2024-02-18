import Levenshtein
from bs4 import BeautifulSoup, Tag

from consts import HEADERS
from v2.client import get
from v2.html_parser import trace_tag_to_root


def get_h1(soup: BeautifulSoup, expected: str | None = None) -> Tag:
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 1:
        return h1_tags[0]
    if len(h1_tags) > 1 and expected:
        best_sim = 0
        best_h1 = None
        for h1 in h1_tags:
            similarity = Levenshtein.ratio(h1.get_text(), expected)
            if similarity > best_sim:
                best_sim = similarity
                best_h1 = h1
        return best_h1
    return None


class ArticleInfoAgent:
    """Once a new article link is found, this agent is responsible for finding the
    traces for the article page itself. Currently only the article title.
    """

    async def create_title_trace(self, soup: BeautifulSoup) -> list[str]:
        """Creates a trace to navigate to the title of the article.

        Args:
            soup (BeautifulSoup): The soup object to navigate.

        Returns:
            list[str]: The trace to navigate to the title.
        """
        h1_text = get_h1(soup)
        if h1_text:
            title_trace = trace_tag_to_root(h1_text)
            return title_trace[::-1]
        raise ValueError("No title found")

    async def run(self, url: str) -> list[str]:
        response = await get(url, headers=HEADERS, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        title_trace = await self.create_title_trace(soup)
        return title_trace
