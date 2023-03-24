from bson import ObjectId
from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime


class FeedOutlet(CustomBaseModel):
    prefix: str = Field(description="The prefix to use when searching for articles")
    outlet: str = Field(description="The module/outlet name i.e. the outlet which to collect articles for", alias='outletRef')
    created_at: datetime
    modified_at: datetime


class DBFeedOutlet(FeedOutlet):
    class Config:
        json_encoders = { ObjectId: str }

    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )
    feedId: PyObjectId = Field(
        description="Unique identifier of the feed associated with the outlet",
    )
    outletId: PyObjectId = Field(
        description="Unique identifier of the outlet associated with the prefix and feed",
    )
