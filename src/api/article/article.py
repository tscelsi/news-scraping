from fastapi import APIRouter, HTTPException
from ..lib.db import Db
from models import DBArticle
from .repository import ArticleRepository, RepositoryException

router = APIRouter(prefix='/article', tags=['article'])
db = Db()


# @router.post('',
#     description='Create a new article',
#     response_model=DBArticle,
#     )
# def create_article(article: Article) -> DBArticle:
#     result = ArticleRepository.create(article)
#     return result


@router.get('', description='List all articles', response_model=list[DBArticle])
def list_articles():
    return ArticleRepository.list()


@router.get('/{id}', description='Get a article by id', response_model=DBArticle | None)
def read_article(id: str):
    try:
        result = ArticleRepository.read(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result


# @router.post('/{id}', description='Update a article by id', response_model=DBArticle | None)
# def update_article(id: str, article: Article):
#     try:
#         result = ArticleRepository.update(id, article)
#     except RepositoryException as e:
#         raise HTTPException(status_code=400, detail=e.message)
#     return result


@router.delete('/{id}', description='Delete an article by id')
def delete_article(id: str):
    try:
        _ = ArticleRepository.delete(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
