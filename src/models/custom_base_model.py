from bson import ObjectId
from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
