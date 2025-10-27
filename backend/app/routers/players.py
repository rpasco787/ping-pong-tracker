from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List, Optional
from ..schemas.players import PlayerIn, PlayerOut
from ..db import Player, get_session

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=List[PlayerOut])
def list_players(q: Optional[str] = None, session: Session = Depends(get_session)):
    """List all players, optionally filtered by name query."""
    statement = select(Player)
    if q:
        q_lower = q.lower()
        statement = statement.where(Player.name.ilike(f"%{q_lower}%"))
    
    players = session.exec(statement).all()
    # Sort by name for determinism
    players.sort(key=lambda p: p.name.lower())
    return players


@router.post(
    "", response_model=PlayerOut, status_code=status.HTTP_201_CREATED
)
def create_player(payload: PlayerIn, session: Session = Depends(get_session)):
    """Create a new player."""
    # Check for duplicate email if provided
    if payload.email:
        existing = session.exec(
            select(Player).where(Player.email == payload.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A player with this email already exists.",
            )
    
    # Create new player
    player = Player(
        name=payload.name,
        email=payload.email,
        wins=0,
        losses=0,
        points=0,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    return player
