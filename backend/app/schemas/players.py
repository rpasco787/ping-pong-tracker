from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class PlayerIn(BaseModel):
    name: str = Field(min_length=1)
    email: Optional[EmailStr] = None


class PlayerOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    wins: int
    losses: int
    points: int
