from pydantic import BaseModel
from typing import List, Optional


class FilmSchemaForAnother(BaseModel):
    id: int
    title: str
    image: bytes| None = None
    age_limit: int| None = None
    download_number: int| None = None

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str

class CategorySchema(BaseModel):
    id: int
    name: str


class CategoryDetailSchema(BaseModel):
    id: int
    name: str
    films: Optional[List[FilmSchemaForAnother]] | None = []  # Bo‘sh bo‘lishi mumkin

    class Config:
        from_attributes = True