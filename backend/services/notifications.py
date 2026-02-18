import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

from backend.config import get_settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.settings = get_settings()

    def send_notifications(self, alerts: List[Dict[str, Any]]):
        """
        Dispatch notifications for a list of alerts to all enabled channels.
        """
        if not alerts:
            return

        channels = self.settings.alert_channels
        logger.info(f"Dispatching {len(alerts)} alerts to channels: {channels}")

        if "console" in channels:
            self._send_console(alerts)
        
        if "email" in channels:
            self._send_email(alerts)
            
        if "sms" in channels:
            self._send_sms(alerts)

    def _format_alert_message(self, alerts: List[Dict[str, Any]]) -> str:
        """Create a human-readable summary of alerts."""
        msg_lines = [f"🚨 PRISM ALERT REPORT: {len(alerts)} high-risk regions detected"]
        for alert in alerts:
            region = alert.get("region_id", "Unknown Region")
            score = alert.get("risk_score", 0.0)
            date = alert.get("date", "Unknown Date")
            disease = alert.get("disease", "General")
            msg_lines.append(f"- [{disease}] Region {region}: Risk Score {score:.2f} (Date: {date})")
        return "\n".join(msg_lines)

    def _send_console(self, alerts: List[Dict[str, Any]]):
        """Log alerts to console/logger."""
        msg = self._format_alert_message(alerts)
        logger.warning(f"\n{'='*40}\n{msg}\n{'='*40}")

    def _send_email(self, alerts: List[Dict[str, Any]]):
        """Send alerts via SMTP."""
        recipients = self.settings.alert_email_recipients
        if not recipients:
            logger.warning("Email alerting enabled but no recipients configured.")
            return
            
        if not self.settings.smtp_host or not self.settings.smtp_user:
            logger.warning("SMTP Config missing. Skipping email alerts.")
            return

        msg_body = self._format_alert_message(alerts)
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.settings.smtp_from
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"PRISM Alert System - {len(alerts)} Alerts"
            msg.attach(MIMEText(msg_body, 'plain'))

            server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
            server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Sent email alerts to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email notifications: {e}")

    def _send_sms(self, alerts: List[Dict[str, Any]]):
        """SMS alerting placeholder — requires Twilio integration.
        
        To enable, install twilio (pip install twilio), add TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER to Settings in config.py.
        """
        severities = {}
        for a in alerts:
            sev = a.get("severity", "UNKNOWN")
            severities[sev] = severities.get(sev, 0) + 1
        logger.warning(
            f"[SMS] Not configured — {len(alerts)} alert(s) skipped "
            f"(severity breakdown: {severities}). Set up Twilio to enable."
        )

def dispatch_notifications(alerts: List[Dict[str, Any]]):
    """Helper function to instantiate service and send."""
    service = NotificationService()
    service.send_notifications(alerts)
