# Testing Guide

This directory contains tests for the ping-pong tracker backend API. All tests use an **in-memory SQLite database** that is completely isolated from the production database (`ping_pong.db`).

## Quick Start

### Install Dependencies

First, install the testing dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
# From the backend directory
pytest
```

### Run Specific Test Files

```bash
# Run only database unit tests
pytest tests/test_db.py

# Run only player API tests
pytest tests/test_players.py

# Run only match API tests
pytest tests/test_matches.py
```

### Run Tests with More Output

```bash
# Show print statements and more details
pytest -v -s

# Show test durations
pytest --durations=10
```

## Test Structure

### `conftest.py`
Contains shared pytest fixtures used across all test files:

- **`setup_test_database`**: Creates test database schema before tests run (session scope)
- **`session`**: Provides a fresh database session for each test with clean data
- **`client`**: FastAPI TestClient with overridden dependencies for API testing
- **`sample_players`**: Creates sample player data (Alice, Bob, Charlie) for tests

### `test_db.py` - Database Unit Tests
Tests database models, constraints, and utility functions without involving the API:

- `TestComputeWinner`: Tests the winner calculation logic
- `TestPlayerModel`: Tests Player model creation and validation
- `TestMatchModel`: Tests Match model creation
- `TestGameScoreModel`: Tests GameScore model creation
- `TestWinPointsConstant`: Verifies the WIN_POINTS constant

### `test_players.py` - Player API Integration Tests
Tests the `/api/players` endpoints:

- `TestListPlayers`: Tests GET endpoint for listing and filtering players
- `TestCreatePlayer`: Tests POST endpoint for creating players
- `TestPlayerPersistence`: Tests that data persists correctly

### `test_matches.py` - Match API Integration Tests
Tests the `/api/matches` endpoints:

- `TestListMatches`: Tests GET endpoint for listing matches
- `TestCreateMatch`: Tests POST endpoint for creating matches and updating stats
- `TestCreateMatchValidation`: Tests validation rules for match creation
- `TestMatchPersistence`: Tests that data persists correctly

## How It Works

### In-Memory Database Isolation

The test suite uses an **in-memory SQLite database** (`sqlite:///:memory:`) instead of the production database. This means:

1. ✅ Tests never affect your production data
2. ✅ Tests run faster (no disk I/O)
3. ✅ Each test starts with a clean database
4. ✅ Database is automatically destroyed after tests

### Database Setup per Test

The `session` fixture ensures each test gets a fresh database:

```python
@pytest.fixture(scope="function")
def session():
    # Drop all tables
    SQLModel.metadata.drop_all(test_engine)
    # Recreate all tables
    SQLModel.metadata.create_all(test_engine)
    # Provide a session
    with Session(test_engine) as test_session:
        yield test_session
```

### FastAPI Dependency Override

The `client` fixture overrides the `get_session()` dependency to use the test database:

```python
@pytest.fixture(scope="function")
def client(session: Session):
    def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
```

## Writing New Tests

### Adding a Database Unit Test

```python
# In test_db.py
def test_my_database_logic(session: Session):
    """Test description."""
    # Create test data
    player = Player(name="Test", email="test@example.com")
    session.add(player)
    session.commit()
    
    # Assert expected behavior
    assert player.id is not None
```

### Adding an API Integration Test

```python
# In test_players.py or test_matches.py
def test_my_api_endpoint(client: TestClient, sample_players):
    """Test description."""
    # Make API request
    response = client.get("/api/players")
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
```

### Using Sample Data

The `sample_players` fixture provides three test players:

```python
def test_with_sample_data(sample_players):
    alice = sample_players["alice"]
    bob = sample_players["bob"]
    charlie = sample_players["charlie"]
    
    # Use them in your test
    assert alice.email == "alice@example.com"
    assert charlie.email is None
```

## Test Categories

You can mark tests with categories using pytest markers:

```python
@pytest.mark.unit
def test_database_logic():
    """Unit test for database."""
    pass

@pytest.mark.integration
def test_api_endpoint():
    """Integration test for API."""
    pass

@pytest.mark.slow
def test_expensive_operation():
    """Test that takes a while."""
    pass
```

Run specific categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Troubleshooting

### Tests Fail Due to Import Errors

Make sure you're running pytest from the `backend` directory:

```bash
cd backend
pytest
```

### Tests Fail with Database Errors

The test database is isolated and recreated for each test. If you see database errors:

1. Check that `app/test_config.py` is using `sqlite:///:memory:`
2. Verify that the `session` fixture is being used in your test
3. Ensure you're not importing the production `engine` in tests

### Need to See Production Database

The tests never touch `ping_pong.db`. To verify:

```bash
# Check production database before tests
sqlite3 ping_pong.db "SELECT * FROM player;"

# Run tests
pytest

# Check production database after tests (should be unchanged)
sqlite3 ping_pong.db "SELECT * FROM player;"
```

## Best Practices

1. ✅ **Always use fixtures**: Use `session` and `client` fixtures to ensure isolation
2. ✅ **Test one thing**: Each test should verify a single behavior
3. ✅ **Use descriptive names**: Test names should explain what they're testing
4. ✅ **Clean and independent**: Tests should not depend on each other
5. ✅ **Assert clearly**: Include helpful assertion messages when needed

## Example Test Session

```bash
$ pytest -v

tests/test_db.py::TestComputeWinner::test_home_wins_simple PASSED
tests/test_db.py::TestComputeWinner::test_away_wins_simple PASSED
tests/test_players.py::TestListPlayers::test_list_empty_players PASSED
tests/test_players.py::TestCreatePlayer::test_create_player_with_email PASSED
tests/test_matches.py::TestCreateMatch::test_create_match_home_wins PASSED

========================= 5 passed in 1.23s =========================
```

All tests pass without affecting your production database! 🎉

