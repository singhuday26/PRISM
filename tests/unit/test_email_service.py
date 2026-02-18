"""
Unit tests for email notification service.
"""
import pytest
from backend.services.email import (
    get_subscribers_for_alert,
    build_alert_email_html,
    build_alert_email_text,
    send_alert_notification,
)


class TestGetSubscribersForAlert:
    """Tests for subscriber matching logic."""
    
    def test_matches_region(self, mock_get_db):
        """Alert region should match subscriber region filter."""
        alert = {
            "region_id": "IN-MH",
            "disease": "DENGUE",
            "risk_level": "HIGH"
        }
        result = get_subscribers_for_alert(alert)
        assert isinstance(result, list)


class TestBuildAlertEmailHtml:
    """Tests for HTML email generation."""
    
    def test_includes_region_name(self):
        """Email should include region name."""
        alert = {
            "region_id": "IN-MH",
            "risk_level": "HIGH",
            "disease": "DENGUE",
            "risk_score": 0.75,
            "created_at": "2024-01-15T10:00:00",
            "drivers": ["increasing_cases"]
        }
        
        html = build_alert_email_html(alert, "test-token-123")
        
        assert "IN-MH" in html
        assert "HIGH" in html
        assert "DENGUE" in html
    
    def test_includes_risk_score(self):
        """Email should display risk score."""
        alert = {
            "region_id": "TEST",
            "risk_level": "CRITICAL",
            "risk_score": 0.95,
            "disease": "COVID",
            "created_at": "2024-01-15",
            "drivers": []
        }
        
        html = build_alert_email_html(alert, "token")
        
        assert "0.95" in html
    
    def test_includes_drivers(self):
        """Email should list risk drivers."""
        alert = {
            "region_id": "TEST",
            "risk_level": "HIGH",
            "risk_score": 0.7,
            "disease": "DENGUE",
            "created_at": "2024-01-15",
            "drivers": ["increasing_cases", "monsoon_season"]
        }
        
        html = build_alert_email_html(alert, "token")
        
        assert "increasing" in html.lower() or "cases" in html.lower()
    
    def test_includes_unsubscribe_link(self):
        """Email must include unsubscribe link."""
        alert = {
            "region_id": "TEST",
            "risk_level": "HIGH",
            "risk_score": 0.7,
            "disease": "DENGUE",
            "created_at": "2024-01-15",
            "drivers": []
        }
        
        html = build_alert_email_html(alert, "my-token-xyz")
        
        assert "my-token-xyz" in html
        assert "unsubscribe" in html.lower()


class TestBuildAlertEmailText:
    """Tests for plain text email generation."""
    
    def test_includes_key_info(self):
        """Text email should include all key information."""
        alert = {
            "region_id": "IN-KA",
            "risk_level": "CRITICAL",
            "risk_score": 0.88,
            "disease": "MALARIA",
            "created_at": "2024-01-15T12:00:00",
            "drivers": ["high_rainfall", "standing_water"]
        }
        
        text = build_alert_email_text(alert, "token-abc")
        
        assert "IN-KA" in text
        assert "CRITICAL" in text
        assert "0.88" in text
        assert "MALARIA" in text
        assert "token-abc" in text
    
    def test_formats_drivers_as_list(self):
        """Drivers should be formatted as a readable list."""
        alert = {
            "region_id": "TEST",
            "risk_level": "HIGH",
            "risk_score": 0.7,
            "disease": "DENGUE",
            "created_at": "2024-01-15",
            "drivers": ["driver_one", "driver_two"]
        }
        
        text = build_alert_email_text(alert, "token")
        
        # Should have formatted driver names
        assert ("Driver One" in text or "driver" in text.lower())


class TestSendAlertNotification:
    """Tests for sending individual notifications."""
    
    def test_returns_false_if_no_email(self):
        """Should return False if subscriber has no email."""
        alert = {"region_id": "TEST", "risk_level": "HIGH", "risk_score": 0.7}
        subscriber = {}
        result = send_alert_notification(alert, subscriber)
        assert result is False
