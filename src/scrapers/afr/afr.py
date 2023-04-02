import logging
from datetime import datetime

import httpx
from pydantic import ValidationError

from models import Article, NineEntArticle
from consts import HEADERS
from exceptions import BaseException
from utils import normalise_tags
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

OUTLET = 'afr'
ARTICLE_BASE_HREF = 'https://www.afr.com/'


async def list_articles(path: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        res = await client.get(ARTICLE_BASE_HREF + path, headers=HEADERS)
    if res.status_code != 200:
        logger.error(f'list_articles;{res.status_code};{res.text}')
        raise BaseException(f'Failed to get {path} with status code {res.status_code}')
    soup = BeautifulSoup(res.text, 'html.parser')
    article_ids = [x.a['href'].split("-")[-1] for x in soup.main.findAll('h3')]
    return article_ids


async def get_article(url: str, path: str) -> Article:
    """In this case, the url is actually an article id which we pass to the API."""
    api_url = "https://api.afr.com/api/content/v0/assets/" + url
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=HEADERS)
    try:
        article = NineEntArticle(**response.json(), url=url)
        if article.assetType != 'article':
            logger.warning(f'get_article;{url} is not an article;{article.assetType}')
            return None
        tags = []
        for el in article.tags.values():
            if isinstance(el, list):
                tags.extend(el)
                continue
            tags.append(el)
        tags = [tag['displayName'] for tag in tags]
        tags.extend(article.categories)
        normalised_tags = normalise_tags(*tags)
        standardised_article = Article(
            outlet=OUTLET,
            url=url,
            created=datetime.strptime(article.dates.created, '%Y-%m-%dT%H:%M:%SZ'),
            modified=datetime.strptime(article.dates.modified, '%Y-%m-%dT%H:%M:%SZ'),
            published=datetime.strptime(article.dates.published, '%Y-%m-%dT%H:%M:%SZ'),
            title=article.asset.headlines.headline,
            body=article.asset.body,
            wordCount=article.asset.wordCount,
            tags=normalised_tags,
            prefix=path,
            scrape_time=datetime.utcnow(),
            author=[x.name for x in article.participants.authors] if article.participants != {} else [],
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    return standardised_article
