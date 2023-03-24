import argparse
import importlib
from typing import Callable, Awaitable, Any
import asyncio
import functools
from confection import registry
import catalogue
from pymongo import UpdateOne
import httpx
import aiometer
from models import Article
from db import Db
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

registry.engine = catalogue.create('engine', 'engines', entry_points=True)


@registry.engine.register('engine.v1')
def _factory(module: str,
             path: str,
             max_at_once: int = 10,
             max_per_second: int = 10,
             db_uri: str | None = None,
             db_must_connect: bool = False,
             debug: bool = False):
    return Engine(module,
                  path,
                  max_at_once=max_at_once,
                  max_per_second=max_per_second,
                  db_uri=db_uri,
                  db_must_connect=db_must_connect,
                  debug=debug)


class Engine:
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
        self._list_articles: Callable[[
            httpx.AsyncClient, Any], Awaitable[list[str]]] = _module.list_articles
        self._get_article: Callable[[
            httpx.AsyncClient, str], Awaitable[Article]] = _module.get_article

    async def run(self) -> Awaitable[list[Article]]:
        async with httpx.AsyncClient() as client:
            logger.info(f'{self._name};getting article urls...')
            # this may raise, we want it to. We can't continue without it.
            article_urls = await self._list_articles(client, self.prefix)
            logger.info(
                f'{self._name};got {len(article_urls)} article urls. Beginning article text retrieval...')
            logger.debug(f'{self._name};{article_urls}')
            jobs = [functools.partial(self._get_article, client, url, self.prefix)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized news outlet scraper.')
    parser.add_argument(
        'config', type=str, help='path to config file. This path should be relative to the root directory. For examples, see the templates/ folder.')
    parser.add_argument(
        '--db', dest='db_uri', help='a mongodb connection string.'
    )
    parser.add_argument(
        '--debug', action='store_true', help='enable debug logging.'
    )
    args = parser.parse_args()
    engine = Engine(args.config, db_uri=args.db_uri, debug=args.debug)
    asyncio.run(engine.run())
