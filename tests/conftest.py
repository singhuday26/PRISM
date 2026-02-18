"""
Pytest configuration and shared fixtures for PRISM tests.
"""
import os
import pytest
from datetime import datetime
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Set default environment variables for tests
if not os.getenv("MONGO_URI"):
    os.environ["MONGO_URI"] = "mongodb://localhost:27017/prism_test"
if not os.getenv("API_URL"):
    os.environ["API_URL"] = "http://localhost:8000"
if not os.getenv("LOG_LEVEL"):
    os.environ["LOG_LEVEL"] = "INFO"


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def app():
    """Create FastAPI application for testing."""
    from backend.app import create_app
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """Create test client for API integration tests."""
    return TestClient(app)


# ============================================================================
# Mock Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db():
    """Create a mock database for unit tests."""
    mock = MagicMock()
    mock.__getitem__ = MagicMock(return_value=MagicMock())
    return mock


@pytest.fixture
def mock_get_db(mock_db):
    """Patch get_db to return mock database."""
    with patch("backend.db.get_db", return_value=mock_db):
        yield mock_db


# ============================================================================
# Validation Test Data
# ============================================================================

@pytest.fixture
def valid_dates():
    """List of valid ISO date strings."""
    return [
        "2021-01-01",
        "2021-12-31",
        "2020-02-29",  # Leap year
        "2023-06-15",
    ]


@pytest.fixture
def invalid_dates():
    """List of invalid date strings."""
    return [
        "2021/01/01",      # Wrong separator
        "01-01-2021",      # Wrong order
        "2021-13-01",      # Invalid month
        "2021-02-30",      # Invalid day
        "not-a-date",      # Not a date
        "2021-1-1",        # Missing leading zeros
        "",                # Empty string
    ]


@pytest.fixture
def valid_diseases():
    """List of valid disease names."""
    return ["DENGUE", "COVID", "COVID-19", "dengue", "Dengue"]


@pytest.fixture
def valid_granularities():
    """List of valid granularity values."""
    return ["yearly", "monthly", "weekly"]


@pytest.fixture
def invalid_granularities():
    """List of invalid granularity values."""
    return ["daily", "hourly", "Annual", "biweekly"]
