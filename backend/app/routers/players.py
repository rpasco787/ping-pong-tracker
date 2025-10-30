from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List, Optional
from ..schemas.players import PlayerOut
from ..db import Player, get_session

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=List[PlayerOut])
def list_players(q: Optional[str] = None, session: Session = Depends(get_session)):
    """List all players, optionally filtered by name query. (Public endpoint)"""
    statement = select(Player)
    if q:
        q_lower = q.lower()
        statement = statement.where(Player.name.ilike(f"%{q_lower}%"))
    
    players = session.exec(statement).all()
    # Sort by name for determinism
    players.sort(key=lambda p: p.name.lower())
    return players


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, session: Session = Depends(get_session)):
    """Get a player by ID. (Public endpoint)"""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player
