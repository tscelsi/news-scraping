import logging
import json
from datetime import datetime
import traceback

import httpx
from pydantic import ValidationError
from bs4 import BeautifulSoup

from models import Article, NineEntArticle
from consts import HEADERS
from exceptions import BaseException
from utils import normalise_tags


logger = logging.getLogger(__name__)

OUTLET = 'theage'
ARTICLE_BASE_HREF = 'https://www.theage.com.au/'


async def list_articles(path: str | list[str]) -> list[str]:
    """Because the pagination relies on synchronous requests, we simply add the delay between
    using our Requestor context.
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(ARTICLE_BASE_HREF + path.lstrip('/'), headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_div = soup.find('div', {'class': '_1-N-m'})
    article_urls = [x.a['href'] for x in content_div.findAll('h3')]
    return article_urls


async def get_article(url: str, path: str) -> Article:
    full_url = ARTICLE_BASE_HREF + url.lstrip('/')
    async with httpx.AsyncClient() as client:
        response = await client.get(full_url, headers=HEADERS)
    if response.status_code != 200:
        logger.error(f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        metadata = json.loads(soup.find(type='application/ld+json').text)
        title = soup.h1.text
        author = [x['name'] for x in metadata['author']] if isinstance(metadata['author'], list) else [metadata['author']['name']]
        published = metadata['datePublished']
        created = metadata['datePublished']
        modified = metadata['dateModified']
        tags = normalise_tags(*[x.text for x in soup.article.header.ul.findAll('li')])
        top_section = soup.find('section', {'data-testid': 'article-body-top'}).findAll('p')
        bottom_section = soup.find('section', {'data-testid': 'article-body-bottom'}).findAll('p')
        top_section_contents = [x.text for x in top_section]
        bottom_section_contents = [x.text for x in bottom_section]
        article = Article(
            outlet=OUTLET,
            url=full_url,
            created=created,
            modified=modified,
            published=published,
            author=author,
            title=title,
            body=' '.join(top_section_contents + bottom_section_contents),
            wordCount=None,
            tags=tags,
            prefix=path,
            scrape_time=datetime.utcnow(),
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    except Exception as e:
        logger.error(traceback.print_tb(e.__traceback__))
        logger.error(f'get_article;Error with the extraction of article contents for {url}')
        return None
    return article
