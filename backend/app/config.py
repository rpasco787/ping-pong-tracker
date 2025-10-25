from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_CORS_ORIGINS: str = "http://localhost:3000"  # Next.js dev port

settings = Settings()