from typing import Optional
from bson import ObjectId
from enum import Enum
from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime


class ScrapingJobStatus(str, Enum):
    running = 'running'
    finished = 'finished'
    error = 'error'


class UpdateScrapingJob(CustomBaseModel):
    class Config:
        json_encoders = { ObjectId: str }

    status: ScrapingJobStatus = Field(description=f"The status of the scraping job, one of: {', '.join([s.value for s in ScrapingJobStatus])}")
    modified_at: Optional[datetime] = Field(description="The last time the scraping job was modified", default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(description="The time the scraping job was completed")    


class ScrapingJob(UpdateScrapingJob):
    created_at: datetime = Field(description="The time the scraping job was created")


class DBScrapingJob(ScrapingJob):
    id: PyObjectId = Field(
        description="Unique identifier of this scraping job in the database",
        alias="_id"
    )
    userId: PyObjectId = Field(
        description="Unique identifier of the user associated with the scraping job",
    )
