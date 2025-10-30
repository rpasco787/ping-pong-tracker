from pydantic import BaseModel, EmailStr


class PlayerOut(BaseModel):
    """Public player information."""
    id: int
    name: str
    email: EmailStr
    wins: int
    losses: int
    points: int
