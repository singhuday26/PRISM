"""Integration tests for resources API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestResourcesPredictEndpoint:
    """Tests for POST /resources/predict endpoint."""

    def test_predict_resources_success(self, client):
        """Test successful resource prediction with valid params."""
        response = client.post(
            "/resources/predict?region_id=IN-MH&date=2024-01-15&disease=DENGUE"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "region_id" in data
        assert "forecasted_cases" in data
        assert "resources" in data
        resources = data["resources"]
        assert "general_beds" in resources
        assert "icu_beds" in resources

    def test_predict_resources_invalid_date(self, client):
        """Test that invalid date format returns 422."""
        response = client.post(
            "/resources/predict?region_id=IN-MH&date=bad-date&disease=DENGUE"
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_resources_invalid_disease(self, client):
        """Test that unknown disease still returns 200 with default config."""
        response = client.post(
            "/resources/predict?region_id=IN-MH&date=2024-01-15&disease=INVALID"
        )
        # The resource endpoint uses defaults for unknown diseases
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestResourcesConfigEndpoint:
    """Tests for GET /resources/config/{disease} endpoint."""

    def test_get_config_success(self, client):
        """Test fetching resource config for a valid disease."""
        response = client.get("/resources/config/DENGUE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "disease" in data

    def test_get_config_invalid_disease(self, client):
        """Test that unknown disease returns 200 with default config."""
        response = client.get("/resources/config/NONEXISTENT")
        # Resources service uses defaults for any unknown disease
        assert response.status_code == status.HTTP_200_OK
