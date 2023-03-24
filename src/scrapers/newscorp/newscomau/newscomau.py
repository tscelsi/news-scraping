import logging
from datetime import datetime
from pydantic import ValidationError
import json
from bs4 import BeautifulSoup
import httpx

from consts import HEADERS
from models import Article


logger = logging.getLogger(__name__)

OUTLET = 'news.com.au'
ARTICLE_BASE_HREF = 'https://www.news.com.au/'


async def list_articles(client: httpx.AsyncClient, path: str) -> list[str]:
    res = await client.get(ARTICLE_BASE_HREF + path, headers=HEADERS)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.findAll('article')
    article_urls = [article.h4.a['href'] for article in articles]
    return article_urls


async def get_article(client: httpx.AsyncClient, url: str, path: str) -> Article:
    response = await client.get(url, headers=HEADERS)
    if response.status_code != 200:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    metadata = json.loads(soup.find(type='application/ld+json').text)
    title = soup.h1.text
    body = soup.find(id='story-primary').text
    tags = url.replace(ARTICLE_BASE_HREF, '').split('/')[:-3]
    try:
        article = Article(
            outlet=OUTLET,
            url=url,
            created=datetime.strptime(metadata['datePublished'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=datetime.strptime(metadata['dateModified'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            published=datetime.strptime(metadata['datePublished'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            title=title,
            body=body,
            wordCount=None,
            tags=tags,
            prefix=path,
            scrape_time=datetime.utcnow(),
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    return article
