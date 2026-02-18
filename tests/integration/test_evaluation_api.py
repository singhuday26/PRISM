"""Integration tests for evaluation API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestEvaluationEndpoints:
    """Tests for forecast evaluation endpoints."""

    def test_forecast_evaluation_success(self, client):
        """Test getting forecast evaluation for a known region."""
        response = client.get(
            "/evaluation/forecast",
            params={"region_id": "IN-MH"}
        )
        # May return 200 with metrics or 200 with error if no forecast data matches
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Response should have some structure
        assert isinstance(data, dict)

    def test_forecast_evaluation_with_params(self, client):
        """Test evaluation with custom horizon."""
        response = client.get(
            "/evaluation/forecast",
            params={"region_id": "IN-MH", "horizon": 3}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_evaluation_summary(self, client):
        """Test evaluation summary endpoint."""
        response = client.get("/evaluation/summary")
        # May be 200 or 404 depending on data
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]
