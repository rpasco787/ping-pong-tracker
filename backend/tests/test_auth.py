"""
Integration tests for authentication and authorized match creation.

Tests the /api/auth endpoints (register, login) and match creation
with authentication enforcement.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.test_config import test_engine
from app.db import Player


class TestRegistration:
    """Test POST /api/auth/register endpoint."""
    
    def test_register_new_user(self, client: TestClient):
        """Test successful user registration."""
        payload = {
            "name": "Alice",
            "email": "alice@example.com"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "player" in data
        
        player = data["player"]
        assert player["name"] == "Alice"
        assert player["email"] == "alice@example.com"
        assert player["wins"] == 0
        assert player["losses"] == 0
        assert player["points"] == 0
        assert "id" in player
    
    def test_register_duplicate_email(self, client: TestClient):
        """Test that registering with duplicate email fails."""
        payload = {
            "name": "Alice",
            "email": "alice@example.com"
        }
        
        # Register first user
        response1 = client.post("/api/auth/register", json=payload)
        assert response1.status_code == 201
        
        # Try to register with same email
        payload2 = {
            "name": "Alice2",
            "email": "alice@example.com"  # Same email
        }
        response2 = client.post("/api/auth/register", json=payload2)
        assert response2.status_code == 400
        assert "email already exists" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, client: TestClient):
        """Test that invalid email format is rejected."""
        payload = {
            "name": "Alice",
            "email": "not-an-email"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_register_empty_name(self, client: TestClient):
        """Test that empty name is rejected."""
        payload = {
            "name": "",
            "email": "alice@example.com"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_fields(self, client: TestClient):
        """Test that missing required fields are rejected."""
        # Missing email
        response1 = client.post("/api/auth/register", json={"name": "Alice"})
        assert response1.status_code == 422
        
        # Missing name
        response2 = client.post("/api/auth/register", json={"email": "alice@example.com"})
        assert response2.status_code == 422
    
    def test_register_creates_player_in_database(self, client: TestClient):
        """Test that registration creates a player in the database."""
        payload = {
            "name": "Alice",
            "email": "alice@example.com"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201
        
        # Verify player is in database
        with Session(test_engine) as session:
            player = session.query(Player).filter(Player.email == "alice@example.com").first()
            assert player is not None
            assert player.name == "Alice"


class TestLogin:
    """Test POST /api/auth/login endpoint."""
    
    def test_login_success(self, client: TestClient):
        """Test successful login with correct credentials."""
        # Register a user first
        register_payload = {
            "name": "Bob",
            "email": "bob@example.com"
        }
        client.post("/api/auth/register", json=register_payload)
        
        # Login with correct credentials
        login_payload = {
            "name": "Bob",
            "email": "bob@example.com"
        }
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "player" in data
        
        player = data["player"]
        assert player["name"] == "Bob"
        assert player["email"] == "bob@example.com"
    
    def test_login_wrong_email(self, client: TestClient):
        """Test that login fails with wrong email."""
        # Register a user
        register_payload = {
            "name": "Bob",
            "email": "bob@example.com"
        }
        client.post("/api/auth/register", json=register_payload)
        
        # Try to login with wrong email
        login_payload = {
            "name": "Bob",
            "email": "wrong@example.com"
        }
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 401
        assert "no player found" in response.json()["detail"].lower()
    
    def test_login_wrong_name(self, client: TestClient):
        """Test that login fails with wrong name."""
        # Register a user
        register_payload = {
            "name": "Bob",
            "email": "bob@example.com"
        }
        client.post("/api/auth/register", json=register_payload)
        
        # Try to login with wrong name
        login_payload = {
            "name": "WrongName",
            "email": "bob@example.com"
        }
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test that login fails for non-existent user."""
        login_payload = {
            "name": "Nonexistent",
            "email": "nonexistent@example.com"
        }
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 401
    
    def test_login_returns_updated_stats(self, client: TestClient):
        """Test that login returns current player stats."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        # Alice creates a match and wins
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [
                {"home": 11, "away": 9},
                {"home": 11, "away": 7}
            ]
        }
        headers = {"Authorization": f"Bearer {alice_token}"}
        client.post("/api/matches", json=match_payload, headers=headers)
        
        # Login again and check stats are updated
        login_response = client.post("/api/auth/login", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        
        assert login_response.status_code == 200
        player = login_response.json()["player"]
        assert player["wins"] == 1
        assert player["losses"] == 0
        assert player["points"] == 3


class TestAuthenticatedMatchCreation:
    """Test creating matches with authentication."""
    
    def test_create_match_without_token(self, client: TestClient):
        """Test that creating a match without authentication fails."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        # Try to create match without token
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        
        response = client.post("/api/matches", json=match_payload)
        assert response.status_code == 403  # Forbidden (no auth header)
    
    def test_create_match_with_invalid_token(self, client: TestClient):
        """Test that creating a match with invalid token fails."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        # Try to create match with invalid token
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = client.post("/api/matches", json=match_payload, headers=headers)
        assert response.status_code == 401
    
    def test_create_match_as_home_player(self, client: TestClient):
        """Test that user can create match where they are home player."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        # Alice creates match where she is home player
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        headers = {"Authorization": f"Bearer {alice_token}"}
        
        response = client.post("/api/matches", json=match_payload, headers=headers)
        assert response.status_code == 201
    
    def test_create_match_as_away_player(self, client: TestClient):
        """Test that user can create match where they are away player."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_token = register2.json()["access_token"]
        bob_id = register2.json()["player"]["id"]
        
        # Bob creates match where he is away player
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        headers = {"Authorization": f"Bearer {bob_token}"}
        
        response = client.post("/api/matches", json=match_payload, headers=headers)
        assert response.status_code == 201
    
    def test_create_match_for_other_players(self, client: TestClient):
        """Test that user cannot create match between other players."""
        # Register three users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        register3 = client.post("/api/auth/register", json={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        charlie_token = register3.json()["access_token"]
        
        # Charlie tries to create match between Alice and Bob
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        headers = {"Authorization": f"Bearer {charlie_token}"}
        
        response = client.post("/api/matches", json=match_payload, headers=headers)
        assert response.status_code == 403
        assert "you are one of the players" in response.json()["detail"].lower()


class TestMultiUserMatchScenarios:
    """Test complex scenarios with multiple users creating matches."""
    
    def test_multiple_users_multiple_matches(self, client: TestClient):
        """Test that multiple users can create matches and stats are tracked correctly."""
        # Register three users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_token = register2.json()["access_token"]
        bob_id = register2.json()["player"]["id"]
        
        register3 = client.post("/api/auth/register", json={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        charlie_token = register3.json()["access_token"]
        charlie_id = register3.json()["player"]["id"]
        
        # Alice beats Bob
        match1 = {
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }
        response1 = client.post("/api/matches", json=match1, 
                               headers={"Authorization": f"Bearer {alice_token}"})
        assert response1.status_code == 201
        
        # Bob beats Charlie
        match2 = {
            "played_at": "2025-10-27T11:00:00Z",
            "home_id": bob_id,
            "away_id": charlie_id,
            "games": [{"home": 11, "away": 8}, {"home": 11, "away": 9}]
        }
        response2 = client.post("/api/matches", json=match2,
                               headers={"Authorization": f"Bearer {bob_token}"})
        assert response2.status_code == 201
        
        # Charlie beats Alice
        match3 = {
            "played_at": "2025-10-27T12:00:00Z",
            "home_id": charlie_id,
            "away_id": alice_id,
            "games": [{"home": 11, "away": 5}, {"home": 11, "away": 6}]
        }
        response3 = client.post("/api/matches", json=match3,
                               headers={"Authorization": f"Bearer {charlie_token}"})
        assert response3.status_code == 201
        
        # Check final stats
        players_response = client.get("/api/players")
        players = {p["name"]: p for p in players_response.json()}
        
        # Alice: 1 win, 1 loss, 3 points
        assert players["Alice"]["wins"] == 1
        assert players["Alice"]["losses"] == 1
        assert players["Alice"]["points"] == 3
        
        # Bob: 1 win, 1 loss, 3 points
        assert players["Bob"]["wins"] == 1
        assert players["Bob"]["losses"] == 1
        assert players["Bob"]["points"] == 3
        
        # Charlie: 1 win, 1 loss, 3 points
        assert players["Charlie"]["wins"] == 1
        assert players["Charlie"]["losses"] == 1
        assert players["Charlie"]["points"] == 3
    
    def test_same_users_multiple_matches(self, client: TestClient):
        """Test that two users can play multiple matches against each other."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_token = register2.json()["access_token"]
        bob_id = register2.json()["player"]["id"]
        
        # Match 1: Alice wins (created by Alice)
        match1 = {
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}, {"home": 11, "away": 7}]
        }
        client.post("/api/matches", json=match1, 
                   headers={"Authorization": f"Bearer {alice_token}"})
        
        # Match 2: Bob wins (created by Bob)
        match2 = {
            "played_at": "2025-10-27T11:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 8, "away": 11}, {"home": 9, "away": 11}]
        }
        client.post("/api/matches", json=match2,
                   headers={"Authorization": f"Bearer {bob_token}"})
        
        # Match 3: Alice wins again (created by Alice)
        match3 = {
            "played_at": "2025-10-27T12:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 6}, {"home": 11, "away": 8}]
        }
        client.post("/api/matches", json=match3,
                   headers={"Authorization": f"Bearer {alice_token}"})
        
        # Check stats
        players_response = client.get("/api/players")
        players = {p["name"]: p for p in players_response.json()}
        
        # Alice: 2 wins, 1 loss, 6 points
        assert players["Alice"]["wins"] == 2
        assert players["Alice"]["losses"] == 1
        assert players["Alice"]["points"] == 6
        
        # Bob: 1 win, 2 losses, 3 points
        assert players["Bob"]["wins"] == 1
        assert players["Bob"]["losses"] == 2
        assert players["Bob"]["points"] == 3
        
        # Check that all matches are recorded
        matches_response = client.get("/api/matches")
        assert len(matches_response.json()) == 3
    
    def test_user_loses_their_own_match(self, client: TestClient):
        """Test that user can record a match where they lose."""
        # Register two users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_id = register2.json()["player"]["id"]
        
        # Alice creates match where she loses
        match_payload = {
            "played_at": "2025-10-27T14:30:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [
                {"home": 9, "away": 11},
                {"home": 7, "away": 11}
            ]
        }
        headers = {"Authorization": f"Bearer {alice_token}"}
        
        response = client.post("/api/matches", json=match_payload, headers=headers)
        assert response.status_code == 201
        
        # Check stats
        players_response = client.get("/api/players")
        players = {p["name"]: p for p in players_response.json()}
        
        assert players["Alice"]["wins"] == 0
        assert players["Alice"]["losses"] == 1
        assert players["Alice"]["points"] == 0
        
        assert players["Bob"]["wins"] == 1
        assert players["Bob"]["losses"] == 0
        assert players["Bob"]["points"] == 3
    
    def test_match_list_includes_all_users_matches(self, client: TestClient):
        """Test that match list shows matches from all users."""
        # Register three users
        register1 = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        alice_token = register1.json()["access_token"]
        alice_id = register1.json()["player"]["id"]
        
        register2 = client.post("/api/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        bob_token = register2.json()["access_token"]
        bob_id = register2.json()["player"]["id"]
        
        register3 = client.post("/api/auth/register", json={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        charlie_token = register3.json()["access_token"]
        charlie_id = register3.json()["player"]["id"]
        
        # Create matches from different users
        match1 = {
            "played_at": "2025-10-27T10:00:00Z",
            "home_id": alice_id,
            "away_id": bob_id,
            "games": [{"home": 11, "away": 9}]
        }
        client.post("/api/matches", json=match1, 
                   headers={"Authorization": f"Bearer {alice_token}"})
        
        match2 = {
            "played_at": "2025-10-27T11:00:00Z",
            "home_id": bob_id,
            "away_id": charlie_id,
            "games": [{"home": 11, "away": 8}]
        }
        client.post("/api/matches", json=match2,
                   headers={"Authorization": f"Bearer {bob_token}"})
        
        match3 = {
            "played_at": "2025-10-27T12:00:00Z",
            "home_id": charlie_id,
            "away_id": alice_id,
            "games": [{"home": 11, "away": 5}]
        }
        client.post("/api/matches", json=match3,
                   headers={"Authorization": f"Bearer {charlie_token}"})
        
        # Check that all matches are in the list
        matches_response = client.get("/api/matches")
        matches = matches_response.json()
        
        assert len(matches) == 3
        
        # Verify they are ordered by most recent first (by ID desc)
        assert matches[0]["played_at"] == "2025-10-27T12:00:00Z"
        assert matches[1]["played_at"] == "2025-10-27T11:00:00Z"
        assert matches[2]["played_at"] == "2025-10-27T10:00:00Z"

