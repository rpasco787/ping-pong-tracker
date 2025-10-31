"""
Schema models for weekly archive endpoints.
"""
from pydantic import BaseModel


class WeeklyArchiveOut(BaseModel):
    """Response model for a single player's archived weekly stats."""
    id: int
    week_start: str
    week_end: str
    winner_id: int
    player_id: int
    player_name: str
    wins: int
    losses: int
    points: int
    rank: int


class WeekInfo(BaseModel):
    """Information about an available week."""
    week_start: str
    week_end: str
    winner_id: int
    winner_name: str
    total_players: int


class ResetResponse(BaseModel):
    """Response from manual reset trigger."""
    success: bool
    message: str
    archived_players: int
    reset_players: int

