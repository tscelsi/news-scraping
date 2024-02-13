from urllib.parse import urlparse

from bson import ObjectId

from api.lib.db import Db, is_valid_id
from api.lib.exceptions import RepositoryException, RepositoryInvalidIdError
from v2.models.source import DBSource, Source

_db = Db()


class SourceRepository:
    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def create(source: Source) -> DBSource:
        result = _db.source.insert_one(source.model_dump())
        return DBSource(**{"_id": result.inserted_id, **source.model_dump()})

    @staticmethod
    def read(id: str) -> DBSource:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError("Invalid id")
        result = _db.source.find_one({"_id": ObjectId(id)})
        if not result:
            raise RepositoryException("Not found")
        return DBSource(**result)

    @staticmethod
    def read_by_url(url: str) -> DBSource:
        try:
            urlparse(url)
        except Exception:
            raise RepositoryException("Invalid url")
        result = _db.source.find_one({"url": url})
        if not result:
            raise RepositoryException("Not found")
        return DBSource(**result)

    @staticmethod
    def list(id: str) -> list[DBSource]:
        result = _db.source.find({"feedId": ObjectId(id)})
        return [DBSource(**r) for r in result]

    @staticmethod
    def read_or_create(source: Source) -> DBSource:
        result = _db.source.find_one({"url": source.url})
        if result:
            return DBSource(**result)
        result = _db.source.insert_one(source.model_dump())
        return DBSource(**{"_id": result.inserted_id, **source.model_dump()})
