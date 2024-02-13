import os
import sys

import pymongo
import pymongo.errors as errors
from bson import ObjectId
from pydantic import BaseModel
from pymongo.collection import Collection

from models import Feed


def is_valid_id(id: str):
    try:
        ObjectId(id)
        return True
    except Exception:
        return False


class MockDeleteResult:
    deleted_count = 1


class MockCollection:
    def __init__(self, model: BaseModel):
        self._model = model

    def find(self, *args, **kwargs):
        model = self._model(name="test", outlets=[])
        return [{**model.dict(), "_id": ObjectId()}]

    def find_one(self, *args, **kwargs):
        model = self._model(name="test", outlets=[])
        _id = args[0].get("_id")
        return {**model.dict(), "_id": _id or ObjectId()}

    def find_one_and_update(self, *args, **kwargs):
        model = self._model(name="test", outlets=[])
        _id = args[0].get("_id")
        return {**model.dict(), "_id": _id or ObjectId()}

    def insert_one(self, *args, **kwargs):
        _obj = args[0]
        return {**Feed(**_obj).dict(), "_id": ObjectId()}

    def delete_one(self, *args, **kwargs):
        return MockDeleteResult()


class MockDatabase:
    def __init__(self):
        self.strategies = MockCollection(Feed)


class MockClient:
    def __init__(self, uri: str):
        self._uri = uri
        self.news = MockDatabase()

    @property
    def strategies(self) -> Collection:
        return self.news.strategies


MONGO_URI = os.getenv("MONGO_URI")
ENV = os.getenv("ENV")
try:
    if not MONGO_URI:
        raise ValueError("Make sure to set the MONGO_URI environment variable.")
    client = pymongo.MongoClient(MONGO_URI)
except errors.ConnectionFailure as e:
    print(e)
    sys.exit(1)


class Db:
    @property
    def articles(self) -> Collection:
        return client.news.articles

    @property
    def strategies(self) -> Collection:
        return client.news.strategies

    @property
    def feed(self) -> Collection:
        return client.news.Feed

    @property
    def feedoutlet(self) -> Collection:
        return client.news.FeedOutlet

    @property
    def feedsource(self) -> Collection:
        return client.news.FeedSource

    @property
    def scrapingjob(self) -> Collection:
        return client.news.ScrapingJob

    @property
    def user(self) -> Collection:
        return client.news.User

    @property
    def source(self) -> Collection:
        return client.news.Source

    @property
    def v2article(self) -> Collection:
        return client.news.V2Article

    @property
    def trace(self) -> Collection:
        return client.news.Trace
