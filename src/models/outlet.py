from models import CustomBaseModel, PyObjectId
from pydantic import Field
from datetime import datetime

# the config needed for the scraper to run
class OutletConfig(CustomBaseModel):
    module: str = Field(description="The module name i.e. the outlet which to collect articles for", alias='outlet')
    path: str = Field(description="The path/prefix to scrape", alias="prefix")
    max_at_once: int = Field(default=4)
    max_per_second: int = Field(default=4)
    db_uri: str | None = Field(default=None)
    db_must_connect: bool = Field(default=True, const=True)
    debug: bool = Field(default=True, const=True)


class Outlet(CustomBaseModel):
    name: str
    ref: str
    created_at: datetime
    modified_at: datetime

class DBOutlet(Outlet):
    id: PyObjectId = Field(
        description="Unique identifier of this strategy in the database",
        alias="_id"
    )
