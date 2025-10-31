"""
Weekly reset functionality for the ping pong leaderboard.

This module handles:
- Archiving current week's stats to WeeklyArchive table
- Resetting all player stats to 0
- Scheduled execution every Sunday at midnight
"""
from datetime import datetime, timedelta
from sqlmodel import Session, select
from .db import Player, WeeklyArchive, engine


def get_week_boundaries() -> tuple[datetime, datetime]:
    """
    Get the start (Sunday) and end (Saturday) of current week.
    
    Returns:
        tuple: (week_start, week_end) as datetime objects
    """
    today = datetime.now()
    # Find last Sunday (0 = Monday, 6 = Sunday in weekday())
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = (today - timedelta(days=days_since_sunday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = (week_start + timedelta(days=6)).replace(
        hour=23, minute=59, second=59, microsecond=0
    )
    return week_start, week_end


def archive_current_week(session: Session) -> int:
    """
    Archive all current player stats to WeeklyArchive table.
    
    Creates a snapshot of each player's current stats (wins, losses, points, rank)
    for the current week. Skips archiving if no activity (all players at 0 points).
    
    Args:
        session: Database session
        
    Returns:
        int: Number of players archived
    """
    week_start, week_end = get_week_boundaries()
    
    # Get all players sorted by points (descending) for ranking
    # Secondary sort by wins to break ties
    statement = select(Player).order_by(Player.points.desc(), Player.wins.desc())
    players = session.exec(statement).all()
    
    # Skip if no players or no activity (all at 0 points and wins)
    if not players or all(p.points == 0 and p.wins == 0 for p in players):
        print(f"No activity this week ({week_start.date()} to {week_end.date()}), skipping archive")
        return 0
    
    # Determine winner (player with most points)
    winner_id = players[0].id if players else None
    
    # Create archive records for each player
    archived_count = 0
    for rank, player in enumerate(players, start=1):
        archive = WeeklyArchive(
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            winner_id=winner_id,
            player_id=player.id,
            player_name=player.name,
            wins=player.wins,
            losses=player.losses,
            points=player.points,
            rank=rank
        )
        session.add(archive)
        archived_count += 1
    
    session.commit()
    print(f"Archived {archived_count} players for week {week_start.date()} to {week_end.date()}")
    return archived_count


def reset_player_stats(session: Session) -> int:
    """
    Reset all player wins/losses/points to 0.
    
    Args:
        session: Database session
        
    Returns:
        int: Number of players reset
    """
    statement = select(Player)
    players = session.exec(statement).all()
    
    for player in players:
        player.wins = 0
        player.losses = 0
        player.points = 0
        session.add(player)
    
    session.commit()
    print(f"Reset stats for {len(players)} players")
    return len(players)


def perform_weekly_reset():
    """
    Main function to archive current week and reset stats.
    
    This function should be called by the scheduler every Sunday at midnight.
    It performs the following steps:
    1. Archive current week's stats to WeeklyArchive table
    2. Reset all player stats (wins, losses, points) to 0
    
    Raises:
        Exception: If archiving or reset fails
    """
    with Session(engine) as session:
        try:
            print(f"Starting weekly reset at {datetime.now()}")
            archived = archive_current_week(session)
            reset = reset_player_stats(session)
            print(f"Weekly reset completed: {archived} players archived, {reset} players reset")
        except Exception as e:
            print(f"Error during weekly reset: {e}")
            session.rollback()
            raise
