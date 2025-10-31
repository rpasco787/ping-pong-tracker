"""
API endpoints for weekly archives.

Endpoints for viewing historical weekly leaderboards and manual reset trigger.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, func
from typing import List
from ..schemas.archives import WeeklyArchiveOut, WeekInfo, ResetResponse
from ..db import WeeklyArchive, Player, get_session
from ..auth import get_current_user
from ..weekly_reset import perform_weekly_reset

router = APIRouter(prefix="/api/archives", tags=["archives"])


@router.get("/weeks", response_model=List[WeekInfo])
def list_archived_weeks(session: Session = Depends(get_session)):
    """
    List all available archived weeks with summary information.
    Returns weeks in descending order (newest first).
    (Public endpoint)
    """
    # Get distinct weeks with winner info
    statement = (
        select(
            WeeklyArchive.week_start,
            WeeklyArchive.week_end,
            WeeklyArchive.winner_id,
            func.count(WeeklyArchive.id).label('total_players')
        )
        .group_by(WeeklyArchive.week_start, WeeklyArchive.week_end, WeeklyArchive.winner_id)
        .order_by(WeeklyArchive.week_start.desc())
    )
    
    results = session.exec(statement).all()
    
    # Build response with winner names
    weeks = []
    for week_start, week_end, winner_id, total_players in results:
        # Get winner name
        winner = session.get(Player, winner_id)
        winner_name = winner.name if winner else "Unknown"
        
        weeks.append(WeekInfo(
            week_start=week_start,
            week_end=week_end,
            winner_id=winner_id,
            winner_name=winner_name,
            total_players=total_players
        ))
    
    return weeks


@router.get("/weeks/{week_start}", response_model=List[WeeklyArchiveOut])
def get_weekly_leaderboard(week_start: str, session: Session = Depends(get_session)):
    """
    Get the full leaderboard for a specific week.
    Returns players ordered by rank (ascending).
    (Public endpoint)
    
    Args:
        week_start: ISO format date string (e.g., "2025-10-27T00:00:00")
    """
    statement = (
        select(WeeklyArchive)
        .where(WeeklyArchive.week_start == week_start)
        .order_by(WeeklyArchive.rank.asc())
    )
    
    archives = session.exec(statement).all()
    
    if not archives:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No archived data found for week starting {week_start}"
        )
    
    return archives


# @router.post("/reset", response_model=ResetResponse)
# def manual_reset(
#     session: Session = Depends(get_session),
#     current_user: Player = Depends(get_current_user)
# ):
#     """
#     Manually trigger a weekly reset.
#     Archives current week's data and resets all player stats to 0.
#     (Protected endpoint - requires authentication)
    
#     Note: In a production system, you might want to restrict this to admin users only.
#     For now, any authenticated user can trigger a reset.
#     """
#     try:
#         # Import here to avoid circular import issues
#         from ..weekly_reset import archive_current_week, reset_player_stats
        
#         # Perform archive and reset
#         archived = archive_current_week(session)
#         reset = reset_player_stats(session)
        
#         return ResetResponse(
#             success=True,
#             message=f"Weekly reset completed successfully by {current_user.name}",
#             archived_players=archived,
#             reset_players=reset
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to perform reset: {str(e)}"
#         )

