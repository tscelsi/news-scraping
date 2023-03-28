from fastapi import APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache
import importlib
from ..lib.db import Db
from ..lib.exceptions import RepositoryInvalidIdError, RepositoryException
from models import CustomBaseModel
from .repository import SourceRepository

router = APIRouter(prefix='/source', tags=['source'])
db = Db()


def create_url(source: str, endpoint: str):
    return '/'.join([source, endpoint.strip("/")])

class PokeResponse(CustomBaseModel):
    url: str
    success: bool

@router.get('/{id}/poke', description='Checks if a source endpoint is scrapeable', response_model=PokeResponse)
@cache(expire=600)
async def read_feedoutlet(id: str, endpoint: str = Query(..., description='The endpoint to scrape')):
    try:
        source = SourceRepository.read(id)
    except RepositoryInvalidIdError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    _module = importlib.import_module(
        'scrapers.' + source.ref)
    try:
        await _module.list_articles(endpoint)
    except Exception as e:
        return PokeResponse(url=create_url(source.base_url, endpoint), success=False)
    return PokeResponse(url=create_url(source.base_url, endpoint), success=True)
