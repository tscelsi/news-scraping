from typing import Any

from bson import ObjectId
from pydantic import ValidationError
from pymongo import ReturnDocument

from api.lib.db import Db, is_valid_id
from api.lib.exceptions import (
    ObjectNotFoundError,
    RepositoryException,
    RepositoryInvalidIdError,
)
from v2.models.trace import DBTrace, Trace, UpdateTrace

_db = Db()


class TraceRepository:
    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def create(trace: Trace) -> DBTrace:
        result = _db.trace.insert_one(trace.model_dump())
        return DBTrace(**{"_id": result.inserted_id, **trace.model_dump()})

    @staticmethod
    def read(id: str) -> DBTrace:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError("Invalid id")
        result = _db.trace.find_one({"_id": ObjectId(id)})
        if not result:
            raise ObjectNotFoundError("Not found")
        return DBTrace(**result)

    @staticmethod
    def read_by(filter: dict[str, Any]) -> DBTrace:
        result = _db.trace.find_one(filter)
        if not result:
            raise ObjectNotFoundError("Not found")
        return DBTrace(**result)

    @staticmethod
    def update(id: str, update_obj: dict):
        if not is_valid_id(id):
            raise RepositoryInvalidIdError("Invalid id")
        try:
            validated_dict = UpdateTrace(**update_obj).model_dump(exclude_unset=True)
        except ValidationError as e:
            raise RepositoryException(e.json())
        result = _db.trace.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": validated_dict},
            return_document=ReturnDocument.AFTER,
        )
        return DBTrace(**result)
