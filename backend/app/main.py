from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, players, matches

app = FastAPI(title="PingPong API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.API_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Database migrations are now handled by Alembic
# Run: alembic upgrade head

app.include_router(health.router)
app.include_router(players.router)
app.include_router(matches.router)