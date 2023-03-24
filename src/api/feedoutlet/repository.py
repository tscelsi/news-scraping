from bson import ObjectId
from pymongo.results import DeleteResult
from pymongo import ReturnDocument
from models import FeedOutlet, DBFeedOutlet
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

class FeedOutletRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def read(id: str) -> DBFeedOutlet:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.feedoutlet.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBFeedOutlet(**result)

    @staticmethod
    def list(id: str) -> list[DBFeedOutlet]:
        result = _db.feedoutlet.find({'feedId': ObjectId(id)})
        return [DBFeedOutlet(**r) for r in result]
