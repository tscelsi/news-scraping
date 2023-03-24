from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from ..lib.db import Db
from models import DBFeed, OutletConfig
from .repository import FeedRepository, RepositoryException
from ..scrapingjob import ScrapingJobRepository, ScrapingJobStatus
from main import run_from_list
from ..feedoutlet import list_feedoutlets
from ..lib.dependencies import user_id

router = APIRouter(prefix='/feed', tags=['feed'])
db = Db()


@router.get('', description='List all feeds', response_model=list[DBFeed])
def list_feeds():
    return FeedRepository.list()


@router.get('/{id}', description='Get a feed by id', response_model=DBFeed | None)
def read_feed(id: str):
    try:
        result = FeedRepository.read(id)
    except RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    return result


@router.post('/{id}/run', description='Gather articles for a particular news feed', status_code=202)
async def run_feed(id: str, background_tasks: BackgroundTasks, user_id: str = Depends(user_id)):
    try:
        outlets = list_feedoutlets(id)
        config = [OutletConfig(**o.dict()).dict() for o in outlets]
    except HTTPException as e:
        raise e
    except KeyError as e:
        raise HTTPException(status_code=400, detail='Invalid feed format')
    # run scrape
    background_tasks.add_task(task, user_id, config)


async def task(user_id: str | ObjectId, config: list[OutletConfig]):
    # triggers scraping job status to running
    scraping_job = ScrapingJobRepository.upsert(user_id)
    await run_from_list(config)
    timestamp = datetime.utcnow()
    # update the scraping job with fresh data
    ScrapingJobRepository.update(scraping_job.id, {
        'status': ScrapingJobStatus.finished.value,
        'completed_at': timestamp,
        'modified_at': timestamp,
    })
