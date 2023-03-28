import logging
import itertools
from datetime import datetime
from pydantic import ValidationError
from bs4 import BeautifulSoup
import httpx

from consts import HEADERS
from models import Article
from .model import AlJazeeraArticle

logger = logging.getLogger(__name__)

OUTLET = 'aljazeera'
ARTICLE_BASE_HREF = 'https://www.aljazeera.com/'


async def list_articles(path: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        res = await client.get(ARTICLE_BASE_HREF + path.lstrip('/'), headers=HEADERS, follow_redirects=True)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(
            f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.findAll('article')
    article_urls = [x.find('h3').a['href'].split('/')[-1] for x in articles]
    return article_urls


async def get_article(url: str, path: str) -> Article:
    query = 'graphql?wp-site=aje&operationName=ArchipelagoSingleArticleQuery&variables={"name":"%s","postType":"post","preview":""}' % url
    async with httpx.AsyncClient() as client:
        response = await client.get(ARTICLE_BASE_HREF + query, headers={**HEADERS, 'wp-site': 'aje'})
    data = response.json()['data']
    if 'errors' in data or data['article'] is None:
        logger.error(
            f'get_article;failed to get {url} with status code {response.status_code};{response.text}')
        return None
    try:
        article = AlJazeeraArticle(**data['article'])
        soup = BeautifulSoup(article.content, 'html.parser')
        article.content = soup.text
    except ValidationError as e:
        logger.error(f'get_article;failed to validate {url};{e}')
        return None
    tags = [x.slug for x in itertools.chain(*[article.tags, article.where, article.categories])]
    standardised_article = Article(
        outlet=OUTLET,
        url=ARTICLE_BASE_HREF + url.lstrip('/'),
        author=[],
        created=datetime.fromisoformat(article.date),
        modified=datetime.fromisoformat(article.modified_gmt),
        published=datetime.fromisoformat(article.date),
        title=article.title,
        body=article.content,
        tags=tags,
        prefix=path,
        scrape_time=datetime.utcnow(),
    )
    return standardised_article
