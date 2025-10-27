"""
Test configuration module for database isolation.

This module provides a separate in-memory SQLite database for testing
that doesn't affect the production database.
"""
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator

# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with echo disabled for cleaner test output
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def get_test_session() -> Generator[Session, None, None]:
    """
    Test database session dependency override.
    Use this to override get_session() in FastAPI tests.
    """
    with Session(test_engine) as session:
        yield session


def create_test_db():
    """
    Create all tables in the test database.
    Call this before running tests to set up the schema.
    """
    SQLModel.metadata.create_all(test_engine)


def drop_test_db():
    """
    Drop all tables from the test database.
    Call this after tests to clean up.
    """
    SQLModel.metadata.drop_all(test_engine)

