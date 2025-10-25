from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from ..schemas.players import PlayerIn, PlayerOut
from ..store import store, Player

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=List[PlayerOut])
def list_players(q: Optional[str] = None):
    players = list(store.players.values())
    if q:
        q_lower = q.lower()
        players = [p for p in players if q_lower in p["name"].lower()]
    # sort by name for determinism
    players.sort(key=lambda p: p["name"].lower())
    return players


@router.post(
    "", response_model=PlayerOut, status_code=status.HTTP_201_CREATED
)
def create_player(payload: PlayerIn):
    # (Optional) Enforce unique email if provided
    if payload.email:
        for p in store.players.values():
            if p["email"] == payload.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A player with this email already exists.",
                )
    pid = store.next_player_id()
    player: Player = {
        "id": pid,
        "name": payload.name,
        "email": payload.email,
        "wins": 0,
        "losses": 0,
        "points": 0,
    }
    store.players[pid] = player
    return player
