from datetime import datetime
from pydantic import BaseModel


class MediumArticleCreator(BaseModel):
    name: str


class MediumArticleParagraph(BaseModel):
    type: str
    text: str


class MediumArticleBodyModel(BaseModel):
    paragraphs: list[MediumArticleParagraph]


class MediumArticleExtendedPreviewContent(BaseModel):
    bodyModel: MediumArticleBodyModel


class MediumArticleTag(BaseModel):
    normalizedTagSlug: str

class MediumArticlePost(BaseModel):
    creator: MediumArticleCreator
    extendedPreviewContent: MediumArticleExtendedPreviewContent
    firstPublishedAt: datetime
    latestPublishedAt: datetime
    title: str
    mediumUrl: str
    tags: list[MediumArticleTag]


class MediumArticle(BaseModel):
    post: MediumArticlePost
