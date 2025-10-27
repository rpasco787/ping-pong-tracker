from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, players, matches
from .db import create_db_and_tables

app = FastAPI(title="PingPong API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.API_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_db_and_tables()


app.include_router(health.router)
app.include_router(players.router)
app.include_router(matches.router)
