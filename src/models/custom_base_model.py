from bson import ObjectId
from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    class Config:
        json_encoders = {ObjectId: str}
