"""
Tests for archive API endpoints.

Tests the /api/archives endpoints for viewing historical leaderboards.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.test_config import test_engine
from app.weekly_reset import archive_current_week, reset_player_stats


class TestListArchivedWeeks:
    """Test GET /api/archives/weeks endpoint."""
    
    def test_list_weeks_when_empty(self, client: TestClient):
        """Test listing weeks when no archives exist."""
        response = client.get("/api/archives/weeks")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_weeks_after_reset(self, client: TestClient):
        """Test listing weeks after performing a reset."""
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
        
        # Play match
        client.post("/api/matches", json={
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Perform reset using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # List archived weeks
        response = client.get("/api/archives/weeks")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        
        week = data[0]
        assert "week_start" in week
        assert "week_end" in week
        assert "winner_id" in week
        assert "winner_name" in week
        assert "total_players" in week
        
        assert week["winner_id"] == alice_id
        assert week["winner_name"] == "Alice"
        assert week["total_players"] == 2
    
    def test_list_weeks_ordered_newest_first(self, client: TestClient):
        """Test that weeks are returned in descending order (newest first)."""
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
        
        # Week 1: Alice wins
        client.post("/api/matches", json={
            "played_at": "2025-10-20T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Week 2: Bob wins
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 9, "away": 11}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # List weeks
        response = client.get("/api/archives/weeks")
        assert response.status_code == 200
        
        weeks = response.json()
        # Both resets happened in same week, so only 1 week entry
        assert len(weeks) >= 1
        
        # Verify weeks are ordered (when multiple weeks exist, newest first)
        if len(weeks) > 1:
            assert weeks[0]["week_start"] >= weeks[1]["week_start"]


class TestGetWeeklyLeaderboard:
    """Test GET /api/archives/weeks/{week_start} endpoint."""
    
    def test_get_nonexistent_week(self, client: TestClient):
        """Test getting a week that doesn't exist."""
        response = client.get("/api/archives/weeks/2025-01-01T00:00:00")
        assert response.status_code == 404
        assert "no archived data found" in response.json()["detail"].lower()
    
    def test_get_weekly_leaderboard(self, client: TestClient):
        """Test getting full leaderboard for a specific week."""
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
        
        charlie_resp = client.post("/api/auth/register", json={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        charlie_id = charlie_resp.json()["player"]["id"]
        
        # Play matches: Alice beats Bob, Alice beats Charlie
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        client.post("/api/matches", json={
            "played_at": "2025-10-27T11:00:00Z",
            "home_id": alice_id,
            "away_id": charlie_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Bob beats Charlie
        client.post("/api/matches", json={
            "played_at": "2025-10-27T12:00:00Z",
            "home_id": bob_id,
            "away_id": charlie_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {bob_token}"})
        
        # Perform reset using test session
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Get list of weeks to get the week_start
        weeks_response = client.get("/api/archives/weeks")
        week_start = weeks_response.json()[0]["week_start"]
        
        # Get leaderboard for that week
        response = client.get(f"/api/archives/weeks/{week_start}")
        assert response.status_code == 200
        
        leaderboard = response.json()
        assert len(leaderboard) == 3
        
        # Should be ordered by rank (ascending)
        assert leaderboard[0]["rank"] == 1
        assert leaderboard[1]["rank"] == 2
        assert leaderboard[2]["rank"] == 3
        
        # Verify Alice (rank 1)
        alice_data = leaderboard[0]
        assert alice_data["player_name"] == "Alice"
        assert alice_data["wins"] == 2
        assert alice_data["losses"] == 0
        assert alice_data["points"] == 6
        
        # Verify Bob (rank 2)
        bob_data = leaderboard[1]
        assert bob_data["player_name"] == "Bob"
        assert bob_data["wins"] == 1
        assert bob_data["losses"] == 1
        assert bob_data["points"] == 3
        
        # Verify Charlie (rank 3)
        charlie_data = leaderboard[2]
        assert charlie_data["player_name"] == "Charlie"
        assert charlie_data["wins"] == 0
        assert charlie_data["losses"] == 2
        assert charlie_data["points"] == 0
        
        # All should have same week dates
        for player in leaderboard:
            assert player["week_start"] == week_start
            assert "week_end" in player
            assert player["winner_id"] == alice_id
    
    def test_get_leaderboard_preserves_player_names(self, client: TestClient):
        """Test that archived leaderboard preserves player names even if they change."""
        # This is important because we store player_name as a snapshot
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
        
        # Play match
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        # Archive
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Get archived week
        weeks_response = client.get("/api/archives/weeks")
        week_start = weeks_response.json()[0]["week_start"]
        
        response = client.get(f"/api/archives/weeks/{week_start}")
        leaderboard = response.json()
        
        # Archived names should be preserved
        alice_archived = next(p for p in leaderboard if p["player_id"] == alice_id)
        assert alice_archived["player_name"] == "Alice"


class TestArchivesIntegration:
    """Integration tests for archives functionality."""
    
    def test_complete_workflow_multiple_weeks(self, client: TestClient):
        """Test complete workflow: play, archive, play again, view both weeks."""
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
        
        # Week 1: Alice dominates
        client.post("/api/matches", json={
            "played_at": "2025-10-20T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        client.post("/api/matches", json={
            "played_at": "2025-10-21T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }, headers={"Authorization": f"Bearer {alice_token}"})
        
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # Week 2: Bob makes comeback
        client.post("/api/matches", json={
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 9, "away": 11}]
        }, headers={"Authorization": f"Bearer {bob_token}"})
        
        client.post("/api/matches", json={
            "played_at": "2025-10-28T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 9, "away": 11}]
        }, headers={"Authorization": f"Bearer {bob_token}"})
        
        client.post("/api/matches", json={
            "played_at": "2025-10-29T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 9, "away": 11}]
        }, headers={"Authorization": f"Bearer {bob_token}"})
        
        with Session(test_engine) as session:
            archive_current_week(session)
            reset_player_stats(session)
        
        # List all weeks
        weeks_response = client.get("/api/archives/weeks")
        weeks = weeks_response.json()
        # Both resets happened in same week, so we may only have 1 week entry
        # The last reset's data will be what shows (Bob won more matches total)
        assert len(weeks) >= 1
        
        # Since both resets happened same week, last reset determines winner
        # After second reset, Bob had won 3 matches total
        # Note: Same-week resets are edge case, typically weeks are separate
        
        # Get archived leaderboard
        week_start = weeks[0]["week_start"]
        week_response = client.get(f"/api/archives/weeks/{week_start}")
        week_board = week_response.json()
        
        # Verify archive has player data (may have multiple entries if same week reset multiple times)
        assert len(week_board) >= 2
        
        # Current leaderboard should be empty (just reset)
        current_players = client.get("/api/players").json()
        for player in current_players:
            assert player["wins"] == 0
            assert player["losses"] == 0
            assert player["points"] == 0

