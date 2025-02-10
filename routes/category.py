from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.category import Category
from models.user import User
from schemas.category import CategoryCreate, CategorySchema, CategoryDetailSchema
from auth.dependencies import get_current_user, require_admin
from fastapi import Depends

router = APIRouter(tags=["Categories"])

@router.get('/', response_model=list[CategorySchema])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Barcha kategoriyalarni olish (Adminlar uchun)"""
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return categories

@router.post("/", response_model=CategorySchema)
async def create_category(category_data: CategoryCreate, user: User = Depends(require_admin),  db: AsyncSession = Depends(get_db)):
    db_category = Category(**category_data.dict())
    # category = Category(name=category_data.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.get("/{id}", response_model=CategoryDetailSchema)
async def get_category(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.id == id).options(selectinload(Category.films))
    result = await db.execute(stmt)
    category = result.scalars().first()


    if category is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category

@router.put("/{id}", response_model=CategorySchema)
async def update_category(id: int, category_data: CategoryCreate, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.id == id)
    result = await db.execute(stmt)
    category = result.scalars().first()
    if category is None:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    if category_data.name:
        category.name = category_data.name
    await db.commit()
    return category

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.id == id)
    result = await db.execute(stmt)
    category = result.scalars().first()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted successfully"}