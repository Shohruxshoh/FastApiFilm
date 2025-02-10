from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.genre import Genre
from models.user import User
from schemas.genre import GenreCreate, GenreSchema, GenreDetailSchema
from auth.dependencies import get_current_user, require_admin
from fastapi import Depends

router = APIRouter(tags=["Genres"])

@router.get('/', response_model=list[GenreSchema])
async def get_countries(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Genre))
    genres = result.scalars().all()
    return genres

@router.post("/", response_model=GenreSchema)
async def create_genre(genre_data: GenreCreate, user: User = Depends(require_admin),  db: AsyncSession = Depends(get_db)):
    db_genre = Genre(**genre_data.dict())
    # Genre = Genre(name=genre_data.name)
    db.add(db_genre)
    await db.commit()
    await db.refresh(db_genre)
    return db_genre

@router.get("/{id}", response_model=GenreDetailSchema)
async def get_genre(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Genre).where(Genre.id == id).options(selectinload(Genre.films))
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if genre is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")

    return genre

@router.put("/{id}", response_model=GenreSchema)
async def update_genre(id: int, genre_data: GenreCreate, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Genre).where(Genre.id == id)
    result = await db.execute(stmt)
    genre = result.scalars().first()
    if genre is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    
    if genre_data.name:
        genre.name = genre_data.name
    await db.commit()
    return genre

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Genre).where(Genre.id == id)
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")

    await db.delete(genre)
    await db.commit()
    return {"message": "Genre deleted successfully"}