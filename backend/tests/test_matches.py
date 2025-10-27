"""
Integration tests for match API endpoints.

Tests the /api/matches endpoints using the FastAPI TestClient
with the test database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestListMatches:
    """Test GET /api/matches endpoint."""
    
    def test_list_empty_matches(self, client: TestClient):
        """Test listing matches when database is empty."""
        response = client.get("/api/matches")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_matches_ordered(self, client: TestClient, sample_players):
        """Test that matches are listed most recent first."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        # Create two matches
        match1_payload = {
            "played_at": "2025-10-26T10:00:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 11, "away": 7},
            ]
        }
        match2_payload = {
            "played_at": "2025-10-27T14:00:00Z",
            "home_id": bob.id,
            "away_id": alice.id,
            "games": [
                {"home": 11, "away": 9},
            ]
        }
        
        client.post("/api/matches", json=match1_payload)
        client.post("/api/matches", json=match2_payload)
        
        # List matches
        response = client.get("/api/matches")
        assert response.status_code == 200
        
        matches = response.json()
        assert len(matches) == 2
        
        # Most recent first (by ID desc, since IDs are sequential)
        assert matches[0]["played_at"] == "2025-10-27T14:00:00Z"
        assert matches[1]["played_at"] == "2025-10-26T10:00:00Z"


class TestCreateMatch:
    """Test POST /api/matches endpoint."""
    
    def test_create_match_home_wins(self, client: TestClient, sample_players):
        """Test creating a match where home player wins."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 11, "away": 7},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] is not None
        assert data["home_id"] == alice.id
        assert data["away_id"] == bob.id
        assert len(data["games"]) == 2
        assert data["games"][0]["home"] == 11
        assert data["games"][0]["away"] == 9
    
    def test_create_match_away_wins(self, client: TestClient, sample_players):
        """Test creating a match where away player wins."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T15:00:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 9, "away": 11},
                {"home": 8, "away": 11},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
    
    def test_create_match_updates_player_stats_home_wins(self, client: TestClient, sample_players):
        """Test that player stats are updated correctly when home player wins."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        # Verify initial stats
        assert alice.wins == 0
        assert alice.losses == 0
        assert alice.points == 0
        assert bob.wins == 0
        assert bob.losses == 0
        assert bob.points == 0
        
        # Create match where Alice (home) wins
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 11, "away": 7},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
        
        # Check updated stats
        players_response = client.get("/api/players")
        players = {p["id"]: p for p in players_response.json()}
        
        alice_updated = players[alice.id]
        bob_updated = players[bob.id]
        
        assert alice_updated["wins"] == 1
        assert alice_updated["losses"] == 0
        assert alice_updated["points"] == 3
        
        assert bob_updated["wins"] == 0
        assert bob_updated["losses"] == 1
        assert bob_updated["points"] == 0
    
    def test_create_match_updates_player_stats_away_wins(self, client: TestClient, sample_players):
        """Test that player stats are updated correctly when away player wins."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        # Create match where Bob (away) wins
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 9, "away": 11},
                {"home": 7, "away": 11},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
        
        # Check updated stats
        players_response = client.get("/api/players")
        players = {p["id"]: p for p in players_response.json()}
        
        alice_updated = players[alice.id]
        bob_updated = players[bob.id]
        
        assert alice_updated["wins"] == 0
        assert alice_updated["losses"] == 1
        assert alice_updated["points"] == 0
        
        assert bob_updated["wins"] == 1
        assert bob_updated["losses"] == 0
        assert bob_updated["points"] == 3
    
    def test_create_match_single_game(self, client: TestClient, sample_players):
        """Test creating a match with a single game."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [{"home": 11, "away": 9}]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["games"]) == 1
    
    def test_create_match_multiple_games(self, client: TestClient, sample_players):
        """Test creating a match with multiple games (best of 5)."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 9, "away": 11},
                {"home": 11, "away": 7},
                {"home": 9, "away": 11},
                {"home": 11, "away": 8},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["games"]) == 5
        
        # Alice won 3-2
        players_response = client.get("/api/players")
        players = {p["id"]: p for p in players_response.json()}
        assert players[alice.id]["wins"] == 1


class TestCreateMatchValidation:
    """Test validation for match creation."""
    
    def test_create_match_invalid_player_ids(self, client: TestClient):
        """Test that match creation fails with non-existent players."""
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": 9999,
            "away_id": 9998,
            "games": [{"home": 11, "away": 9}]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 400
        assert "existing players" in response.json()["detail"].lower()
    
    def test_create_match_same_player_both_sides(self, client: TestClient, sample_players):
        """Test that a player cannot play against themselves."""
        alice = sample_players["alice"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": alice.id,
            "games": [{"home": 11, "away": 9}]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_match_tied_games(self, client: TestClient, sample_players):
        """Test that match with even split of games is rejected."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 9, "away": 11},
            ]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 422  # Validation error
        assert "winner" in response.json()["detail"][0]["msg"].lower()
    
    def test_create_match_game_tied_score(self, client: TestClient, sample_players):
        """Test that a game with tied score is rejected."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [{"home": 10, "away": 10}]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_match_no_games(self, client: TestClient, sample_players):
        """Test that match without games is rejected."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": []
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_match_negative_score(self, client: TestClient, sample_players):
        """Test that negative scores are rejected."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [{"home": -1, "away": 11}]
        }
        
        response = client.post("/api/matches", json=payload)
        assert response.status_code == 422  # Validation error


class TestMatchPersistence:
    """Test that match data persists correctly."""
    
    def test_match_appears_in_list_after_creation(self, client: TestClient, sample_players):
        """Test that newly created match appears in list."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice.id,
            "away_id": bob.id,
            "games": [{"home": 11, "away": 9}]
        }
        
        create_response = client.post("/api/matches", json=payload)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # List matches and verify it's there
        list_response = client.get("/api/matches")
        assert list_response.status_code == 200
        
        matches = list_response.json()
        assert len(matches) == 1
        assert matches[0]["id"] == created_id
        assert matches[0]["home_id"] == alice.id
        assert matches[0]["away_id"] == bob.id

