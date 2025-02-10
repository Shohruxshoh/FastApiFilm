from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from models.user import User, RoleEnum
from .auth import decode_token
from jose import JWTError, jwt
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_current_user(token: str = Depends(reuseable_oauth), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token=token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user