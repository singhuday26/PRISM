"""Integration tests for reports API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestReportsEndpoints:
    """Tests for report generation and listing endpoints."""

    def test_generate_report_accepted(self, client):
        """Test report generation returns 202 Accepted."""
        response = client.post(
            "/reports/generate",
            json={"type": "weekly_summary", "disease": "DENGUE"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert "report_id" in data
        assert data["status"] == "generating"
        assert "estimated_time_seconds" in data

    def test_generate_report_with_region(self, client):
        """Test report generation with region detail type."""
        response = client.post(
            "/reports/generate",
            json={"type": "region_detail", "region_id": "IN-MH", "disease": "DENGUE"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["report_id"].startswith("rpt_")

    def test_list_reports_success(self, client):
        """Test listing reports."""
        response = client.get("/reports/list")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reports" in data
        assert "count" in data
        assert isinstance(data["reports"], list)

    def test_list_reports_with_disease_filter(self, client):
        """Test listing reports filtered by disease."""
        response = client.get("/reports/list", params={"disease": "DENGUE"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["count"], int)
