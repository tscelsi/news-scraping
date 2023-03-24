import logging
import json
from datetime import datetime
from pydantic import ValidationError
from bs4 import BeautifulSoup
import httpx

from consts import HEADERS
from models import Article
from utils import normalise_tags

logger = logging.getLogger(__name__)

OUTLET = 'nytimes'
ARTICLE_BASE_HREF = 'https://www.nytimes.com/'


async def list_articles(client: httpx.AsyncClient, path: str) -> list[str]:
    res = await client.get(ARTICLE_BASE_HREF + path.lstrip('/'), headers=HEADERS, follow_redirects=True)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(
            f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    featured_section = soup.find('section', {'id': 'collection-highlights-container'})
    list_section = soup.find('section', {'id': 'stream-panel'})
    list_section_urls = set([x['href'] for x in list_section.findAll('a') if x['href'].endswith('.html')])
    featured_urls = set([x['href'] for x in featured_section.findAll('a') if x['href'].endswith('.html')])
    article_urls = list(list_section_urls.union(featured_urls))
    return article_urls


async def get_article(client: httpx.AsyncClient, url: str, path: str) -> Article:
    full_url = ARTICLE_BASE_HREF + url.lstrip('/')
    response = await client.get(full_url, headers=HEADERS)
    if response.status_code != 200:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    metadata = json.loads(soup.find(type='application/ld+json').text)
    article = soup.find('article', {'id': 'story'})
    if not article:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{metadata}')
        return None
    elif 'inLanguage' in metadata and metadata['inLanguage'] != 'en':
        logger.error(f'get_article;article {url} not in english;{metadata}')
        return None
    title = article.h1.text
    content_section = article.find('section', {'name': 'articleBody'})
    body = ' '.join([x.text for x in content_section.findAll('p', {'class': 'css-at9mc1 evys1bk0'})])
    author = [x['name'] for x in metadata['author']] if isinstance(metadata['author'], list) else metadata['author']['name']
    published = metadata['datePublished']
    modified = metadata['dateModified']
    try:
        article = Article(
            outlet=OUTLET,
            url=full_url,
            created=datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=datetime.strptime(modified, '%Y-%m-%dT%H:%M:%S.%fZ'),
            published=datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%fZ'),
            title=title,
            body=body,
            author=author,
            tags=[],
            prefix=path,
            scrape_time=datetime.utcnow(),
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    return article
