from pydantic import Field

from models import CustomBaseModel, PyObjectId
from v2.models.mixins import AuditMixin


class Feed(CustomBaseModel, AuditMixin):
    name: str


class DBFeed(Feed):
    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database", alias="_id"
    )
    userId: PyObjectId = Field(
        description="Unique identifier of the user associated with the feed",
    )
