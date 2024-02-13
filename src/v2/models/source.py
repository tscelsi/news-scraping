from bson import ObjectId
from pydantic import Field

from models import CustomBaseModel, PyObjectId
from v2.models.mixins import AuditMixin


class Source(CustomBaseModel, AuditMixin):
    class Config:
        json_encoders = {ObjectId: str}

    name: str = Field(
        description="The human-readable name of the news source",
    )
    url: str = Field(
        description="A url - a unique reference for the news source",
    )


class DBSource(Source):
    id: PyObjectId = Field(
        description="Unique identifier of a news source", alias="_id"
    )
