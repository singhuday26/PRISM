# 📄 Feature Spec: PDF Report Generation

> **Priority**: P0 (Critical)  
> **Estimated Effort**: 2-3 days  
> **Dependencies**: Risk scores, alerts, forecasts

---

## Overview

Generate downloadable PDF reports summarizing outbreak status, risk levels, and forecasts for specific regions and time periods.

---

## Requirements

### Functional
- [ ] Generate weekly summary reports
- [ ] Generate region-specific reports
- [ ] Include risk trends chart
- [ ] Include alert history table
- [ ] Include forecast visualization
- [ ] Download as PDF

### Report Types
| Type | Description |
|------|-------------|
| `weekly_summary` | All regions, past 7 days |
| `region_detail` | Single region, configurable period |
| `disease_overview` | Single disease, all regions |

---

## API Endpoints

### POST /reports/generate

**Request Body**:
```json
{
  "type": "region_detail",
  "region_id": "IN-MH",
  "disease": "dengue",
  "period_start": "2024-01-01",
  "period_end": "2024-01-15"
}
```

**Response** (202 Accepted):
```json
{
  "report_id": "rpt_abc123",
  "status": "generating",
  "estimated_time_seconds": 10
}
```

### GET /reports/{report_id}

**Response** (200 OK - JSON):
```json
{
  "report_id": "rpt_abc123",
  "type": "region_detail",
  "status": "ready",
  "download_url": "/reports/rpt_abc123/download",
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### GET /reports/{report_id}/download

**Response**: PDF file download

### GET /reports/list

**Query Params**: `region_id`, `disease`, `limit`

**Response** (200 OK):
```json
{
  "reports": [
    {
      "report_id": "rpt_abc123",
      "type": "region_detail",
      "region_id": "IN-MH",
      "generated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

## Report Content Structure

### Weekly Summary Report
```
┌─────────────────────────────────────┐
│ PRISM Weekly Summary                │
│ January 8-15, 2024                  │
├─────────────────────────────────────┤
│ Executive Summary                   │
│ • 5 HIGH risk regions               │
│ • 12 new alerts generated           │
│ • Dengue trending up 15%            │
├─────────────────────────────────────┤
│ Risk Heatmap (static image)         │
│ [Map visualization]                 │
├─────────────────────────────────────┤
│ Top Risk Regions                    │
│ ┌─────────┬───────┬────────┐        │
│ │ Region  │ Score │ Level  │        │
│ ├─────────┼───────┼────────┤        │
│ │ Mumbai  │ 0.85  │ CRIT   │        │
│ │ Delhi   │ 0.72  │ HIGH   │        │
│ └─────────┴───────┴────────┘        │
├─────────────────────────────────────┤
│ 7-Day Forecast                      │
│ [Line chart]                        │
├─────────────────────────────────────┤
│ Alerts Issued                       │
│ [Table of alerts]                   │
└─────────────────────────────────────┘
```

---

## Technical Approach

### PDF Generation
Use **weasyprint** (HTML/CSS to PDF):
```python
from weasyprint import HTML

def generate_pdf(template_name, context):
    html = render_template(template_name, **context)
    pdf = HTML(string=html).write_pdf()
    return pdf
```

### Chart Generation
Use **matplotlib** or **plotly** for static charts:
```python
import matplotlib.pyplot as plt

def create_risk_trend_chart(data):
    fig, ax = plt.subplots()
    ax.plot(data['dates'], data['scores'])
    # Save to BytesIO, embed in HTML as base64
```

---

## File Structure

```
backend/
├── routes/
│   └── reports.py           # Report endpoints
├── services/
│   └── reports.py           # Report generation logic
├── templates/
│   └── reports/
│       ├── base.html        # Common layout
│       ├── weekly.html      # Weekly summary
│       ├── region.html      # Region detail
│       └── styles.css       # PDF styles
└── generated_reports/       # Store generated PDFs
```

---

## Database Schema

### reports collection
```javascript
{
  "_id": ObjectId,
  "report_id": "rpt_abc123",
  "type": "region_detail",
  "region_id": "IN-MH",
  "disease": "dengue",
  "period_start": ISODate,
  "period_end": ISODate,
  "status": "ready",  // "generating" | "ready" | "failed"
  "file_path": "generated_reports/2024/01/rpt_abc123.pdf",
  "file_size_bytes": 125000,
  "generated_at": ISODate,
  "error": null
}
```

---

## Dependencies

Add to `requirements.txt`:
```
weasyprint>=60.0
matplotlib>=3.8.0
Jinja2>=3.1.0
```

---

## Acceptance Criteria

- [ ] Can request report generation via API
- [ ] Report generates within 30 seconds
- [ ] PDF downloads correctly
- [ ] Report contains charts and tables
- [ ] List endpoint shows past reports
- [ ] All tests pass
