from fastapi import APIRouter, HTTPException
from ..lib.db import Db
from models import DBFeedOutlet
from .repository import FeedOutletRepository, RepositoryException

router = APIRouter(prefix='/feedoutlet', tags=['feedoutlet'])
db = Db()


@router.get('/{feed_id}', description='List all outlets relating to a feed', response_model=list[DBFeedOutlet])
def list_feedoutlets(feed_id: str):
    return FeedOutletRepository.list(feed_id)


@router.get('/{id}', description='Get a feedoutlet by id', response_model=DBFeedOutlet | None)
def read_feedoutlet(id: str):
    try:
        result = FeedOutletRepository.read(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result
