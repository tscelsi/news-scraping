from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from ..lib.db import Db
from models import DBFeed, OutletConfig
from models.user import DBUser
from .repository import FeedRepository, RepositoryException
from ..scrapingjob import ScrapingJobRepository, ScrapingJobStatus
from ..user import UserRepository
from main import run_from_list
from ..feedoutlet import list_feedoutlets
from ..lib.dependencies import on_user

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
async def run_feed(id: str, background_tasks: BackgroundTasks, user: DBUser = Depends(on_user)):
    # check if user hasn't already scraped today:
    if isinstance(user.daily_scrape_count, int) and user.daily_scrape_count > 0:
        raise HTTPException(
            status_code=400, detail='daily scrape limit reached')
    try:
        outlets = list_feedoutlets(id)
        config = [OutletConfig(**o.dict()).dict() for o in outlets]
    except HTTPException as e:
        raise e
    except KeyError as e:
        raise HTTPException(status_code=400, detail='Invalid feed format')
    # run scrape
    background_tasks.add_task(task, user, config)


async def task(user: DBUser, config: list[OutletConfig]):
    # increment the user's daily scrape count so that we don't spin off
    # multiple scraping jobs
    if not user.daily_scrape_count:
        user.daily_scrape_count = 0
    UserRepository.update(
        user.id, {'daily_scrape_count': user.daily_scrape_count + 1})
    # triggers scraping job status to running
    scraping_job = ScrapingJobRepository.upsert(user.id)
    await run_from_list(config)
    timestamp = datetime.utcnow()
    # update the scraping job with fresh data
    ScrapingJobRepository.update(scraping_job.id, {
        'status': ScrapingJobStatus.finished.value,
        'completed_at': timestamp,
        'modified_at': timestamp,
    })
