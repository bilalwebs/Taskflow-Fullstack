"""
Test Configuration and Fixtures

This module provides pytest fixtures and configuration for all test suites.
Fixtures include database setup, user authentication, and MCP context mocking.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from datetime import datetime

from src.database import engine as production_engine
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
from src.tools.mcp_server import MCPContext, mcp_server


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_engine():
    """
    Create an in-memory SQLite database engine for testing.

    Uses StaticPool to ensure the same connection is reused,
    which is necessary for in-memory databases.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.

    Provides a clean database session for each test.
    Automatically rolls back changes after test completion.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def clean_database(test_session):
    """
    Ensure database is clean before each test.

    Deletes all records from all tables.
    """
    # Delete in order to respect foreign key constraints
    test_session.query(Message).delete()
    test_session.query(Conversation).delete()
    test_session.query(Task).delete()
    test_session.query(User).delete()
    test_session.commit()

    yield test_session


# ============================================================================
# User Authentication Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_user(test_session) -> User:
    """
    Create a test user.

    Returns a User instance with id=1 for testing.
    """
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        password_hash="$2b$12$test_hash",  # Dummy hash
        created_at=datetime.utcnow()
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_user2(test_session) -> User:
    """
    Create a second test user for cross-user isolation tests.

    Returns a User instance with id=2 for testing.
    """
    user = User(
        id=2,
        email="test2@example.com",
        name="Test User 2",
        password_hash="$2b$12$test_hash2",  # Dummy hash
        created_at=datetime.utcnow()
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_jwt_token(test_user) -> str:
    """
    Create a test JWT token for authentication.

    Returns a valid JWT token for the test user.
    """
    from jose import jwt
    from src.config import settings
    from datetime import timedelta

    payload = {
        "user_id": test_user.id,
        "email": test_user.email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
def auth_headers(test_jwt_token) -> dict:
    """
    Create authentication headers with JWT token.

    Returns headers dict with Authorization header.
    """
    return {
        "Authorization": f"Bearer {test_jwt_token}"
    }


# ============================================================================
# MCP Context Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_mcp_context(test_engine, test_user) -> MCPContext:
    """
    Create a mock MCPContext for testing tools.

    Returns an MCPContext instance with test database engine
    and test user_id pre-bound.
    """
    context = MCPContext(
        db_engine=test_engine,
        user_id=test_user.id,
        config={}
    )

    return context


@pytest.fixture(scope="function")
def mock_mcp_context_user2(test_engine, test_user2) -> MCPContext:
    """
    Create a mock MCPContext for second test user.

    Used for cross-user isolation testing.
    """
    context = MCPContext(
        db_engine=test_engine,
        user_id=test_user2.id,
        config={}
    )

    return context


# ============================================================================
# Event Loop Fixtures (for async tests)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.

    Provides a single event loop for the entire test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_client():
    """
    Create a FastAPI test client.

    Returns a TestClient instance for testing API endpoints.
    """
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app)
    return client


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mcp_server():
    """
    Reset MCP server state between tests.

    Ensures tools are properly registered and no state leaks between tests.
    """
    # MCP server is stateless, but we verify tool registration
    assert len(mcp_server.list_tools()) == 6, "Expected 6 tools registered"

    yield

    # No cleanup needed for stateless server
