from pydantic import BaseModel, Field


class NineEntArticleHeadlines(BaseModel):
    headline: str = Field(__mapping="title")


class NineEntArticleAsset(BaseModel):
    about: str
    body: str
    headlines: NineEntArticleHeadlines
    wordCount: int


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


class NineEntArticle(BaseModel):
    assetType: str = Field()
    asset: NineEntArticleAsset
    categories: list[str]
    dates: NineEntArticleDates
    id: str
    publicState: str # published or not
    sources: list[NineEntArticleSource]
    tags: dict
    url: str = Field(__mapping="url") # uuid
