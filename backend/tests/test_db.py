"""
Unit tests for database models and logic.

Tests the database models, constraints, and utility functions
without involving the API layer.
"""
import pytest
from sqlmodel import Session, select

from app.db import Player, Match, GameScore, compute_winner, WIN_POINTS


class TestComputeWinner:
    """Test the compute_winner utility function."""
    
    def test_home_wins_simple(self):
        """Test home player winning 2-1."""
        games = [
            GameScore(match_id=1, home=11, away=9),
            GameScore(match_id=1, home=11, away=8),
            GameScore(match_id=1, home=9, away=11),
        ]
        assert compute_winner(games) == "home"
    
    def test_away_wins_simple(self):
        """Test away player winning 2-1."""
        games = [
            GameScore(match_id=1, home=11, away=9),
            GameScore(match_id=1, home=9, away=11),
            GameScore(match_id=1, home=8, away=11),
        ]
        assert compute_winner(games) == "away"
    
    def test_home_wins_sweep(self):
        """Test home player winning 3-0."""
        games = [
            GameScore(match_id=1, home=11, away=5),
            GameScore(match_id=1, home=11, away=7),
            GameScore(match_id=1, home=11, away=9),
        ]
        assert compute_winner(games) == "home"
    
    def test_away_wins_sweep(self):
        """Test away player winning 3-0."""
        games = [
            GameScore(match_id=1, home=5, away=11),
            GameScore(match_id=1, home=7, away=11),
            GameScore(match_id=1, home=9, away=11),
        ]
        assert compute_winner(games) == "away"
    
    def test_single_game_match(self):
        """Test match with only one game."""
        games = [GameScore(match_id=1, home=11, away=9)]
        assert compute_winner(games) == "home"
        
        games = [GameScore(match_id=1, home=9, away=11)]
        assert compute_winner(games) == "away"


class TestPlayerModel:
    """Test Player model creation and constraints."""
    
    def test_create_player_with_email(self, session: Session):
        """Test creating a player with all fields."""
        player = Player(
            name="Test Player",
            email="test@example.com",
            wins=5,
            losses=3,
            points=15,
        )
        session.add(player)
        session.commit()
        session.refresh(player)
        
        assert player.id is not None
        assert player.name == "Test Player"
        assert player.email == "test@example.com"
        assert player.wins == 5
        assert player.losses == 3
        assert player.points == 15
    
    def test_create_player_without_email(self, session: Session):
        """Test creating a player without email."""
        player = Player(
            name="Anonymous Player",
            email=None,
            wins=0,
            losses=0,
            points=0,
        )
        session.add(player)
        session.commit()
        session.refresh(player)
        
        assert player.id is not None
        assert player.name == "Anonymous Player"
        assert player.email is None
    
    def test_player_default_stats(self, session: Session):
        """Test that player stats default to 0."""
        player = Player(name="New Player")
        session.add(player)
        session.commit()
        session.refresh(player)
        
        assert player.wins == 0
        assert player.losses == 0
        assert player.points == 0
    
    def test_unique_email_constraint(self, session: Session):
        """Test that duplicate emails are rejected."""
        player1 = Player(name="Player 1", email="duplicate@example.com")
        session.add(player1)
        session.commit()
        
        # Try to create another player with same email
        player2 = Player(name="Player 2", email="duplicate@example.com")
        session.add(player2)
        
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            session.commit()


class TestMatchModel:
    """Test Match model creation."""
    
    def test_create_match(self, session: Session, sample_players):
        """Test creating a match between two players."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        match = Match(
            played_at="2025-10-27T14:30:00Z",
            home_id=alice.id,
            away_id=bob.id,
        )
        session.add(match)
        session.commit()
        session.refresh(match)
        
        assert match.id is not None
        assert match.home_id == alice.id
        assert match.away_id == bob.id
        assert match.played_at == "2025-10-27T14:30:00Z"


class TestGameScoreModel:
    """Test GameScore model creation."""
    
    def test_create_game_score(self, session: Session, sample_players):
        """Test creating game scores for a match."""
        alice = sample_players["alice"]
        bob = sample_players["bob"]
        
        match = Match(
            played_at="2025-10-27T14:30:00Z",
            home_id=alice.id,
            away_id=bob.id,
        )
        session.add(match)
        session.commit()
        session.refresh(match)
        
        game = GameScore(
            match_id=match.id,
            home=11,
            away=9,
        )
        session.add(game)
        session.commit()
        session.refresh(game)
        
        assert game.id is not None
        assert game.match_id == match.id
        assert game.home == 11
        assert game.away == 9


class TestWinPointsConstant:
    """Test WIN_POINTS constant value."""
    
    def test_win_points_value(self):
        """Verify that WIN_POINTS is set to 3."""
        assert WIN_POINTS == 3

