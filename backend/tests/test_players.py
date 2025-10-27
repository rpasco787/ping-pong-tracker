"""
Integration tests for player API endpoints.

Tests the /api/players endpoints using the FastAPI TestClient
with the test database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestListPlayers:
    """Test GET /api/players endpoint."""
    
    def test_list_empty_players(self, client: TestClient):
        """Test listing players when database is empty."""
        response = client.get("/api/players")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_players(self, client: TestClient, sample_players):
        """Test listing all players."""
        response = client.get("/api/players")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Should be sorted by name
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"
        assert data[2]["name"] == "Charlie"
        
        # Check structure
        for player in data:
            assert "id" in player
            assert "name" in player
            assert "email" in player
            assert "wins" in player
            assert "losses" in player
            assert "points" in player
    
    def test_list_players_with_query(self, client: TestClient, sample_players):
        """Test filtering players by name query."""
        response = client.get("/api/players?q=ali")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice"
    
    def test_list_players_query_case_insensitive(self, client: TestClient, sample_players):
        """Test that name filtering is case-insensitive."""
        response = client.get("/api/players?q=CHARLIE")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Charlie"
    
    def test_list_players_query_no_match(self, client: TestClient, sample_players):
        """Test query with no matching players."""
        response = client.get("/api/players?q=nonexistent")
        assert response.status_code == 200
        assert response.json() == []


class TestCreatePlayer:
    """Test POST /api/players endpoint."""
    
    def test_create_player_with_email(self, client: TestClient):
        """Test creating a player with email."""
        payload = {
            "name": "New Player",
            "email": "newplayer@example.com"
        }
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["id"] is not None
        assert data["name"] == "New Player"
        assert data["email"] == "newplayer@example.com"
        assert data["wins"] == 0
        assert data["losses"] == 0
        assert data["points"] == 0
    
    def test_create_player_without_email(self, client: TestClient):
        """Test creating a player without email."""
        payload = {"name": "Anonymous"}
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Anonymous"
        assert data["email"] is None
    
    def test_create_player_duplicate_email(self, client: TestClient, sample_players):
        """Test that duplicate emails are rejected."""
        payload = {
            "name": "Duplicate",
            "email": "alice@example.com"  # Alice already exists
        }
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"].lower()
    
    def test_create_player_invalid_email(self, client: TestClient):
        """Test that invalid email format is rejected."""
        payload = {
            "name": "Bad Email",
            "email": "not-an-email"
        }
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_player_empty_name(self, client: TestClient):
        """Test that empty name is rejected."""
        payload = {"name": ""}
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_player_missing_name(self, client: TestClient):
        """Test that missing name is rejected."""
        payload = {"email": "test@example.com"}
        response = client.post("/api/players", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_multiple_players_without_email(self, client: TestClient):
        """Test that multiple players can have null emails."""
        payload1 = {"name": "Player 1"}
        payload2 = {"name": "Player 2"}
        
        response1 = client.post("/api/players", json=payload1)
        response2 = client.post("/api/players", json=payload2)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["email"] is None
        assert response2.json()["email"] is None


class TestPlayerPersistence:
    """Test that player data persists correctly."""
    
    def test_player_appears_in_list_after_creation(self, client: TestClient):
        """Test that newly created player appears in list."""
        # Create a player
        payload = {"name": "Test Player", "email": "test@example.com"}
        create_response = client.post("/api/players", json=payload)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # List players and verify it's there
        list_response = client.get("/api/players")
        assert list_response.status_code == 200
        
        players = list_response.json()
        assert len(players) == 1
        assert players[0]["id"] == created_id
        assert players[0]["name"] == "Test Player"

