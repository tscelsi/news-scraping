from typing import Any
from datetime import datetime
from models import Article

test_article = {
    'outlet': 'theage',
    'url': 'test_article1',
    'created': datetime(2023, 1, 1, 18, 30, 0),
    'modified': datetime(2023, 1, 1, 18, 30, 0),
    'published': datetime(2023, 1, 1, 18, 30, 0),
    'title': 'Test Article 1',
    'body': 'This is a test article.',
    'wordCount': 5,
    'tags': ['test-tag'],
    'extra': None,
}


async def list_articles(client: Any, *args, **kwargs):
    return [
        'test_article1',
        'test_article2',
    ]


async def get_article(client: Any, url: str):
    return Article(**test_article)
