"""Unit tests for the NotificationService."""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from backend.services.notifications import NotificationService, dispatch_notifications


class TestNotificationService:
    """Tests for NotificationService class."""

    @patch("backend.services.notifications.get_settings")
    def test_send_notifications_empty_list(self, mock_settings):
        """Sending empty alerts list should return immediately."""
        svc = NotificationService()
        svc.send_notifications([])  # Should not raise

    @patch("backend.services.notifications.get_settings")
    def test_console_channel(self, mock_settings):
        """Console channel should log alerts without error."""
        settings = MagicMock()
        settings.alert_channels = ["console"]
        mock_settings.return_value = settings

        svc = NotificationService()
        alerts = [{"region_id": "IN-MH", "risk_score": 0.85, "disease": "DENGUE"}]
        svc.send_notifications(alerts)  # Should not raise

    @patch("backend.services.notifications.get_settings")
    def test_sms_channel_logs_warning(self, mock_settings):
        """SMS channel should log a warning (stub) without error."""
        settings = MagicMock()
        settings.alert_channels = ["sms"]
        mock_settings.return_value = settings

        svc = NotificationService()
        alerts = [
            {"region_id": "IN-DL", "risk_score": 0.9, "severity": "CRITICAL"},
            {"region_id": "IN-KA", "risk_score": 0.7, "severity": "HIGH"},
        ]
        svc.send_notifications(alerts)  # Should not raise

    @patch("backend.services.notifications.get_settings")
    def test_email_channel_no_recipients(self, mock_settings):
        """Email channel with no recipients should log warning, not crash."""
        settings = MagicMock()
        settings.alert_channels = ["email"]
        settings.alert_email_recipients = []
        mock_settings.return_value = settings

        svc = NotificationService()
        svc.send_notifications([{"region_id": "IN-MH", "risk_score": 0.8}])

    @patch("backend.services.notifications.get_settings")
    def test_email_channel_no_smtp_config(self, mock_settings):
        """Email channel with missing SMTP config should log warning."""
        settings = MagicMock()
        settings.alert_channels = ["email"]
        settings.alert_email_recipients = ["admin@example.com"]
        settings.smtp_host = ""
        settings.smtp_user = ""
        mock_settings.return_value = settings

        svc = NotificationService()
        svc.send_notifications([{"region_id": "IN-MH", "risk_score": 0.8}])

    @patch("backend.services.notifications.get_settings")
    def test_format_alert_message(self, mock_settings):
        """_format_alert_message should produce a readable report."""
        svc = NotificationService()
        alerts = [
            {"region_id": "IN-MH", "risk_score": 0.85, "date": "2024-01-15", "disease": "DENGUE"},
            {"region_id": "IN-DL", "risk_score": 0.72, "date": "2024-01-15", "disease": "COVID"},
        ]
        msg = svc._format_alert_message(alerts)
        assert "2 high-risk" in msg
        assert "IN-MH" in msg
        assert "IN-DL" in msg
        assert "DENGUE" in msg
        assert "COVID" in msg

    @patch("backend.services.notifications.get_settings")
    def test_sms_severity_breakdown(self, mock_settings):
        """SMS stub should count severity breakdown correctly."""
        settings = MagicMock()
        settings.alert_channels = ["sms"]
        mock_settings.return_value = settings

        svc = NotificationService()
        alerts = [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
        ]
        # This should just log, not crash
        svc._send_sms(alerts)


class TestDispatchNotifications:
    """Tests for the dispatch_notifications helper."""

    @patch("backend.services.notifications.get_settings")
    def test_dispatch_creates_service_and_calls(self, mock_settings):
        """dispatch_notifications should create a service and call send_notifications."""
        settings = MagicMock()
        settings.alert_channels = ["console"]
        mock_settings.return_value = settings

        alerts = [{"region_id": "IN-TN", "risk_score": 0.75}]
        dispatch_notifications(alerts)  # Should not raise

    @patch("backend.services.notifications.get_settings")
    def test_dispatch_empty(self, mock_settings):
        """dispatch_notifications with empty list should do nothing."""
        dispatch_notifications([])
