"""Integration tests for pipeline API endpoints."""
import pytest
from fastapi import status

from backend.routes.auth import get_current_user


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
        """Test running pipeline starts a background task and returns task metadata."""
        client.app.dependency_overrides[get_current_user] = lambda: {"username": "test-admin", "role": "admin"}
        response = client.post("/pipeline/run", params={"disease": "DENGUE"})
        client.app.dependency_overrides.pop(get_current_user, None)

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert "task_id" in data
        assert data["message"] == "Pipeline execution started in background"
        assert data["status_url"].endswith(data["task_id"])

        # Status endpoint should return task state for generated task_id
        status_res = client.get(f"/pipeline/status/{data['task_id']}")
        assert status_res.status_code == status.HTTP_200_OK
        status_data = status_res.json()
        assert status_data["task_id"] == data["task_id"]
        assert status_data["disease"] == "DENGUE"
        assert status_data["status"] in {"queued", "processing", "completed", "failed"}

    def test_pipeline_run_with_custom_params(self, client):
        """Test running pipeline accepts custom params and stores them in task metadata."""
        client.app.dependency_overrides[get_current_user] = lambda: {"username": "test-admin", "role": "admin"}
        response = client.post(
            "/pipeline/run",
            params={"disease": "DENGUE", "horizon": 3, "granularity": "yearly"}
        )
        client.app.dependency_overrides.pop(get_current_user, None)

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        task_id = data["task_id"]

        status_res = client.get(f"/pipeline/status/{task_id}")
        assert status_res.status_code == status.HTTP_200_OK
        status_data = status_res.json()
        assert status_data["task_id"] == task_id
        assert status_data["params"]["horizon"] == 3
        assert status_data["params"]["granularity"] == "yearly"
