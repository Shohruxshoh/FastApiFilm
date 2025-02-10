from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.country import Country
from models.user import User
from schemas.country import CountryCreate, CountrySchema, CountryDetailSchema
from auth.dependencies import get_current_user, require_admin
from fastapi import Depends

router = APIRouter(tags=["Countries"])

@router.get('/', response_model=list[CountrySchema])
async def get_countries(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Country))
    countries = result.scalars().all()
    return countries

@router.post("/", response_model=CountrySchema)
async def create_Country(country_data: CountryCreate, user: User = Depends(require_admin),  db: AsyncSession = Depends(get_db)):
    db_country = Country(**country_data.dict())
    # Country = Country(name=country_data.name)
    db.add(db_country)
    await db.commit()
    await db.refresh(db_country)
    return db_country

@router.get("/{id}", response_model=CountryDetailSchema)
async def get_country(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Country).where(Country.id == id).options(selectinload(Country.films))
    result = await db.execute(stmt)
    country = result.scalars().first()

    if country is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    return country

@router.put("/{id}", response_model=CountrySchema)
async def update_country(id: int, country_data: CountryCreate, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Country).where(Country.id == id)
    result = await db.execute(stmt)
    country = result.scalars().first()
    if country is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    
    if country_data.name:
        country.name = country_data.name
    await db.commit()
    return country

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Country).where(Country.id == id)
    result = await db.execute(stmt)
    country = result.scalars().first()

    if country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    await db.delete(country)
    await db.commit()
    return {"message": "Country deleted successfully"}