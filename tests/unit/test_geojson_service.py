"""
Unit tests for GeoJSON service.
"""
import pytest
from backend.services.geojson import (
    get_risk_level,
    get_risk_color,
    risk_to_geojson_feature,
    RISK_COLORS,
    INDIA_STATE_GEOMETRIES,
)


class TestGetRiskLevel:
    """Tests for get_risk_level function."""
    
    def test_critical_threshold(self):
        """Score >= 0.7 should be CRITICAL."""
        assert get_risk_level(0.7) == "CRITICAL"
        assert get_risk_level(0.85) == "CRITICAL"
        assert get_risk_level(1.0) == "CRITICAL"
    
    def test_high_threshold(self):
        """Score 0.5-0.7 should be HIGH."""
        assert get_risk_level(0.5) == "HIGH"
        assert get_risk_level(0.6) == "HIGH"
        assert get_risk_level(0.69) == "HIGH"
    
    def test_medium_threshold(self):
        """Score 0.3-0.5 should be MEDIUM."""
        assert get_risk_level(0.3) == "MEDIUM"
        assert get_risk_level(0.4) == "MEDIUM"
        assert get_risk_level(0.49) == "MEDIUM"
    
    def test_low_threshold(self):
        """Score < 0.3 should be LOW."""
        assert get_risk_level(0.0) == "LOW"
        assert get_risk_level(0.1) == "LOW"
        assert get_risk_level(0.29) == "LOW"


class TestGetRiskColor:
    """Tests for get_risk_color function."""
    
    def test_valid_levels(self):
        """Valid risk levels should return correct colors."""
        assert get_risk_color("LOW") == "#22c55e"
        assert get_risk_color("MEDIUM") == "#eab308"
        assert get_risk_color("HIGH") == "#f97316"
        assert get_risk_color("CRITICAL") == "#ef4444"
    
    def test_case_insensitive(self):
        """Risk levels should be case-insensitive."""
        assert get_risk_color("low") == "#22c55e"
        assert get_risk_color("High") == "#f97316"
    
    def test_unknown_level(self):
        """Unknown risk levels should return default gray."""
        assert get_risk_color("UNKNOWN") == "#9ca3af"
        assert get_risk_color("") == "#9ca3af"


class TestRiskToGeojsonFeature:
    """Tests for risk_to_geojson_feature function."""
    
    def test_basic_conversion(self):
        """Test basic risk data to GeoJSON feature conversion."""
        risk_data = {
            "region_id": "IN-MH",
            "risk_score": 0.75,
            "risk_level": "CRITICAL",
            "disease": "DENGUE",
            "date": "2024-01-15",
            "drivers": ["increasing_cases", "monsoon"]
        }
        
        feature = risk_to_geojson_feature(risk_data)
        
        assert feature["type"] == "Feature"
        assert feature["properties"]["region_id"] == "IN-MH"
        assert feature["properties"]["risk_score"] == 0.75
        assert feature["properties"]["risk_level"] == "CRITICAL"
        assert feature["properties"]["disease"] == "DENGUE"
        assert "geometry" in feature
    
    def test_known_region_gets_name(self):
        """Known region IDs should get proper names."""
        risk_data = {"region_id": "IN-MH", "risk_score": 0.5}
        feature = risk_to_geojson_feature(risk_data)
        
        assert feature["properties"]["region_name"] == "Maharashtra"
    
    def test_unknown_region_uses_id_as_name(self):
        """Unknown region IDs should use ID as name."""
        risk_data = {"region_id": "UNKNOWN-123", "risk_score": 0.5}
        feature = risk_to_geojson_feature(risk_data)
        
        assert feature["properties"]["region_name"] == "UNKNOWN-123"
    
    def test_includes_risk_color(self):
        """Feature should include risk_color property."""
        risk_data = {"region_id": "IN-MH", "risk_score": 0.8, "risk_level": "CRITICAL"}
        feature = risk_to_geojson_feature(risk_data)
        
        assert feature["properties"]["risk_color"] == "#ef4444"
    
    def test_auto_calculates_risk_level(self):
        """If risk_level not provided, it should be calculated from score."""
        risk_data = {"region_id": "IN-MH", "risk_score": 0.35}
        feature = risk_to_geojson_feature(risk_data)
        
        assert feature["properties"]["risk_level"] == "MEDIUM"


class TestIndiaStateGeometries:
    """Tests for India state geometry data."""
    
    def test_has_major_states(self):
        """Should include major Indian states."""
        major_states = ["IN-MH", "IN-KA", "IN-TN", "IN-UP", "IN-DL", "IN-WB"]
        for state in major_states:
            assert state in INDIA_STATE_GEOMETRIES
    
    def test_state_has_required_fields(self):
        """Each state should have name and center coordinates."""
        for state_id, info in INDIA_STATE_GEOMETRIES.items():
            assert "name" in info, f"{state_id} missing name"
            assert "center" in info, f"{state_id} missing center"
            assert len(info["center"]) == 2, f"{state_id} center should be [lng, lat]"
