import pytest
import os
from bson import ObjectId
from datetime import datetime
import mongomock


@pytest.fixture
def env():
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017'


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_upsert_creates_successfully(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    result = ScrapingJobRepository.upsert('640ddfc8f9ebf203fe2c9171')
    assert set(list(result.dict(exclude_none=True).keys())) == set([
        'status', 'id', 'userId', 'created_at', 'modified_at'
    ])
    assert result.status == 'running'


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_upsert_raises_on_invalid_id(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    with pytest.raises(Exception):
        ScrapingJobRepository.upsert('sdas')


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_upsert_updates_preexisting_document(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    from src.api.lib.db import Db
    db = Db()
    db.scrapingjob.insert_one({
        'userId': ObjectId('640ddfc8f9ebf203fe2c8282'),
        'status': 'finished',
        'created_at': datetime.fromisoformat('2021-09-01'),
    })
    result = ScrapingJobRepository.upsert('640ddfc8f9ebf203fe2c8282')
    assert result.status == 'running'
    # doesn't get updated by the create method unless inserted
    assert result.created_at == datetime.fromisoformat('2021-09-01')


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_update_ignores_irrelevant_fields(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    upsert_result = ScrapingJobRepository.upsert('640ddfc8f9ebf203fe2c8282')
    result = ScrapingJobRepository.update(upsert_result.id, {
        'status': 'error',
        'granola': 'is good',
    })
    assert result.status == 'error'
    assert 'granola' not in result.dict(exclude_none=True).keys()


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_update_can_insert_non_existent_fields(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    upsert_result = ScrapingJobRepository.upsert('640ddfc8f9ebf203fe2c8282')
    result = ScrapingJobRepository.update(upsert_result.id, {
        'status': 'finished',
        'articleIds': [ObjectId('640ddfc8f9ebf203fe2c8282')]
    })
    assert result.articleIds == [ObjectId('640ddfc8f9ebf203fe2c8282')]


@mongomock.patch(servers=(('localhost', 27017),))
def test_scrapingjob_repository_update_overrides_field_previous_values(env):
    from src.api.scrapingjob.repository import ScrapingJobRepository
    from src.api.lib.db import Db
    db = Db()
    insert_result = db.scrapingjob.insert_one({
        'userId': ObjectId('640ddfc8f9ebf203fe2c8282'),
        'status': 'finished',
        'created_at': datetime.fromisoformat('2021-09-01'),
        'articleIds': [ObjectId('640ddfc8f9ebf203fe2c8282')]
    })
    result = ScrapingJobRepository.update(insert_result.inserted_id, {
        'status': 'finished',
        'articleIds': [ObjectId('330ddfc8f9ebf203fe2c8284')]
    })
    assert result.articleIds == [ObjectId('330ddfc8f9ebf203fe2c8284')]
