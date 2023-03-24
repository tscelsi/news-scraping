from bson import ObjectId
from pymongo.results import DeleteResult
from pymongo import ReturnDocument
from models import Feed, DBFeed
from ..lib.db import Db

class RepositoryException(Exception):
    message: str
    def __init__(self, message: str):
        self.message = message


def is_valid_id(id: str):
    try:
        ObjectId(id)
        return True
    except Exception:
        return False

_db = Db()

class FeedRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def read(id: str) -> DBFeed:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.feed.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBFeed(**result)

    @staticmethod
    def list() -> list[DBFeed]:
        result = _db.feed.find()
        return [DBFeed(**r) for r in result]
