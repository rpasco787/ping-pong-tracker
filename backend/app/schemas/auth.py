from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class LoginRequest(BaseModel):
    """Request schema for user login."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class TokenResponse(BaseModel):
    """Response schema for authentication token."""
    access_token: str
    token_type: str = "bearer"
    player: dict  # Contains player info (id, name, email, wins, losses, points)

