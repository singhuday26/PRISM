"""
Pytest configuration and shared fixtures for PRISM tests.
"""
import pytest
from datetime import datetime
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def app():
    """Create FastAPI application for testing."""
    from backend.app import create_app
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> Generator:
    """Create test client for API integration tests."""
    with TestClient(app) as test_client:
        yield test_client


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
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_region() -> Dict[str, Any]:
    """Sample region data."""
    return {
        "region_id": "IN-AP",
        "region_name": "Andhra Pradesh",
        "disease": "DENGUE",
    }


@pytest.fixture
def sample_case_daily() -> Dict[str, Any]:
    """Sample daily case data."""
    return {
        "region_id": "IN-AP",
        "date": "2021-07-15",
        "confirmed": 150,
        "deaths": 2,
        "recovered": 120,
        "disease": "DENGUE",
        "granularity": "monthly",
    }


@pytest.fixture
def sample_risk_score() -> Dict[str, Any]:
    """Sample risk score data."""
    return {
        "region_id": "IN-AP",
        "date": "2021-07-15",
        "risk_score": 0.85,
        "risk_level": "HIGH",
        "drivers": ["High 7-day growth", "Climate boost: +11%"],
        "disease": "DENGUE",
        "climate_info": {
            "base_risk": 0.77,
            "climate_multiplier": 1.8,
            "adjusted_risk": 0.85,
            "explanation": "Monsoon peak - high transmission risk",
            "season": "monsoon",
            "is_monsoon": True,
        }
    }


@pytest.fixture
def sample_alert() -> Dict[str, Any]:
    """Sample alert data."""
    return {
        "region_id": "IN-AP",
        "date": "2021-07-15",
        "risk_score": 0.85,
        "risk_level": "HIGH",
        "reason": "Risk score 0.85 >= threshold 0.70",
        "disease": "DENGUE",
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_forecast() -> Dict[str, Any]:
    """Sample forecast data."""
    return {
        "region_id": "IN-AP",
        "date": "2021-07-16",
        "pred_mean": 145.5,
        "pred_lower": 131.0,
        "pred_upper": 160.0,
        "model_version": "naive_v2",
        "source_granularity": "monthly",
        "disease": "DENGUE",
        "generated_at": datetime.utcnow(),
    }


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
