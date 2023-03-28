import logging
from datetime import datetime
from pydantic import ValidationError
import json
from bs4 import BeautifulSoup
import httpx

from consts import HEADERS
from models import Article
from utils import normalise_tags
from exceptions import BaseException

logger = logging.getLogger(__name__)

OUTLET = 'bbc'
ARTICLE_BASE_HREF = 'https://www.bbc.com/'


async def list_articles(path: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        res = await client.get(ARTICLE_BASE_HREF + path.lstrip('/'), headers=HEADERS)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    article_urls = []
    for article_block in soup.ol.findAll('h3'):
        atag = article_block.find('a')
        if atag:
            article_urls.append(atag['href'])
    # featured contents
    featured_section = soup.find('div', {'aria-label': 'Featured Contents'}).findAll('a', {'class': 'gs-c-promo-heading'})
    article_urls.extend([a['href'] for a in featured_section])
    article_urls = [x for x in filter(lambda x: x.startswith('/news'), article_urls)]
    return article_urls


async def get_article(url: str, path: str) -> Article:
    full_url = ARTICLE_BASE_HREF + url
    async with httpx.AsyncClient() as client:
        response = await client.get(full_url, headers=HEADERS, follow_redirects=True)
    if response.status_code != 200:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    metadata_html = soup.find(type='application/ld+json')
    if not metadata_html:
        logger.error(f'get_article;no metadata in article;{url}')
        return None
    metadata = json.loads(metadata_html.text)
    created_string = metadata['datePublished'] if 'datePublished' in metadata.keys() else metadata['uploadDate']
    modified_string = metadata['dateModified'] if 'dateModified' in metadata.keys() else metadata['uploadDate']
    created = datetime.strptime(created_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    modified = datetime.strptime(modified_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    published = datetime.strptime(created_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    title = soup.h1.text
    body = ' '.join([x.text for x in soup.article.findAll('div', {'data-component': 'text-block'})])
    tag_div = soup.article.find('div', {'data-component': 'topic-list'})
    tags = normalise_tags(*[x.text for x in tag_div.findAll('li')]) if tag_div else []
    try:
        article = Article(
            outlet=OUTLET,
            author=[],
            url=full_url,
            created=created,
            modified=modified,
            published=published,
            title=title,
            body=body,
            tags=tags,
            prefix=path,
            scrape_time=datetime.utcnow(),
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    return article
