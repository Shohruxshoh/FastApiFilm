from pydantic import BaseModel
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class UserCreate(BaseModel):
    username: str
    phone: str
    password: str
    role: RoleEnum = RoleEnum.user  # Default user

class UserLogin(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    id: int
    username: str
    phone: str
    role: RoleEnum = RoleEnum.user  # Default user

class UserUpdate(BaseModel):
    phone: str
    role: RoleEnum = RoleEnum.user  # Default user

class Token(BaseModel):
    access_token: str
    token_type: str
