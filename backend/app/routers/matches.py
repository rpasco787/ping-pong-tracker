from fastapi import APIRouter, HTTPException, status
from typing import List
from ..schemas.matches import MatchIn, MatchOut
from ..store import store, Match, GameScore, compute_winner, WIN_POINTS

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("", response_model=List[MatchOut])
def list_matches():
    # Most recent first by simple id (we assign sequentially)
    return sorted(store.matches, key=lambda m: m["id"], reverse=True)


@router.post("", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(payload: MatchIn):
    # Validate players exist
    if payload.home_id not in store.players or payload.away_id not in store.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both home_id and away_id must refer to existing players.",
        )

    # Prepare typed games for our store
    games: List[GameScore] = [{"home": g.home, "away": g.away} for g in payload.games]

    # Decide winner based on games
    winner = compute_winner(games)
    home_won = winner == "home"

    # Create and store the match
    mid = store.next_match_id()
    match: Match = {
        "id": mid,
        "played_at": payload.played_at,
        "home_id": payload.home_id,
        "away_id": payload.away_id,
        "games": games,
    }
    store.matches.append(match)

    # Update player aggregates (wins/losses/points)
    home_player = store.players[payload.home_id]
    away_player = store.players[payload.away_id]

    if home_won:
        home_player["wins"] += 1
        away_player["losses"] += 1
        home_player["points"] += WIN_POINTS
    else:
        away_player["wins"] += 1
        home_player["losses"] += 1
        away_player["points"] += WIN_POINTS

    return match
