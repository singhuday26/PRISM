"""Integration tests for pipeline API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestPipelineStatusEndpoint:
    """Tests for pipeline status endpoint."""

    def test_pipeline_status_success(self, client):
        """Test getting pipeline status without disease filter."""
        response = client.get("/pipeline/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "risk_scores" in data
        assert "alerts" in data
        assert "forecasts" in data
        assert isinstance(data["risk_scores"], int)
        assert isinstance(data["alerts"], int)
        assert isinstance(data["forecasts"], int)

    def test_pipeline_status_with_disease(self, client):
        """Test getting pipeline status filtered by disease."""
        response = client.get("/pipeline/status", params={"disease": "DENGUE"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("disease") == "DENGUE"
        assert "risk_scores" in data


@pytest.mark.integration
class TestPipelineRunEndpoint:
    """Tests for pipeline run endpoint."""

    def test_pipeline_run_success(self, client):
        """Test running pipeline for DENGUE (idempotent - uses existing data)."""
        response = client.post("/pipeline/run", params={"disease": "DENGUE"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["disease"] == "DENGUE"
        assert "created" in data
        assert "total" in data
        assert "execution_date" in data

    def test_pipeline_run_with_custom_params(self, client):
        """Test running pipeline with custom horizon and granularity."""
        response = client.post(
            "/pipeline/run",
            params={"disease": "DENGUE", "horizon": 3, "granularity": "yearly"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["horizon"] == 3
        assert data["granularity"] == "yearly"
