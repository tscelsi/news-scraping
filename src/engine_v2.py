import importlib
from typing import Awaitable
import functools
from pymongo import UpdateOne
import aiometer
from models import Article
from db import Db
import logging
from scrapers.core import CoreScraper
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class Enginev2:
    """Implements the same engine, but with scrapers as classes"""
    def __init__(
        self,
        module_name: str,
        prefix: str,
        max_at_once: int = 10,
        max_per_second: int = 10,
        db_uri: str | None = None,
        db_must_connect: bool = False,
        debug: bool = False,
    ):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self._name = module_name
        self.prefix = prefix
        self.max_at_once = max_at_once
        self.max_per_second = max_per_second
        logger.info(f'{self._name};initialising engine...')
        # import module containing list_articles and get_article
        logger.debug(f'{self._name};importing module scrapers.{self._name}')
        _module = importlib.import_module(
            'scrapers.' + self._name)
        self._db = Db(db_uri, must_connect=db_must_connect)
        self.scraper: CoreScraper = _module.Scraper()
    
    async def run(self) -> Awaitable[list[Article]]:
        logger.info(f'{self._name};getting article urls...')
        # this may raise, we want it to. We can't continue without it.
        article_urls = await self.scraper.list_articles(self.prefix)
        if self.scraper.articles:
            logger.info(
                f'{self._name};extracted {len(self.scraper.articles)} without calling get_article().')
            articles = self.scraper.articles
        else:
            logger.info(
                f'{self._name};got {len(article_urls)} article urls. Beginning article text retrieval...')
            logger.debug(f'{self._name};{article_urls}')
            # only runs if list_articles doesn't populate list of Articles
            jobs = [functools.partial(self.scraper.get_article, url, self.prefix)
                    for url in article_urls]
            articles = await aiometer.run_all(
                jobs,
                max_at_once=self.max_at_once,
                max_per_second=self.max_per_second,
            )
        articles = [x for x in filter(lambda x: x is not None, articles)]
        logger.info(
            f'{self._name};found text for {len(articles)} articles. Updating in db...')
        logger.debug(f'{self._name};{articles}')
        if not self._db.empty:
            db_ops = [
                UpdateOne(
                    {'url': article.url, 'outlet': article.outlet},
                    {'$set': {**article.dict(), 'url': article.url}},
                    upsert=True
                ) for article in articles
            ]
            write_result = self._db.get_collection(
                'Article').bulk_write(db_ops)
            logger.info(
                f'{self._name};updated {write_result.modified_count} articles. inserted {write_result.upserted_count} articles.')
            logger.debug(f'{self._name};{write_result}')
        else:
            logger.info(f'{self._name};no db connection. skipping db update.')
        return articles
