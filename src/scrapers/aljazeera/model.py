from pydantic import BaseModel

class AlJazeeraTag(BaseModel):
    title: str
    slug: str

class AlJazeeraArticle(BaseModel):
    content: str
    title: str
    date: str
    link: str
    modified_gmt: str
    tags: list[AlJazeeraTag]
    where: list[AlJazeeraTag]
    categories: list[AlJazeeraTag]