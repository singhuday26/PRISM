"""
Email notification service for PRISM alerts.
"""
import logging
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime

from jinja2 import Template

from backend.config import get_settings
from backend.db import get_db

logger = logging.getLogger(__name__)


def get_subscribers_for_alert(alert: Dict) -> List[Dict]:
    """
    Find subscribers who should receive this alert.
    
    Args:
        alert: Alert document with region_id, disease, risk_level
        
    Returns:
        List of matching subscriber documents
    """
    try:
        db = get_db()
        subscribers_col = db["subscribers"]
        
        region_id = alert.get("region_id")
        disease = alert.get("disease")
        risk_level = alert.get("risk_level", "")
        
        # Build query for matching subscribers
        query = {
            "active": True,
            "$or": [
                {"regions": region_id},
                {"regions": {"$size": 0}},  # Empty regions means "all"
                {"regions": {"$exists": False}}
            ]
        }
        
        # Filter by disease if specified
        if disease:
            query["$and"] = [
                {
                    "$or": [
                        {"diseases": disease},
                        {"diseases": {"$size": 0}},
                        {"diseases": {"$exists": False}}
                    ]
                }
            ]
        
        # Find matching subscribers
        subscribers = list(subscribers_col.find(query))
        
        # Filter by risk level threshold
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        try:
            alert_level_idx = risk_levels.index(risk_level.upper())
        except ValueError:
            alert_level_idx = 0
        
        filtered_subscribers = []
        for sub in subscribers:
            min_level = sub.get("min_risk_level", "HIGH").upper()
            try:
                min_level_idx = risk_levels.index(min_level)
                if alert_level_idx >= min_level_idx:
                    filtered_subscribers.append(sub)
            except ValueError:
                continue
        
        return filtered_subscribers
        
    except Exception as e:
        logger.error(f"Error finding subscribers for alert: {e}")
        return []


def build_alert_email_html(alert: Dict, unsubscribe_token: str) -> str:
    """
    Build HTML email content for an alert.
    
    Args:
        alert: Alert document
        unsubscribe_token: Unsubscribe token for this subscriber
        
    Returns:
        HTML email content
    """
    settings = get_settings()
    dashboard_url = f"http://localhost:8501"  # TODO: Make configurable
    unsubscribe_url = f"{settings.api_url}/notifications/unsubscribe?token={unsubscribe_token}"
    
    risk_level = alert.get("risk_level", "").upper()
    risk_class = f"risk-{risk_level.lower()}"
    
    template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%); color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .alert-box { padding: 15px; margin: 20px 0; border-radius: 8px; }
        .risk-high { background: #fef2f2; border-left: 4px solid #f97316; }
        .risk-critical { background: #fef2f2; border-left: 4px solid #ef4444; }
        .info-row { margin: 10px 0; }
        .info-label { font-weight: bold; color: #6b7280; }
        .drivers { background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }
        .drivers li { margin: 5px 0; }
        .button { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
        .footer a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 PRISM Disease Alert</h1>
    </div>
    <div class="content">
        <div class="alert-box {{ risk_class }}">
            <h2>{{ region_name }}</h2>
            <p style="font-size: 18px; margin: 10px 0;">
                <strong>{{ risk_level }}</strong> risk level detected
            </p>
        </div>
        
        <div class="info-row">
            <span class="info-label">Disease:</span> {{ disease }}
        </div>
        <div class="info-row">
            <span class="info-label">Risk Score:</span> {{ risk_score }}
        </div>
        <div class="info-row">
            <span class="info-label">Date:</span> {{ date }}
        </div>
        
        {% if drivers %}
        <div class="drivers">
            <h3>📊 Risk Drivers</h3>
            <ul>
            {% for driver in drivers %}
                <li>{{ driver | replace("_", " ") | title }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div style="text-align: center;">
            <a href="{{ dashboard_url }}" class="button">View Full Dashboard →</a>
        </div>
    </div>
    <div class="footer">
        <p>This is an automated alert from PRISM (Predictive Risk Intelligence & Surveillance Model)</p>
        <p><a href="{{ unsubscribe_url }}">Unsubscribe from alerts</a></p>
    </div>
</body>
</html>
    """)
    
    return template.render(
        region_name=alert.get("region_id", "Unknown Region"),
        risk_level=risk_level,
        risk_class=risk_class,
        disease=alert.get("disease", "Unknown"),
        risk_score=round(alert.get("risk_score", 0), 3),
        date=alert.get("created_at", datetime.now().isoformat()),
        drivers=alert.get("drivers", []),
        dashboard_url=dashboard_url,
        unsubscribe_url=unsubscribe_url
    )


def build_alert_email_text(alert: Dict, unsubscribe_token: str) -> str:
    """
    Build plain text email content for an alert.
    
    Args:
        alert: Alert document
        unsubscribe_token: Unsubscribe token for this subscriber
        
    Returns:
        Plain text email content
    """
    settings = get_settings()
    unsubscribe_url = f"{settings.api_url}/notifications/unsubscribe?token={unsubscribe_token}"
    
    drivers_text = ""
    if alert.get("drivers"):
        drivers_text = "\n\nRisk Drivers:\n" + "\n".join(
            f"  - {d.replace('_', ' ').title()}" for d in alert["drivers"]
        )
    
    return f"""
🚨 PRISM Disease Alert

Region: {alert.get("region_id", "Unknown")}
Risk Level: {alert.get("risk_level", "UNKNOWN")}
Disease: {alert.get("disease", "Unknown")}
Risk Score: {round(alert.get("risk_score", 0), 3)}
Date: {alert.get("created_at", datetime.now().isoformat())}
{drivers_text}

View Dashboard: http://localhost:8501

---
Unsubscribe: {unsubscribe_url}
    """.strip()


def send_email(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    """
    Send an email using SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        text_content: Plain text email body
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        settings = get_settings()
        
        # Skip if SMTP not configured
        if not settings.smtp_host or settings.smtp_host == "localhost":
            logger.warning(f"SMTP not configured, skipping email to {to_email}")
            logger.info(f"[EMAIL] To: {to_email}, Subject: {subject}")
            return True  # Return True to not block the flow
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from}>"
        msg['To'] = to_email
        
        # Attach both plain text and HTML
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_user and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False


def send_alert_notification(alert: Dict, subscriber: Dict) -> bool:
    """
    Send alert notification to a single subscriber.
    
    Args:
        alert: Alert document
        subscriber: Subscriber document
        
    Returns:
        True if sent successfully
    """
    try:
        email = subscriber.get("email")
        if not email:
            return False
        
        unsubscribe_token = subscriber.get("unsubscribe_token", "")
        
        # Build email content
        subject = f"🚨 PRISM Alert: {alert.get('risk_level', 'HIGH')} Risk in {alert.get('region_id', 'Region')}"
        html_content = build_alert_email_html(alert, unsubscribe_token)
        text_content = build_alert_email_text(alert, unsubscribe_token)
        
        # Send email
        success = send_email(email, subject, html_content, text_content)
        
        if success:
            # Update last_notified_at
            db = get_db()
            db["subscribers"].update_one(
                {"_id": subscriber["_id"]},
                {"$set": {"last_notified_at": datetime.utcnow()}}
            )
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending notification for alert: {e}")
        return False


def send_alert_notifications(alerts: List[Dict]) -> int:
    """
    Send notifications for a list of alerts.
    
    Args:
        alerts: List of alert documents
        
    Returns:
        Number of notifications sent
    """
    total_sent = 0
    
    for alert in alerts:
        # Only notify for HIGH and CRITICAL alerts
        risk_level = alert.get("risk_level", "").upper()
        if risk_level not in ["HIGH", "CRITICAL"]:
            continue
        
        # Find matching subscribers
        subscribers = get_subscribers_for_alert(alert)
        
        # Filter by frequency (skip daily digest subscribers for now)
        immediate_subscribers = [s for s in subscribers if s.get("frequency") == "immediate"]
        
        # Send notifications
        for subscriber in immediate_subscribers:
            if send_alert_notification(alert, subscriber):
                total_sent += 1
    
    if total_sent > 0:
        logger.info(f"Sent {total_sent} alert notifications")
    
    return total_sent
