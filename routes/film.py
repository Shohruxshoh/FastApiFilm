from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from models.category import Category
from models.country import Country
from models.film import Film
from models.genre import Genre
from models.user import User
from schemas.film import FilmSchema, FilmSchemaForAnother, FilmCreateSchema, FilmDetailSchema
from auth.dependencies import get_current_user, require_admin
from models.database import get_db
import os
from typing import List, Optional
import shutil
import os
from uuid import uuid4



router = APIRouter(tags=["Films"])


UPLOAD_DIR = "uploads/images"  # 📂 Rasm yuklanadigan joy

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)  # 🔥 Katalogni yaratamiz (agar mavjud bo‘lmasa)


@router.get("/", response_model=List[FilmSchemaForAnother])
async def get_films(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    year: Optional[int] = None,
    age_limit: Optional[int] = None,
    download_number: Optional[int] = None,
    category_id: Optional[int] = None,
    country_id: Optional[int] = None,
    genre_id: Optional[int] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
):
    stmt = (
        select(Film)
        .options(
            joinedload(Film.category), 
            joinedload(Film.country),
            joinedload(Film.genres)
        )
        .distinct()  # Takrorlangan natijalarni oldini olish
        .limit(limit)
        .offset(offset)
    )

    # 🔍 **Qidiruv (search)**
    if search:
        stmt = stmt.where(
            (Film.title.ilike(f"%{search}%")) |
            (Film.body.ilike(f"%{search}%")) |
            (Film.year == search) |
            (Film.age_limit == search)
        )

    # 🎯 **Filterlar**
    filters = {
        "year": year,
        "age_limit": age_limit,
        "download_number": download_number,
        "category_id": category_id,
        "country_id": country_id,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    for key, value in filters.items():
        if value is not None:
            stmt = stmt.where(getattr(Film, key) == value)

    if genre_id:
        stmt = stmt.join(Film.genres).where(Genre.id == genre_id)

    result = await db.execute(stmt)
    films = result.unique().scalars().all()  # ✅ `.unique()` bilan ishladik

    if not films:
        raise HTTPException(status_code=404, detail="No films found")

    return films


@router.post("/", response_model=FilmCreateSchema)  # JSON emas, oddiy dict qaytariladi
async def create_film(
    title: str = Form(...),
    body: Optional[str] = Form(None),
    image: UploadFile = File(None),  # 🖼 Rasm yuklash
    video_url: Optional[str] = Form(None),
    year: int = Form(None),
    age_limit: int = Form(None),
    download_number: int = Form(None),
    category_id: Optional[int] = Form(None),
    country_id: Optional[int] = Form(None),
    genre_ids: Optional[str] = Form(None),  
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    

     # 📌 **Janrlarni integer listga o‘tkazish**
    genre_list = []
    if genre_ids:
        try:
            genre_list = [int(g.strip()) for g in genre_ids.split(",")]  # 🎯 "2,3" → [2, 3]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid genre_ids format")

    # 📌 **Kategoriyani tekshirish**
    if category_id:
        category = await db.execute(select(Category).where(Category.id == category_id))
        if not category.scalars().first():
            raise HTTPException(status_code=400, detail="Category not found")

    # 📌 **Mamlakatni tekshirish**
    if country_id:
        country = await db.execute(select(Country).where(Country.id == country_id))
        if not country.scalars().first():
            raise HTTPException(status_code=400, detail="Country not found")

    # 📌 **Janrlarni tekshirish**
    genres = []
    if genre_list:
        genre_stmt = select(Genre).where(Genre.id.in_(genre_list))
        result = await db.execute(genre_stmt)
        genres = result.scalars().all()
        if len(genres) != len(genre_list):
            raise HTTPException(status_code=400, detail="One or more genres not found")

    # 📌 **Rasmni saqlash**
    file_ext = image.filename.split(".")[-1]  # 🔥 Foydalanuvchi yuklagan fayl kengaytmasi
    unique_filename = f"{uuid4().hex}.{file_ext}"  # 🆕 Yangi rasm nomi (UUID bilan)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)  # 📥 Faylni saqlaymiz

    # 📌 **Film yaratish**
    new_film = Film(
        title=title,
        body=body,
        image=file_path,  # 🖼 Faqat fayl manzilini saqlaymiz
        video_url=video_url,
        year=year,
        age_limit=age_limit,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        download_number=download_number,
        user_id=user.id,
        category_id=category_id,
        country_id=country_id,
        genres=genres,
    )

    db.add(new_film)
    await db.commit()
    await db.refresh(new_film)

    return new_film

# ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
# MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 📏 10MB limit

# @router.post("/", response_model=dict)
# async def create_film(
#     title: str = Form(...),
#     body: Optional[str] = Form(None),
#     image: UploadFile = File(...),
#     video_url: Optional[str] = Form(None),
#     year: int = Form(...),
#     age_limit: int = Form(...),
#     user_id: Optional[int] = Form(None),
#     category_id: Optional[int] = Form(None),
#     country_id: Optional[int] = Form(None),
#     genre_ids: Optional[List[int]] = Form(None),
#     db: AsyncSession = Depends(get_db)
# ):
#     # ✅ **Fayl turini tekshirish**
#     if image.content_type not in ALLOWED_IMAGE_TYPES:
#         raise HTTPException(
#             status_code=400,
#             detail="Only JPEG, PNG, and WEBP images are allowed"
#         )

#     # ✅ **Fayl hajmini tekshirish**
#     image.file.seek(0, os.SEEK_END)  # 📏 Fayl o‘lchamini olish
#     file_size = image.file.tell()
#     image.file.seek(0)  # 🔄 Faylni boshidan o‘qishga qaytarish

#     if file_size > MAX_IMAGE_SIZE:
#         raise HTTPException(
#             status_code=400,
#             detail="Image size must be less than 2MB"
#         )

#     # 📥 **Rasmni saqlash**
#     file_ext = image.filename.split(".")[-1]
#     unique_filename = f"{uuid4().hex}.{file_ext}"
#     file_path = os.path.join(UPLOAD_DIR, unique_filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)

#     # 📌 **Film yaratish**
#     new_film = Film(
#         title=title,
#         body=body,
#         image=file_path,  # 🖼 Rasm yo‘li saqlanadi
#         video_url=video_url,
#         year=year,
#         age_limit=age_limit,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow(),
#         download_number=0,
#         user_id=user_id,
#         category_id=category_id,
#         country_id=country_id,
#     )

#     db.add(new_film)
#     await db.commit()
#     await db.refresh(new_film)

#     return {
#         "message": "Film successfully created",
#         "film_id": new_film.id,
#         "image_url": f"http://127.0.0.1:9003/uploads/images/{unique_filename}"
#     }

@router.get("/{id}", response_model=FilmDetailSchema)
async def get_film(id:int,     db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Film).where(Film.id==id)
        .options(
            joinedload(Film.category), 
            joinedload(Film.country),
            joinedload(Film.genres)
        )
        .distinct()  # Takrorlangan natijalarni oldini olish
    )
    result = await db.execute(stmt)
    film = result.scalars().first()
    return film

@router.patch("/{film_id}", response_model=FilmSchemaForAnother)
async def update_film_partial(
    film_id: int,
    title: Optional[str] = Form(None),
    body: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    age_limit: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    country_id: Optional[int] = Form(None),
    genre_ids: Optional[str] = Form(None),  
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    film = (await db.execute(select(Film).where(Film.id == film_id).options(
            joinedload(Film.category), 
            joinedload(Film.country),
            joinedload(Film.genres)
        )
        .distinct())).scalars().first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")

    # 📌 **Janrlarni integer listga o‘tkazish**
    genre_list = []
    if genre_ids:
        try:
            genre_list = [int(g.strip()) for g in genre_ids.split(",")]  # 🎯 "2,3" → [2, 3]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid genre_ids format")
    if genre_list:
        genres = (await db.execute(select(Genre).where(Genre.id.in_(genre_list)))).scalars().all()
        if len(genres) != len(genre_list):
            raise HTTPException(status_code=400, detail="One or more genres not found")
        film.genres = genres  # 🎭 Janrlarni yangilash

    # 🖼 **Rasmni yangilash**
    if image:
        # Eski rasmni o‘chirish (agar mavjud bo‘lsa)
        if film.image and os.path.exists(film.image):
            os.remove(film.image)
        
        # Yangi rasmni saqlash
        file_ext = image.filename.split(".")[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid4().hex}.{file_ext}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        film.image = file_path  # 🖼 Faqat `file_path` bazaga yoziladi

    # # 🔥 **Foydalanuvchi faqat yuborgan maydonlarini yangilaymiz**
    # for field, value in locals().items():
    #     if value is not None and hasattr(film, field):
    #         setattr(film, field, value)

    # film.updated_at = datetime.utcnow()  # ⏳ Yangilangan vaqtni saqlash

    # 🔥 **Foydalanuvchi yuborgan maydonlarni yangilaymiz**
    fields_to_update = {
        "title": title,
        "body": body,
        "video_url": video_url,
        "year": year,
        "age_limit": age_limit,
        "user_id": user.id,
        "category_id": category_id,
        "country_id": country_id,
        "updated_at": datetime.utcnow()
    }

    for field, value in fields_to_update.items():
        if value is not None:
            setattr(film, field, value)
    await db.commit()
    await db.refresh(film)

    return film

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Film).where(Film.id == id)
    result = await db.execute(stmt)
    film = result.scalars().first()

    if film is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")

    await db.delete(film)
    await db.commit()
    return {"message": "Film deleted successfully"}