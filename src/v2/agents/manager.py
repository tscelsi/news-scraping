"""A manager that orchestrates agents"""

from bson import ObjectId
from bson.errors import InvalidId

from api.lib.db import Db
from api.lib.exceptions import ObjectNotFoundError
from api.v2.trace.repository import TraceRepository
from models import PyObjectId
from v2.models.trace import Trace

from .article_info_agent import ArticleInfoAgent
from .article_links_agent import ArticleLinksAgent


class AgentManager:
    def __init__(self):
        self.article_links_agent = ArticleLinksAgent()
        self.article_info_agent = ArticleInfoAgent()
        self._db = Db()

    async def maybe_create_article_link_traces(
        self, url: str, source_id: PyObjectId | str
    ) -> list[list[str]]:
        """Creates article link traces for the specified url if they don't exist and
        are finalised."""
        trace_obj = None
        try:
            source_id = ObjectId(source_id)
            trace_obj = TraceRepository.read_by(
                {"sourceId": ObjectId(source_id), "type": "article_links"}
            )
        except ObjectNotFoundError:
            pass
        except InvalidId:
            pass
        if trace_obj and trace_obj.is_finalised:
            return trace_obj.traces
        traces, _ = await self.article_links_agent.run(url)
        if trace_obj:
            # not finalised, so we want to update
            TraceRepository.update(
                trace_obj.id, {"traces": traces, "is_finalised": False}
            )
            return traces
        # create new
        TraceRepository.create(
            Trace(
                traces=traces,
                is_finalised=False,
                sourceId=source_id,
                type="article_links",
            )
        )
        return traces

    async def maybe_create_article_info_traces(
        self, url: str, source_id: PyObjectId | str
    ) -> list[list[str]]:
        trace_obj = None
        try:
            source_id = ObjectId(source_id)
            trace_obj = TraceRepository.read_by(
                {"sourceId": ObjectId(source_id), "type": "article_title"}
            )
        except ObjectNotFoundError:
            pass
        except InvalidId:
            pass
        if trace_obj and trace_obj.is_finalised:
            return trace_obj.traces
        trace = await self.article_info_agent.run(url)
        traces = [trace]
        if trace_obj:
            # not finalised, so we want to update
            TraceRepository.update(
                trace_obj.id, {"traces": traces, "is_finalised": False}
            )
            return traces
        # create new
        TraceRepository.create(
            Trace(
                traces=traces,
                is_finalised=False,
                sourceId=source_id,
                type="article_title",
            )
        )
        return traces
