from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = False

class User(UserBase):
    id: int
    player_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserIn(UserBase):
    hashed_password: str
    id: Optional[int] = None
    player_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None