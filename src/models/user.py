from typing import Optional
from bson import ObjectId
from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime

# model User {
#     id                 String        @id @default(auto()) @map("_id") @db.ObjectId
#     name               String?
#     email              String?       @unique
#     emailVerified      DateTime?
#     image              String?
#     daily_scrape_count Int?          @default(0)
#     accounts           Account[]
#     sessions           Session[]
#     feed               Feed?
#     scrapingJobs       ScrapingJob[]
# }


class UpdateUser(CustomBaseModel):
    daily_scrape_count: Optional[int] = Field(
        description="The number of times the user has scraped today")


class DBUser(UpdateUser):
    class Config:
        json_encoders = {ObjectId: str}

    id: PyObjectId = Field(
        description="Unique identifier of a user in the database",
        alias="_id"
    )
    name: Optional[str]
    email: Optional[str]
    emailVerified: Optional[datetime]
    image: Optional[str]
