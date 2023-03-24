from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError
from pymongo.results import DeleteResult
from pymongo import ReturnDocument
from models.scrapingjob import ScrapingJobStatus, DBScrapingJob, UpdateScrapingJob
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


class ScrapingJobRepository:

    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def upsert(user_id: str) -> DBScrapingJob:
        """Create or update a scraping job entry in the database. This will only
        be called when a new feed run is triggered. Therefore, if a scraping job
        already exists, it will be updated with a status of running, else a new
        one will be created.

        Args:
            user_id (str): The unique identifier of the user who triggered the feed run

        Raises:
            RepositoryException: If the user id is invalid

        Returns:
            DBScrapingJob: The newly created or updated scraping job
        """
        if not is_valid_id(user_id):
            raise RepositoryException('Invalid id')
        result = _db.scrapingjob.find_one_and_update(
            {'userId': ObjectId(user_id)}, {
                '$set': {
                    'status': ScrapingJobStatus.running.value,
                    'modified_at': datetime.utcnow(),
                },
                '$setOnInsert': {
                    'userId': ObjectId(user_id),
                    'created_at': datetime.utcnow(),
                },
            }, upsert=True, return_document=ReturnDocument.AFTER)
        return DBScrapingJob(**result)

    @staticmethod
    def update(id: str, update_obj: dict):
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        try:
            validated_dict = UpdateScrapingJob(**update_obj).dict()
        except ValidationError as e:
            raise RepositoryException(e.json())
        result = _db.scrapingjob.find_one_and_update(
            {'_id': ObjectId(id)}, {'$set': validated_dict}, return_document=ReturnDocument.AFTER)
        return DBScrapingJob(**result)

    @staticmethod
    def read(id: str) -> DBScrapingJob:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.feedoutlet.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBScrapingJob(**result)

    @staticmethod
    def list(id: str) -> list[DBScrapingJob]:
        result = _db.feedoutlet.find({'feedId': ObjectId(id)})
        return [DBScrapingJob(**r) for r in result]
