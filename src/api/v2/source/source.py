import logging

from fastapi import APIRouter

from api.lib.db import Db
from models import CustomBaseModel
from v2.tracer import create_url_traces

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/source", tags=["source"])
db = Db()


def create_url(source: str, endpoint: str):
    return "/".join([source, endpoint.strip("/")])


class CheckResponse(CustomBaseModel):
    success: bool
    titles: list[str]


class CheckRequestBody(CustomBaseModel):
    name: str
    url: str


@router.post(
    "/check",
    description="Checks if a source url is scrapeable",
    response_model=CheckResponse,
)
async def check_source(body: CheckRequestBody) -> CheckResponse:
    try:
        article_info_models = await create_url_traces(body.name, body.url)
    except Exception as e:
        logger.exception(e)
        return CheckResponse(success=False, titles=[])
    return CheckResponse(success=True, titles=[x.title for x in article_info_models])
