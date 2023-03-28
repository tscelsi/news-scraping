from bson import ObjectId
from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime


class DBSource(CustomBaseModel):
    class Config:
        json_encoders = {ObjectId: str}

    id: PyObjectId = Field(
        description="Unique identifier of a news source",
        alias="_id"
    )
    ref: str = Field(
        description="A unique reference for the news source",
    )
    name: str = Field(
        description="The human-readable name of the news source",
    )
    created_at: datetime = Field(
        description="The time the news source was created",
    )
    modified_at: datetime = Field(
        description="The most recent time the news source was modified",
    )
    base_url: str = Field(
        description="The base URL of the news source, e.g. https://www.nytimes.com",
    )
