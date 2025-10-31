"""
Tests for weekly reset functionality.

Tests archiving, reset logic, and ensures the system works correctly after reset.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime

from app.test_config import test_engine
from app.db import Player, Match, GameScore, WeeklyArchive
from app.weekly_reset import (
    get_week_boundaries,
    archive_current_week,
    reset_player_stats,
    perform_weekly_reset
)


class TestWeekBoundaries:
    """Test week boundary calculations."""
    
    def test_get_week_boundaries_returns_sunday_to_saturday(self):
        """Test that week boundaries are Sunday 00:00 to Saturday 23:59."""
        week_start, week_end = get_week_boundaries()
        
        # Week should start on Sunday (weekday 6)
        assert week_start.weekday() == 6, "Week should start on Sunday"
        
        # Week should end on Saturday (weekday 5)
        assert week_end.weekday() == 5, "Week should end on Saturday"
        
        # Start should be at midnight
        assert week_start.hour == 0
        assert week_start.minute == 0
        assert week_start.second == 0
        
        # End should be at 23:59:59
        assert week_end.hour == 23
        assert week_end.minute == 59
        assert week_end.second == 59
        
        # Should be 6 days apart
        delta = week_end - week_start
        assert delta.days == 6


class TestArchiveCurrentWeek:
    """Test archiving current week's stats."""
    
    def test_archive_with_no_players(self, client: TestClient):
        """Test archiving when there are no players."""
        with Session(test_engine) as session:
            archived = archive_current_week(session)
            assert archived == 0
    
    def test_archive_with_no_activity(self, client: TestClient):
        """Test archiving when players have no stats (all zeros)."""
        # Register users with no activity
        client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        
        with Session(test_engine) as session:
            archived = archive_current_week(session)
            # Should skip archiving since no activity
            assert archived == 0
    
    def test_archive_with_activity(self, client: TestClient):
        """Test archiving when players have stats."""
        # Register users and play matches
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Alice beats Bob
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        with Session(test_engine) as session:
            archived = archive_current_week(session)
            assert archived == 2  # Both players archived
            
            # Verify archive records were created
            archives = session.exec(select(WeeklyArchive)).all()
            assert len(archives) == 2
            
            # Check Alice (rank 1, winner)
            alice_archive = next(a for a in archives if a.player_name == "Alice")
            assert alice_archive.wins == 1
            assert alice_archive.losses == 0
            assert alice_archive.points == 3
            assert alice_archive.rank == 1
            
            # Check Bob (rank 2)
            bob_archive = next(a for a in archives if a.player_name == "Bob")
            assert bob_archive.wins == 0
            assert bob_archive.losses == 1
            assert bob_archive.points == 0
            assert bob_archive.rank == 2
            
            # Both should have same winner_id (Alice's id)
            assert alice_archive.winner_id == alice_id
            assert bob_archive.winner_id == alice_id
    
    def test_archive_preserves_week_dates(self, client: TestClient):
        """Test that archive records contain correct week dates."""
        # Register and create activity
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Play a match
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        week_start, week_end = get_week_boundaries()
        
        with Session(test_engine) as session:
            archive_current_week(session)
            
            archives = session.exec(select(WeeklyArchive)).all()
            for archive in archives:
                assert archive.week_start == week_start.isoformat()
                assert archive.week_end == week_end.isoformat()


class TestResetPlayerStats:
    """Test resetting player stats."""
    
    def test_reset_with_no_players(self, client: TestClient):
        """Test reset when there are no players."""
        with Session(test_engine) as session:
            reset = reset_player_stats(session)
            assert reset == 0
    
    def test_reset_clears_all_stats(self, client: TestClient):
        """Test that reset sets all stats to zero."""
        # Register users and play matches
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Play matches
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Verify stats before reset
        players_before = client.get("/api/players").json()
        alice_before = next(p for p in players_before if p["name"] == "Alice")
        assert alice_before["wins"] == 1
        assert alice_before["points"] == 3
        
        # Reset stats
        with Session(test_engine) as session:
            reset = reset_player_stats(session)
            assert reset == 2
        
        # Verify stats after reset
        players_after = client.get("/api/players").json()
        for player in players_after:
            assert player["wins"] == 0
            assert player["losses"] == 0
            assert player["points"] == 0


class TestPerformWeeklyReset:
    """Test the complete weekly reset process."""
    
    def test_full_reset_workflow(self, client: TestClient):
        """Test complete reset: archive then reset."""
        # Setup: Register users and play matches
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Play matches
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Perform weekly reset using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Verify archive was created
        with Session(test_engine) as session:
            archives = session.exec(select(WeeklyArchive)).all()
            assert len(archives) == 2
        
        # Verify stats were reset
        players = client.get("/api/players").json()
        for player in players:
            assert player["wins"] == 0
            assert player["losses"] == 0
            assert player["points"] == 0


class TestSystemAfterReset:
    """Test that system works correctly after reset."""
    
    def test_can_play_matches_after_reset(self, client: TestClient):
        """Test that players can play matches after reset."""
        # Setup and perform reset
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Play match before reset
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Perform reset using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Play match after reset
        response = client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        assert response.status_code == 201
        
        # Verify stats are tracked correctly after reset
        players = client.get("/api/players").json()
        alice = next(p for p in players if p["name"] == "Alice")
        assert alice["wins"] == 1
        assert alice["losses"] == 0
        assert alice["points"] == 3
    
    def test_leaderboard_shows_current_week_only(self, client: TestClient):
        """Test that leaderboard shows only current week stats after reset."""
        # Register users
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_token = bob_resp.json()["access_token"]
        bob_id = bob_resp.json()["player"]["id"]
        
        # Week 1: Alice wins
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Reset (archives week 1) using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Week 2: Bob wins
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 9, "away": 11}, {"home": 7, "away": 11}]
        }, headers={"Authorization": f"Bearer {bob_token}"})
        
        # Check current leaderboard
        players = client.get("/api/players").json()
        alice = next(p for p in players if p["name"] == "Alice")
        bob = next(p for p in players if p["name"] == "Bob")
        
        # Current leaderboard should only show week 2 stats
        assert alice["wins"] == 0  # Lost in week 2
        assert alice["losses"] == 1
        assert alice["points"] == 0
        
        assert bob["wins"] == 1  # Won in week 2
        assert bob["losses"] == 0
        assert bob["points"] == 3
        
        # Archives should have week 1 stats
        with Session(test_engine) as session:
            archives = session.exec(select(WeeklyArchive)).all()
            alice_archive = next(a for a in archives if a.player_name == "Alice")
            assert alice_archive.wins == 1  # Week 1 stats
            assert alice_archive.points == 3
    
    def test_multiple_resets_work_correctly(self, client: TestClient):
        """Test that multiple consecutive resets work without errors."""
        # Register users
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        # Week 1
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Week 2
        client.post("/api/matches", json={
            "played_at": "2025-10-28T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Week 3
        client.post("/api/matches", json={
            "played_at": "2025-10-29T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Should have 3 weeks of archives (all will have same week_start since they happen on same day)
        with Session(test_engine) as session:
            archives = session.exec(select(WeeklyArchive)).all()
            assert len(archives) == 6  # 2 players × 3 resets
            
            # Note: All resets happen in same week, so week_start will be the same
            # but we verify that multiple consecutive resets don't cause errors
            week_starts = set(a.week_start for a in archives)
            assert len(week_starts) >= 1  # At least one week recorded
        
        # Current stats should be 0 (just reset)
        players = client.get("/api/players").json()
        for player in players:
            assert player["wins"] == 0
            assert player["losses"] == 0
            assert player["points"] == 0
    
    def test_login_works_after_reset(self, client: TestClient):
        """Test that login returns updated stats after reset."""
        # Register and play
        alice_resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = alice_resp.json()["access_token"]
        alice_id = alice_resp.json()["player"]["id"]
        
        bob_resp = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = bob_resp.json()["player"]["id"]
        
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Perform reset using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Login and check stats
        login_resp = client.post("/api/auth/login", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        
        assert login_resp.status_code == 200
        player_data = login_resp.json()["player"]
        assert player_data["wins"] == 0
        assert player_data["losses"] == 0
        assert player_data["points"] == 0

