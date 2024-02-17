from pydantic import Field

from models import CustomBaseModel, PyObjectId
from v2.models.helpers import partial_model
from v2.models.mixins import AuditMixin


class Trace(CustomBaseModel, AuditMixin):
    traces: list[list[str]] = Field(default=[])
    is_finalised: bool = Field(default=False)
    sourceId: PyObjectId = Field(
        description="Unique identifier of the feed associated with the outlet",
    )
    type: str = Field(
        description="The type of trace, e.g. article_links, article_info, etc.",
    )


@partial_model
class UpdateTrace(Trace):
    pass


class DBTrace(Trace):
    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database", alias="_id"
    )
