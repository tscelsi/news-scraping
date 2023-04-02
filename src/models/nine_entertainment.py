from pydantic import BaseModel, Field
from typing import Union, Optional


class NineEntArticleHeadlines(BaseModel):
    headline: str = Field(__mapping="title")


class NineEntArticleAsset(BaseModel):
    about: str
    body: str
    headlines: NineEntArticleHeadlines
    wordCount: Optional[int]


class NineEntArticleDates(BaseModel):
    created: str
    firstPublished: str
    imported: str
    modified: str
    published: str
    saved: str


class NineEntArticleSource(BaseModel):
    id: str
    name: str


class NineEntAuthor(BaseModel):
    name: str


class NineEntParticipants(BaseModel):
    authors: list[NineEntAuthor]


class NineEntArticle(BaseModel):
    assetType: str = Field()
    asset: NineEntArticleAsset
    participants: Union[NineEntParticipants, dict]
    categories: list[str]
    dates: NineEntArticleDates
    id: str
    publicState: str # published or not
    sources: list[NineEntArticleSource]
    tags: dict
    url: str = Field(__mapping="url") # uuid
