from api.v2.source import SourceRepository
from v2.agents.manager import AgentManager
from v2.models.article import Article
from v2.models.source import Source
from v2.scraper import Scraper


async def create_url_traces(name: str, url: str) -> list[Article]:
    """Checks that the URL is scrapeable"""
    agent_manager = AgentManager()
    # finds article links and sets traces if applicable
    url = url.rstrip("/")
    # get or create source
    source = SourceRepository.read_or_create(Source(name=name, url=url))
    scraper = Scraper(sourceId=source.id)
    await agent_manager.maybe_create_article_link_traces(url, source.id)
    article_links = await scraper.get_article_links(url)
    # finds article info and sets traces if applicable
    await agent_manager.maybe_create_article_info_traces(article_links[0], source.id)
    article_info_models = await scraper.run(url)
    return article_info_models
