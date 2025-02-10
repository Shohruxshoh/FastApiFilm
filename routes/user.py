from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db, Base
from sqlalchemy.future import select
from models.user import User
from schemas.user import UserCreate, UserLogin, Token, UserSchema, UserUpdate
from auth.auth import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_user, require_admin
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserSchema)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_password, phone=user_data.phone, role=user_data.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/admin/", dependencies=[Depends(require_admin)])
async def admin_only():
    return {"message": "Welcome, admin!"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=UserSchema)
async def update_user(
    user_data: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Login bo'lgan user o'z profilini yangilaydi"""
    try:
        stmt = select(User).where(User.id == current_user.id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_data.phone:
            user.phone = user_data.phone
        if user_data.role:
            user.role = user_data.role
        await db.commit()
        return user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
