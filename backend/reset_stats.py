# backend/reset_stats.py
from app.db import Player, Match, WeeklyArchive, engine
from sqlmodel import Session, select

def delete_all_players():
    """Reset all player stats to 0."""
    with Session(engine) as session:
        # Delete all player stats
        players = session.exec(select(Player)).all()
        for player in players:
            session.delete(player)
        
        session.commit()
        print(f"✓ Reset stats for {len(players)} players")

def delete_all_matches():
    """Delete all matches."""
    with Session(engine) as session:
        matches = session.exec(select(Match)).all()
        for match in matches:
            session.delete(match)
        session.commit()
        print(f"✓ Deleted {len(matches)} matches")

def delete_all_archives():
    """Delete all archives."""
    with Session(engine) as session:
        archives = session.exec(select(WeeklyArchive)).all()
        for archive in archives:
            session.delete(archive)
        session.commit()
        print(f"✓ Deleted {len(archives)} archives")

if __name__ == "__main__":
    #delete_all_archives()
    #delete_all_matches()
    #delete_all_players()
    print()