"""
Unit tests for report generation service.
"""
import pytest
from backend.services.reports import (
    create_risk_trend_chart,
    create_risk_trend_chart_base64,
    get_risk_color,
)
from reportlab.lib import colors


class TestCreateRiskTrendChart:
    """Tests for risk trend chart generation."""
    
    def test_returns_none_for_no_data(self):
        """Should return None if no data provided."""
        result = create_risk_trend_chart([])
        assert result is None
    
    def test_returns_bytesio_for_valid_data(self):
        """Should return BytesIO buffer with chart image."""
        risk_data = [
            {"date": "2024-01-01", "risk_score": 0.5},
            {"date": "2024-01-02", "risk_score": 0.6},
            {"date": "2024-01-03", "risk_score": 0.7},
        ]
        
        result = create_risk_trend_chart(risk_data)
        
        assert result is not None
        # Should be BytesIO with PNG data
        result.seek(0)
        data = result.read()
        assert len(data) > 100
        assert data[:4] == b'\x89PNG'  # PNG signature
    
    def test_sorts_data_by_date(self):
        """Chart should handle unsorted input data."""
        risk_data = [
            {"date": "2024-01-03", "risk_score": 0.7},
            {"date": "2024-01-01", "risk_score": 0.5},
            {"date": "2024-01-02", "risk_score": 0.6},
        ]
        
        result = create_risk_trend_chart(risk_data)
        assert result is not None


class TestCreateRiskTrendChartBase64:
    """Tests for base64 chart generation."""
    
    def test_returns_empty_for_no_data(self):
        """Should return empty string if no data."""
        result = create_risk_trend_chart_base64([])
        assert result == ""
    
    def test_returns_base64_data_uri(self):
        """Should return base64-encoded PNG data URI."""
        risk_data = [
            {"date": "2024-01-01", "risk_score": 0.5},
            {"date": "2024-01-02", "risk_score": 0.6},
        ]
        
        result = create_risk_trend_chart_base64(risk_data)
        
        assert result.startswith("data:image/png;base64,")


class TestGetRiskColor:
    """Tests for risk level color mapping."""
    
    def test_critical_returns_red(self):
        """CRITICAL should return red color."""
        result = get_risk_color("CRITICAL")
        assert result == colors.HexColor('#ef4444')
    
    def test_high_returns_orange(self):
        """HIGH should return orange color."""
        result = get_risk_color("HIGH")
        assert result == colors.HexColor('#f97316')
    
    def test_medium_returns_yellow(self):
        """MEDIUM should return yellow color."""
        result = get_risk_color("MEDIUM")
        assert result == colors.HexColor('#eab308')
    
    def test_low_returns_green(self):
        """LOW should return green color."""
        result = get_risk_color("LOW")
        assert result == colors.HexColor('#22c55e')
    
    def test_unknown_returns_grey(self):
        """Unknown level should return grey."""
        result = get_risk_color("UNKNOWN")
        assert result == colors.grey


class TestReportGeneration:
    """Integration tests for full report generation."""
    
    def test_weekly_report_compiles(self):
        """Weekly report functions should exist and be callable."""
        from backend.services.reports import generate_weekly_summary_report
        assert callable(generate_weekly_summary_report)
    
    def test_region_report_compiles(self):
        """Region report functions should exist and be callable."""
        from backend.services.reports import generate_region_detail_report
        assert callable(generate_region_detail_report)
    
    def test_disease_report_compiles(self):
        """Disease report functions should exist and be callable."""
        from backend.services.reports import generate_disease_overview_report
        assert callable(generate_disease_overview_report)
