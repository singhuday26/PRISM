"""Integration tests for forecasts API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestForecastsGenerateEndpoint:
    """Tests for POST /forecasts/generate endpoint."""
    
    def test_generate_forecasts_success(self, client):
        """Test successful forecast generation."""
        response = client.post("/forecasts/generate")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "forecasts" in data
        assert "count" in data
        assert isinstance(data["forecasts"], list)
    
    def test_generate_forecasts_with_disease(self, client):
        """Test forecast generation with disease filter."""
        response = client.post("/forecasts/generate?disease=DENGUE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("disease") == "DENGUE"
    
    def test_generate_forecasts_with_granularity(self, client):
        """Test forecast generation with granularity parameter."""
        for granularity in ["yearly", "monthly", "weekly"]:
            response = client.post(f"/forecasts/generate?granularity={granularity}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data.get("granularity") == granularity
    
    def test_generate_forecasts_invalid_granularity(self, client):
        """Test that invalid granularity returns 422."""
        response = client.post("/forecasts/generate?granularity=hourly")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_forecasts_with_horizon(self, client):
        """Test forecast generation with custom horizon."""
        response = client.post("/forecasts/generate?horizon=14")
        assert response.status_code == status.HTTP_200_OK
    
    def test_generate_forecasts_horizon_validation(self, client):
        """Test that horizon is validated."""
        # Too high
        response = client.post("/forecasts/generate?horizon=100")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Too low
        response = client.post("/forecasts/generate?horizon=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestForecastsLatestEndpoint:
    """Tests for GET /forecasts/latest endpoint."""
    
    def test_latest_forecasts_success(self, client):
        """Test fetching latest forecasts."""
        response = client.get("/forecasts/latest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "forecasts" in data
        assert "count" in data
    
    def test_latest_forecasts_with_disease(self, client):
        """Test latest forecasts with disease filter."""
        response = client.get("/forecasts/latest?disease=DENGUE")
        assert response.status_code == status.HTTP_200_OK
    
    def test_latest_forecasts_with_horizon(self, client):
        """Test latest forecasts with horizon parameter."""
        response = client.get("/forecasts/latest?horizon=7")
        assert response.status_code == status.HTTP_200_OK
