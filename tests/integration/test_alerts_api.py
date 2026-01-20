"""Integration tests for alerts API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestAlertsGenerateEndpoint:
    """Tests for POST /alerts/generate endpoint."""
    
    def test_generate_alerts_success(self, client):
        """Test successful alert generation."""
        response = client.post("/alerts/generate")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "alerts" in data
        assert "count" in data
        assert isinstance(data["alerts"], list)
    
    def test_generate_alerts_with_disease(self, client):
        """Test alert generation with disease filter."""
        response = client.post("/alerts/generate?disease=DENGUE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("disease") == "DENGUE"
    
    def test_generate_alerts_invalid_date(self, client):
        """Test that invalid date returns 422."""
        response = client.post("/alerts/generate?date=bad-date")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestAlertsLatestEndpoint:
    """Tests for GET /alerts/latest endpoint."""
    
    def test_latest_alerts_success(self, client):
        """Test fetching latest alerts."""
        response = client.get("/alerts/latest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "alerts" in data
        assert "count" in data
    
    def test_latest_alerts_with_limit(self, client):
        """Test latest alerts with limit parameter."""
        response = client.get("/alerts/latest?limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["alerts"]) <= 5
    
    def test_latest_alerts_limit_validation(self, client):
        """Test that limit is validated."""
        # Too high
        response = client.get("/alerts/latest?limit=200")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Too low
        response = client.get("/alerts/latest?limit=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
