import pytest
import os
import mongomock
from bson import ObjectId

@pytest.fixture
def env():
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017'


@mongomock.patch(servers=(('localhost', 27017),))
def test_user_repository_update_overrides_field_previous_values(env):
    from src.api.user.repository import UserRepository
    from src.api.lib.db import Db
    db = Db()
    insert_result = db.user.insert_one({
        'id': ObjectId('640ddfc8f9ebf203fe2c8282'),
        'daily_scrape_count': 0,
    })
    result = UserRepository.update(insert_result.inserted_id, {
        'daily_scrape_count': 1,
        'unwantedkey': "unwantedvalue"
    })
    assert result.daily_scrape_count == 1
    assert 'unwantedkey' not in result.dict(exclude_none=True).keys()
