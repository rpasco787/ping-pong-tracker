"""
Pytest configuration and shared fixtures for testing.

This file contains reusable fixtures that set up test database,
sessions, and test client for API testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.db import get_session, Player
from app.test_config import (
    test_engine,
    get_test_session,
    create_test_db,
    drop_test_db,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create test database tables before any tests run,
    and drop them after all tests complete.
    """
    create_test_db()
    yield
    drop_test_db()


@pytest.fixture(scope="function")
def session():
    """
    Provide a fresh database session for each test.
    All data is cleaned up after each test by dropping and recreating tables.
    """
    # Clean up any existing data before each test
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as test_session:
        yield test_session


@pytest.fixture(scope="function")
def client(session: Session):
    """
    Provide a FastAPI TestClient with overridden database dependency.
    This client makes HTTP requests to the API using the test database.
    """
    def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up override after test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_players(session: Session):
    """
    Create sample players for testing.
    Returns a dict with player objects for easy reference.
    """
    alice = Player(
        name="Alice",
        email="alice@example.com",
        wins=0,
        losses=0,
        points=0,
    )
    bob = Player(
        name="Bob",
        email="bob@example.com",
        wins=0,
        losses=0,
        points=0,
    )
    charlie = Player(
        name="Charlie",
        email=None,  # Test player without email
        wins=0,
        losses=0,
        points=0,
    )
    
    session.add(alice)
    session.add(bob)
    session.add(charlie)
    session.commit()
    session.refresh(alice)
    session.refresh(bob)
    session.refresh(charlie)
    
    return {
        "alice": alice,
        "bob": bob,
        "charlie": charlie,
    }

