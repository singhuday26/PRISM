"""Integration tests for diseases API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestDiseasesEndpoints:
    """Tests for disease configuration endpoints."""

    def test_list_diseases_success(self, client):
        """Test listing all configured diseases."""
        response = client.get("/diseases/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "diseases" in data
        assert data["count"] >= 2  # at least DENGUE and COVID configured
        disease_ids = [d["disease_id"] for d in data["diseases"]]
        assert "DENGUE" in disease_ids
        assert "COVID" in disease_ids

    def test_list_diseases_has_required_fields(self, client):
        """Test that each disease has required configuration fields."""
        response = client.get("/diseases/")
        data = response.json()
        for disease in data["diseases"]:
            assert "disease_id" in disease
            assert "name" in disease
            assert "transmission_mode" in disease
            assert "severity" in disease

    def test_filter_by_transmission_mode(self, client):
        """Test filtering diseases by transmission mode."""
        response = client.get("/diseases/", params={"transmission_mode": "vector"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for disease in data["diseases"]:
            assert disease["transmission_mode"] == "vector"

    def test_filter_by_severity(self, client):
        """Test filtering diseases by severity."""
        response = client.get("/diseases/", params={"severity": "high"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for disease in data["diseases"]:
            assert disease["severity"] == "high"
