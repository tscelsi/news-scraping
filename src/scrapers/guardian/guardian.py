import logging
from datetime import datetime
from pydantic import ValidationError
import json
from bs4 import BeautifulSoup
import httpx

from consts import HEADERS
from models import Article
from utils import normalise_tags

logger = logging.getLogger(__name__)

OUTLET = 'guardian'
ARTICLE_BASE_HREF = 'https://www.theguardian.com/'


## yes i know the guardian has an API, idc ##

async def list_articles(client: httpx.AsyncClient, path: str) -> list[str]:
    res = await client.get(ARTICLE_BASE_HREF + path, headers=HEADERS)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    article_urls = [x.a['href'] for x in soup.findAll('div', {'class': 'fc-item'})]
    return article_urls


async def get_article(client: httpx.AsyncClient, url: str, path: str) -> Article:
    response = await client.get(url, headers=HEADERS)
    if response.status_code != 200:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    print(url)
    metadata = json.loads(soup.find(type='application/ld+json').text)
    if isinstance(metadata, list):
        metadata = metadata[0]
    title = soup.h1.text
    body = soup.find('div', {'id': 'maincontent'}).text
    tag_div = soup.find('div', {'class': 'dcr-1nx1rmt'})
    if tag_div is None or body is None or body == '':
        logger.error(f'get_article;failed to get article body or tags;{url};{body};{tag_div}')
        return None
    tags = normalise_tags(*[x.text for x in tag_div.findAll('li')])
    try:
        article = Article(
            outlet=OUTLET,
            author=[],
            url=url,
            created=datetime.strptime(metadata['datePublished'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=datetime.strptime(metadata['dateModified'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            published=datetime.strptime(metadata['datePublished'], '%Y-%m-%dT%H:%M:%S.%fZ'),
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
