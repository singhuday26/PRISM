# 📧 Feature Spec: Email Notification System

> **Priority**: P0 (Critical)  
> **Estimated Effort**: 2-3 days  
> **Dependencies**: Existing alert system

---

## Overview

Enable automated email notifications when disease risk alerts are generated, with subscriber management.

---

## Requirements

### Functional
- [ ] Users can subscribe to alerts via API
- [ ] Subscribers receive emails when HIGH/CRITICAL alerts occur
- [ ] Emails contain risk summary and recommended actions
- [ ] Subscribers can filter by region and disease
- [ ] Unsubscribe link in every email
- [ ] Daily digest option (vs immediate)

### Non-Functional
- [ ] Emails delivered within 5 minutes of alert
- [ ] HTML emails with plain-text fallback
- [ ] Rate limiting to prevent spam

---

## API Endpoints

### POST /notifications/subscribe

**Request Body**:
```json
{
  "email": "user@example.com",
  "regions": ["IN-MH", "IN-KA"],
  "diseases": ["dengue", "covid"],
  "frequency": "immediate",
  "min_risk_level": "HIGH"
}
```

**Response** (201 Created):
```json
{
  "message": "Subscribed successfully",
  "subscriber_id": "sub_abc123",
  "email": "user@example.com"
}
```

### DELETE /notifications/unsubscribe

**Query Params**: `token=<unsubscribe_token>`

**Response** (200 OK):
```json
{
  "message": "Unsubscribed successfully"
}
```

### GET /notifications/preferences

**Query Params**: `email=user@example.com`

**Response** (200 OK):
```json
{
  "email": "user@example.com",
  "regions": ["IN-MH"],
  "diseases": ["dengue"],
  "frequency": "daily",
  "min_risk_level": "HIGH",
  "active": true
}
```

---

## Database Schema

### subscribers collection
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",
  "regions": ["IN-MH", "IN-KA"],
  "diseases": ["dengue"],
  "frequency": "immediate",  // "immediate" | "daily"
  "min_risk_level": "HIGH",  // "MEDIUM" | "HIGH" | "CRITICAL"
  "active": true,
  "unsubscribe_token": "uuid-token",
  "created_at": ISODate,
  "last_notified_at": ISODate
}
```

---

## Configuration

Add to `.env`:
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM=alerts@prism-health.org
SMTP_FROM_NAME=PRISM Alerts
```

Add to `backend/config.py`:
```python
class Settings(BaseSettings):
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@localhost"
    smtp_from_name: str = "PRISM"
```

---

## File Structure

```
backend/
├── routes/
│   └── notifications.py   # Subscription endpoints
├── services/
│   └── email.py           # Email sending logic
├── templates/
│   └── emails/
│       ├── alert.html     # Alert email template
│       ├── alert.txt      # Plain text version
│       ├── digest.html    # Daily digest template
│       └── welcome.html   # Subscription confirmation
```

---

## Email Templates

### Alert Email (HTML)
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .risk-high { background: #f97316; color: white; }
    .risk-critical { background: #ef4444; color: white; }
  </style>
</head>
<body>
  <h1>🚨 PRISM Alert: {{ region_name }}</h1>
  <div class="risk-{{ risk_level|lower }}">
    <strong>{{ risk_level }}</strong> risk detected
  </div>
  <p><strong>Disease:</strong> {{ disease }}</p>
  <p><strong>Risk Score:</strong> {{ risk_score }}</p>
  <p><strong>Date:</strong> {{ date }}</p>
  
  <h3>Risk Drivers</h3>
  <ul>
    {% for driver in drivers %}
    <li>{{ driver }}</li>
    {% endfor %}
  </ul>
  
  <a href="{{ dashboard_url }}">View Dashboard →</a>
  
  <hr>
  <small>
    <a href="{{ unsubscribe_url }}">Unsubscribe</a>
  </small>
</body>
</html>
```

---

## Integration with Alerts

Modify `backend/services/alerts.py`:
```python
async def generate_alerts(date, disease=None):
    alerts = []  # existing logic
    
    # NEW: Send notifications
    from backend.services.email import send_alert_notifications
    await send_alert_notifications(alerts)
    
    return alerts
```

---

## Testing

### Unit Tests
```python
# tests/unit/test_email_service.py
def test_build_alert_email():
    """Test email content generation."""

def test_subscriber_matching():
    """Test finding subscribers for an alert."""
```

### Integration Tests
```python
# tests/integration/test_notifications_api.py
def test_subscribe_creates_subscriber():
    """Test subscription endpoint."""

def test_unsubscribe_deactivates():
    """Test unsubscribe flow."""
```

---

## Acceptance Criteria

- [ ] Can subscribe via API
- [ ] Receives email when alert generated
- [ ] Email contains correct risk info
- [ ] Unsubscribe link works
- [ ] Daily digest sends once per day
- [ ] All tests pass
