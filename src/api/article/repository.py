from bson import ObjectId
from pymongo.results import DeleteResult
from pymongo import ReturnDocument
from models import Article, DBArticle
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

class ArticleRepository:
    @classmethod
    def factory(cls):
        return cls()

    @staticmethod
    def create(article: Article) -> DBArticle:
        result = _db.articles.insert_one(article.dict())
        return DBArticle(**{'_id': result.inserted_id, **article.dict()})

    @staticmethod
    def read(id: str) -> DBArticle:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.articles.find_one({'_id': ObjectId(id)})
        if not result:
            raise RepositoryException('Not found')
        return DBArticle(**result)

    @staticmethod
    def list() -> list[DBArticle]:
        result = _db.articles.find()
        return [DBArticle(**r) for r in result]

    @staticmethod
    def update(id: str, article: Article) -> DBArticle:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.articles.find_one_and_update(
            {'_id': ObjectId(id)}, {'$set': article.dict()},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise RepositoryException('Not found')
        return DBArticle(**result)

    @staticmethod
    def delete(id: str) -> DeleteResult:
        if not is_valid_id(id):
            raise RepositoryException('Invalid id')
        result = _db.articles.delete_one({'_id': ObjectId(id)})
        if not result.deleted_count:
            raise RepositoryException('Not found')
        return result
