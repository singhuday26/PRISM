"""Integration tests for risk API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestRiskComputeEndpoint:
    """Tests for POST /risk/compute endpoint."""
    
    def test_compute_risk_success(self, client):
        """Test successful risk computation."""
        response = client.post("/risk/compute")
        # Should succeed even without date (uses latest)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_200_OK]
        data = response.json()
        assert "date" in data
        assert "risk_scores" in data
        assert "count" in data
        assert isinstance(data["risk_scores"], list)
    
    def test_compute_risk_with_disease(self, client):
        """Test risk computation with disease filter."""
        response = client.post("/risk/compute?disease=DENGUE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("disease") == "DENGUE"
    
    def test_compute_risk_with_date(self, client):
        """Test risk computation with specific date."""
        response = client.post("/risk/compute?target_date=2021-07-15")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["date"] == "2021-07-15"
    
    def test_compute_risk_invalid_date(self, client):
        """Test that invalid date returns 422."""
        response = client.post("/risk/compute?target_date=invalid-date")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Check that the error response has structured format
        if isinstance(data["detail"], dict):
            assert "error" in data["detail"]
            assert "message" in data["detail"]


@pytest.mark.integration
class TestRiskLatestEndpoint:
    """Tests for GET /risk/latest endpoint."""
    
    def test_latest_risk_success(self, client):
        """Test fetching latest risk scores."""
        response = client.get("/risk/latest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "risk_scores" in data
        assert "count" in data
    
    def test_latest_risk_with_disease(self, client):
        """Test latest risk with disease filter."""
        response = client.get("/risk/latest?disease=DENGUE")
        assert response.status_code == status.HTTP_200_OK
    
    def test_latest_risk_with_region(self, client):
        """Test latest risk with region filter."""
        response = client.get("/risk/latest?region_id=IN-AP")
        assert response.status_code == status.HTTP_200_OK
    
    def test_latest_risk_empty_result(self, client):
        """Test that unknown disease returns empty list."""
        response = client.get("/risk/latest?disease=UNKNOWN_DISEASE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return empty list, not error
        assert data["count"] == 0
        assert data["risk_scores"] == []
