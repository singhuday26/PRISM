"""Unit tests for analytics service (hotspot computation)."""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.analytics import compute_hotspots


class TestComputeHotspots:
    """Tests for compute_hotspots function."""

    @patch("backend.services.analytics.get_db")
    def test_returns_list(self, mock_get_db):
        """compute_hotspots should return a list."""
        mock_db = MagicMock()
        mock_db.__getitem__.return_value.aggregate.return_value = []
        mock_get_db.return_value = mock_db

        result = compute_hotspots()
        assert isinstance(result, list)

    @patch("backend.services.analytics.get_db")
    def test_default_limit_is_five(self, mock_get_db):
        """Default limit parameter should be 5."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        compute_hotspots()

        # Verify the pipeline includes $limit: 5
        pipeline = mock_col.aggregate.call_args[0][0]
        limit_stages = [s for s in pipeline if "$limit" in s]
        assert len(limit_stages) == 1
        assert limit_stages[0]["$limit"] == 5

    @patch("backend.services.analytics.get_db")
    def test_custom_limit(self, mock_get_db):
        """Custom limit should be applied."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        compute_hotspots(limit=10)

        pipeline = mock_col.aggregate.call_args[0][0]
        limit_stages = [s for s in pipeline if "$limit" in s]
        assert limit_stages[0]["$limit"] == 10

    @patch("backend.services.analytics.get_db")
    def test_disease_filter_adds_match(self, mock_get_db):
        """When disease is provided, pipeline should start with $match."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        compute_hotspots(disease="DENGUE")

        pipeline = mock_col.aggregate.call_args[0][0]
        assert pipeline[0] == {"$match": {"disease": "DENGUE"}}

    @patch("backend.services.analytics.get_db")
    def test_no_disease_no_match_stage(self, mock_get_db):
        """Without disease filter, pipeline should not start with $match."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        compute_hotspots()

        pipeline = mock_col.aggregate.call_args[0][0]
        assert "$match" not in pipeline[0]

    @patch("backend.services.analytics.get_db")
    def test_results_returned_as_is(self, mock_get_db):
        """Results from aggregation should be returned directly."""
        expected = [
            {"region_id": "IN-MH", "confirmed_sum": 100, "deaths_sum": 5},
            {"region_id": "IN-DL", "confirmed_sum": 80, "deaths_sum": 3},
        ]
        mock_col = MagicMock()
        mock_col.aggregate.return_value = expected
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        result = compute_hotspots(limit=2)
        assert result == expected

    @patch("backend.services.analytics.get_db")
    def test_db_error_propagates(self, mock_get_db):
        """Database errors should propagate."""
        mock_col = MagicMock()
        mock_col.aggregate.side_effect = Exception("DB error")
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_col
        mock_get_db.return_value = mock_db

        with pytest.raises(Exception, match="DB error"):
            compute_hotspots()
