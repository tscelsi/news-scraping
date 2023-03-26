from bson import ObjectId
from models import DBFeed
from ..lib.db import Db, is_valid_id
from ..lib.exceptions import RepositoryException, RepositoryInvalidIdError


_db = Db()

class FeedRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def read(id: str) -> DBFeed:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError('Invalid id')
        result = _db.feed.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBFeed(**result)

    @staticmethod
    def list() -> list[DBFeed]:
        result = _db.feed.find()
        return [DBFeed(**r) for r in result]
