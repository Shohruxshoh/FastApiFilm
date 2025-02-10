from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from schemas.category import CategorySchema
from schemas.country import CountrySchema
from schemas.genre import GenreSchema

class FilmSchemaForAnother(BaseModel):
    id: int
    title: str
    image: bytes| None = None
    age_limit: int| None = None
    download_number: int| None = None

    class Config:
        from_attributes = True

class FilmSchema(BaseModel):
    id: int | None = None


class FilmCreateSchema(BaseModel):
    id: int | None = None
    title: str
    body: Optional[str] = None
    image: Optional[str] = None
    video_url: Optional[str] = None
    year: int
    age_limit: int
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    country_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None  # 🎭 Ko‘p janrlar tanlash

    class Config:
        from_attributes = True

class FilmDetailSchema(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    image: Optional[str] = None
    video_url: Optional[str] = None
    year: int | None =None
    age_limit: int | None =None
    category: CategorySchema | None = None
    country: CountrySchema | None = None
    genres: List[GenreSchema] | None = None  # 🎭 Ko‘p janrlar tanlash

    class Config:
        from_attributes = True