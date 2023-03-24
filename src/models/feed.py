from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime


class Feed(CustomBaseModel):
    name: str
    created_at: datetime
    modified_at: datetime


class DBFeed(Feed):
    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )
    userId: PyObjectId = Field(
        description="Unique identifier of the user associated with the feed",
    )
