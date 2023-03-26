from bson import ObjectId
from pydantic import ValidationError
from pymongo import ReturnDocument
from models.user import UpdateUser, DBUser
from ..lib.db import Db, is_valid_id
from ..lib.exceptions import RepositoryException, RepositoryInvalidIdError

_db = Db()


class UserRepository:
    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def update(id: str, update_obj: dict) -> DBUser:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError('Invalid id')
        try:
            validated_dict = UpdateUser(**update_obj).dict()
        except ValidationError as e:
            raise RepositoryException(e.json())
        result = _db.user.find_one_and_update(
            {'_id': ObjectId(id)}, {'$set': validated_dict}, return_document=ReturnDocument.AFTER)
        return DBUser(**result)

    @staticmethod
    def read(id: str) -> DBUser:
        if not is_valid_id(id):
            raise RepositoryInvalidIdError('Invalid id')
        result = _db.user.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBUser(**result)
