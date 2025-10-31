from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, players, matches, auth, archives
from .scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    # Startup: Start the scheduler
    start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    shutdown_scheduler()


app = FastAPI(title="PingPong API", lifespan=lifespan)

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
app.include_router(auth.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(archives.router)
