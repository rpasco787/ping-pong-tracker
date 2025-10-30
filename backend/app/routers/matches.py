from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List
from ..schemas.matches import MatchIn, MatchOut, GameScore as GameScoreSchema
from ..db import Match, GameScore, Player, get_session, compute_winner, WIN_POINTS
from ..auth import get_current_user

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("", response_model=List[MatchOut])
def list_matches(session: Session = Depends(get_session)):
    """List all matches, most recent first. (Public endpoint)"""
    statement = select(Match).order_by(Match.id.desc())
    matches = session.exec(statement).all()
    
    # Build response with games for each match
    result = []
    for match in matches:
        games_statement = select(GameScore).where(GameScore.match_id == match.id)
        games = session.exec(games_statement).all()
        
        result.append(
            MatchOut(
                id=match.id,
                played_at=match.played_at,
                home_id=match.home_id,
                away_id=match.away_id,
                games=[GameScoreSchema(home=g.home, away=g.away) for g in games],
            )
        )
    
    return result


@router.post("", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(
    payload: MatchIn, 
    session: Session = Depends(get_session),
    current_user: Player = Depends(get_current_user)
):
    """Create a new match and update player stats. (Protected - requires authentication)"""
    # Validate that one of the players is the current user
    if current_user.id not in [payload.home_id, payload.away_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create matches where you are one of the players.",
        )
    
    # Validate players exist
    home_player = session.get(Player, payload.home_id)
    away_player = session.get(Player, payload.away_id)
    
    if not home_player or not away_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both home_id and away_id must refer to existing players.",
        )

    # Create match record
    match = Match(
        played_at=payload.played_at,
        home_id=payload.home_id,
        away_id=payload.away_id,
    )
    session.add(match)
    session.commit()
    session.refresh(match)

    # Create game score records
    game_scores = []
    for game in payload.games:
        game_score = GameScore(
            match_id=match.id,
            home=game.home,
            away=game.away,
        )
        session.add(game_score)
        game_scores.append(game_score)
    
    session.commit()
    for gs in game_scores:
        session.refresh(gs)

    # Determine winner and update player stats
    winner = compute_winner(game_scores)
    home_won = winner == "home"

    if home_won:
        home_player.wins += 1
        away_player.losses += 1
        home_player.points += WIN_POINTS
    else:
        away_player.wins += 1
        home_player.losses += 1
        away_player.points += WIN_POINTS

    session.add(home_player)
    session.add(away_player)
    session.commit()

    # Return match with games
    return MatchOut(
        id=match.id,
        played_at=match.played_at,
        home_id=match.home_id,
        away_id=match.away_id,
        games=[GameScoreSchema(home=g.home, away=g.away) for g in game_scores],
    )
