from bson import ObjectId
from models.source import DBSource
from ..lib.db import Db, is_valid_id
from ..lib.exceptions import RepositoryException, RepositoryInvalidIdError

_db = Db()


class SourceRepository:
    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def read(id: str) -> DBSource:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError('Invalid id')
        result = _db.source.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBSource(**result)

    @staticmethod
    def list(id: str) -> list[DBSource]:
        result = _db.source.find({'feedId': ObjectId(id)})
        return [DBSource(**r) for r in result]
