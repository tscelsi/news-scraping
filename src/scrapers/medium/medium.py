import re
from datetime import datetime
import logging
import httpx
from pydantic import ValidationError
from models import Article
from scrapers.core import CoreScraper, URL, ScraperError
from models import MediumArticle
from .query import query

logger = logging.getLogger(__name__)


class Scraper(CoreScraper):
    SOURCE = 'medium'
    BASE_HREF = 'https://medium.com/'

    async def list_articles(self, prefix: str) -> list[URL] | None:
        """ Returns none, because we can populate the self.articles list from this function. No need to 
        return list of article urls."""
        async with httpx.AsyncClient() as client:
            tag_slug = re.search(r'^/?(tag/(\w+))', prefix)
            if not tag_slug:
                raise ScraperError(f'Invalid tag slug: {prefix}')
            # mode NEW to get latest articles
            res = await client.post(self.BASE_HREF + "_/graphql", json=[{"operationName": "TopicFeedQuery", "variables": {"tagSlug": tag_slug.group(2), "mode": "NEW", "paging": {"to": "0", "limit": 25}}, "query": query}])
            res.raise_for_status()
            data = res.json()
            articles = data[0]['data']['tagFeed']['items']
            medium_articles = [self._extract_article(
                article, tag_slug.group(1)) for article in articles]
            self.articles = [x for x in medium_articles if x]

    def _extract_article(self, article: dict, prefix: str) -> Article:
        try:
            medium_article = MediumArticle(**article)
            article = Article(
                outlet=self.SOURCE,
                url=medium_article.post.mediumUrl,
                author=[medium_article.post.creator.name],
                created=medium_article.post.firstPublishedAt,
                modified=medium_article.post.latestPublishedAt,
                published=medium_article.post.firstPublishedAt,
                title=medium_article.post.title,
                body=" ".join([x.text for x in medium_article.post.extendedPreviewContent.bodyModel.paragraphs if x.type.lower() == 'p']),
                tags=[x.normalizedTagSlug for x in medium_article.post.tags],
                prefix=prefix,
                scrape_time=datetime.utcnow(),
            )
        except ValidationError as e:
            logger.error(f'medium;failed to validate {article};{e}')
            return None
        return article
