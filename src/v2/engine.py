import functools
import logging
from typing import Awaitable

import aiometer
from dotenv import load_dotenv
from pymongo import UpdateOne

from db import Db
from v2.client.helpers import get_domain
from v2.models.article import Article
from v2.scraper import Scraper

load_dotenv()

logger = logging.getLogger(__name__)


class Engine:
    def __init__(
        self,
        url: str,
        max_at_once: int = 10,
        max_per_second: int = 10,
        db_uri: str | None = None,
        db_must_connect: bool = False,
        debug: bool = False,
    ):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self._name = get_domain(url)
        self.url = url
        self.max_at_once = max_at_once
        self.max_per_second = max_per_second
        logger.info(f"{self._name};initialising engine...")
        self._db = Db(db_uri, must_connect=db_must_connect)
        self.scraper: Scraper = Scraper(
            max_at_once=max_at_once,
            max_per_second=max_per_second,
        )

    async def run(self) -> Awaitable[list[Article]]:
        articles = await self.scraper.run(self.url)
        if not self._db.empty:
            db_ops = [
                UpdateOne(
                    {"url": article.url, "outlet": article.outlet},
                    {"$set": {**article.dict(), "url": article.url}},
                    upsert=True,
                )
                for article in articles
            ]
            write_result = self._db.get_collection("Article").bulk_write(db_ops)
            logger.info(
                f"{self._name};updated {write_result.modified_count} articles. inserted {write_result.upserted_count} articles."
            )
            logger.debug(f"{self._name};{write_result}")
        else:
            logger.info(f"{self._name};no db connection. skipping db update.")
        return articles
