from pydantic import Field

from models import CustomBaseModel, PyObjectId
from v2.models.mixins import AuditMixin


class FeedSource(CustomBaseModel, AuditMixin):
    name: str = Field(description="The name associated with the source")


class DBFeedSource(FeedSource):
    id: PyObjectId = Field(
        description="Unique identifier of this feed source in the database", alias="_id"
    )
    feedId: PyObjectId = Field(
        description="Unique identifier of the feed associated with the source",
    )
    sourceId: PyObjectId = Field(
        description="Unique identifier of the source associated with an instance of FeedSource",
    )
