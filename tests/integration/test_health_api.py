"""Integration tests for health API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_ping_success(self, client):
        """Test simple ping endpoint."""
        response = client.get("/health/ping")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "PRISM API"
    
    def test_health_check_success(self, client):
        """Test comprehensive health check."""
        response = client.get("/health/")
        # May return 200 (healthy) or 503 (unhealthy depending on DB)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "PRISM API"
