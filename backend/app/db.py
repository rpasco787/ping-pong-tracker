from sqlmodel import SQLModel, Session, create_engine, Field
from typing import Generator, Optional
from typing import List
import os

# SQLite database URL for development
# Override with environment variable DATABASE_URL for production (e.g., PostgreSQL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ping_pong.db"
)

# Create engine
# connect_args is only needed for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
    connect_args=connect_args
)


# Database Models
class Player(SQLModel, table=True):
    """Player table - tracks player information and stats."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: Optional[str] = Field(default=None, unique=True)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    points: int = Field(default=0)


class Match(SQLModel, table=True):
    """Match table - tracks individual matches between players."""
    id: Optional[int] = Field(default=None, primary_key=True)
    played_at: str = Field(index=True)
    home_id: int = Field(foreign_key="player.id")
    away_id: int = Field(foreign_key="player.id")


class GameScore(SQLModel, table=True):
    """GameScore table - tracks individual game scores within a match."""
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id")
    home: int = Field(ge=0)
    away: int = Field(ge=0)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id")



def create_db_and_tables() -> None:
    """
    Create all tables in the database.
    Call this on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get a database session.
    Use this with FastAPI's Depends() to inject sessions into route handlers.
    
    Example:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


# Constants
WIN_POINTS = 3  # scoring rule: 3 points per match win


def compute_winner(games: List["GameScore"]) -> str:
    """Return 'home' or 'away' based on who won more games."""
    home_wins = sum(1 for g in games if g.home > g.away)
    away_wins = len(games) - home_wins
    return "home" if home_wins > away_wins else "away"

