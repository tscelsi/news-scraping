from bson import ObjectId
from models import DBFeedOutlet
from ..lib.db import Db, is_valid_id
from ..lib.exceptions import RepositoryException, RepositoryInvalidIdError

_db = Db()

class FeedOutletRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def read(id: str) -> DBFeedOutlet:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError('Invalid id')
        result = _db.feedoutlet.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBFeedOutlet(**result)

    @staticmethod
    def list(id: str) -> list[DBFeedOutlet]:
        result = _db.feedoutlet.find({'feedId': ObjectId(id)})
        return [DBFeedOutlet(**r) for r in result]
