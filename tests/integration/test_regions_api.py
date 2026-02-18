"""Integration tests for regions API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestRegionsEndpoints:
    """Tests for region listing endpoints."""

    def test_list_regions_success(self, client):
        """Test listing all regions."""
        response = client.get("/regions/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "regions" in data
        assert "count" in data
        assert data["count"] >= 1

    def test_regions_have_required_fields(self, client):
        """Test that each region has required fields."""
        response = client.get("/regions/")
        data = response.json()
        for region in data["regions"]:
            assert "region_id" in region

    def test_regions_contain_known_states(self, client):
        """Test that known Indian states are present."""
        response = client.get("/regions/")
        data = response.json()
        region_ids = [r["region_id"] for r in data["regions"]]
        # At minimum, expect Maharashtra
        assert "IN-MH" in region_ids
