from datetime import datetime, timezone
from typing import Optional

from pydantic import Field, validator

from models import CustomBaseModel, PyObjectId
from v2.models.mixins import AuditMixin


class Article(CustomBaseModel, AuditMixin):
    domain: str = Field(description="The domain the article was extracted from")
    url: str = Field(description="The URL of the article")
    published_at: Optional[str] | Optional[datetime] = Field(
        default=None, description="The date the article was published"
    )
    title: str = Field(description="The title of the article")
    preview: Optional[str] = Field(
        default=None, description="The first text content of the article"
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Descriptive tags summarising the topics of the article",
    )
    author: Optional[list[str]] = Field(
        default=None, description="The author(s) of the article"
    )
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The time the article was last scraped",
    )


class DBArticle(Article):
    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database", alias="_id"
    )

    @validator("id", pre=True)
    def _set_id(cls, v):
        """potential ObjectId cast to string"""
        return str(v)
