# 🤖 PRISM AI Agent Prompts

> Copy-paste these prompts when starting a new AI agent session to provide rich context for PRISM development.

---

## Quick Context Injection

Use this at the start of any PRISM development session:

```
I'm building PRISM (Predictive Risk Intelligence & Surveillance Model) - an open-source disease surveillance platform.

**Location**: C:\0001_Project\PRISM
**Stack**: FastAPI + MongoDB + Streamlit + Python 3.9+

**Key Files**:
- Main app: backend/app.py
- Config: backend/config.py  
- Exceptions: backend/exceptions.py
- Response schemas: backend/schemas/responses.py
- Tests: tests/unit/ and tests/integration/

**Current Features**: Risk scoring, alerts, ARIMA forecasting, multi-disease support
**Run Tests**: pytest
**Start API**: python -m uvicorn backend.app:app --reload
```

---

## Feature Implementation Prompts

### P0: Interactive Risk Heatmap

```
In PRISM (C:\0001_Project\PRISM), implement an interactive risk heatmap.

Requirements:
1. Create a new route GET /risk/geojson that returns risk scores as GeoJSON
2. Build an HTML page with Leaflet.js showing a map
3. Color-code regions by risk level (green/yellow/orange/red)
4. Add click handlers to show region details
5. Add a time slider for historical data

Technical constraints:
- Use existing risk_scores collection in MongoDB
- Follow patterns in backend/routes/risk.py
- Add response model in backend/schemas/responses.py
- Write tests in tests/integration/

Serve the HTML via FastAPI static files or as a new Streamlit page.
```

### P0: Email Notifications

```
In PRISM (C:\0001_Project\PRISM), add email notification support.

Requirements:
1. Add SMTP configuration to backend/config.py
2. Create backend/services/email.py for sending emails
3. Create subscriber management endpoints:
   - POST /notifications/subscribe
   - DELETE /notifications/unsubscribe  
   - GET /notifications/preferences
4. Create MongoDB collection 'subscribers'
5. Trigger emails when alerts are generated (modify backend/services/alerts.py)

Use fastapi-mail or aiosmtplib. Create HTML email templates in backend/templates/.
Add to requirements.txt as needed.
```

### P0: PDF Report Generation

```
In PRISM (C:\0001_Project\PRISM), implement PDF report generation.

Requirements:
1. Create backend/services/reports.py
2. Add endpoints:
   - POST /reports/generate (params: region_id, disease, period)
   - GET /reports/{report_id}
   - GET /reports/list
3. Use weasyprint or reportlab for PDF generation
4. Create Jinja2 templates in backend/templates/reports/
5. Store reports in 'reports' MongoDB collection with file paths

Reports should include: risk summary, case trends chart, alert history, forecast.
```

---

## Code Quality Requirements

Include these expectations in prompts:

```
Code Quality Requirements:
- Use custom exceptions from backend/exceptions.py
- Add Pydantic response models to backend/schemas/responses.py
- Write unit tests in tests/unit/
- Write integration tests in tests/integration/
- Follow existing code patterns in the codebase
- Run pytest before considering complete
```

---

## Verification Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Type checking (if mypy configured)
mypy backend/

# Start and test API manually
python -m uvicorn backend.app:app --reload
# Then visit http://localhost:8000/docs
```
