from exceptions import BaseException
from models.article import Article, ArticleType

URL = str
Source = ArticleType


class ScraperError(BaseException):
    pass


class CoreScraper:
    """The core abstract scraping engine class. The general idea is to populate the classes
    articles list with Article objects. Usually, this is done by calling get_article() on
    each URL returned by list_articles(). However, this also allows for list_articles to populate
    the articles list directly. The engine will only call get_articles if there are no articles in
    the article list after list_articles() has been called.
    """

    BASE_HREF: str = None
    SOURCE: Source = None

    def __init__(self):
        if not self.BASE_HREF or not self.SOURCE:
            raise ScraperError(
                "Please provide a BASE_HREF and SOURCE in the child class."
            )

    async def get_article(self, url: URL, prefix: str) -> Article | None:
        """Gets the article content and creates an article object. All errors should
        be caught and should return None on error"""
        raise NotImplementedError("Please implement get_articles()")

    async def list_articles(self, prefix: str) -> list[URL]:
        """List articles from the page found at self.BASE_HREF + prefix."""
        raise NotImplementedError("Please implement list_articles()")
