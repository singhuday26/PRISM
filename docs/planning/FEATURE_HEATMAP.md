# 🗺️ Feature Spec: Interactive Risk Heatmap

> **Priority**: P0 (Critical)  
> **Estimated Effort**: 3-5 days  
> **Dependencies**: Existing risk scoring system

---

## Overview

Replace basic Streamlit risk visualization with an interactive geographic heatmap that shows real-time disease risk levels across regions.

---

## Requirements

### Functional
- [ ] Display world/country map with region boundaries
- [ ] Color-code regions by risk level (4 colors)
- [ ] Click region to see detailed risk information
- [ ] Time slider to view historical risk data
- [ ] Filter by disease type
- [ ] Legend showing risk level meanings
- [ ] Responsive on desktop and tablet

### Non-Functional
- [ ] Load time < 2 seconds for 100 regions
- [ ] Smooth animations on hover/click
- [ ] Works in Chrome, Firefox, Edge

---

## API Endpoints

### GET /risk/geojson

Returns risk scores formatted as GeoJSON for map rendering.

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| date | string | No | today | Date for risk scores (YYYY-MM-DD) |
| disease | string | No | all | Filter by disease |

**Response** (200 OK):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "region_id": "IN-MH",
        "region_name": "Maharashtra",
        "risk_score": 0.75,
        "risk_level": "HIGH",
        "disease": "dengue",
        "date": "2024-01-15",
        "drivers": ["increasing_cases", "monsoon"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...], ...]]
      }
    }
  ],
  "metadata": {
    "date": "2024-01-15",
    "disease": "dengue",
    "count": 35
  }
}
```

### GET /regions/boundaries

Returns region boundary polygons (cached, rarely changes).

**Response** (200 OK):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "region_id": "IN-MH",
        "region_name": "Maharashtra"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[72.6, 15.6], [72.9, 15.8], ...]]
      }
    }
  ]
}
```

---

## Frontend Implementation

### Technology
- **Leaflet.js** (open-source, lightweight)
- Vanilla JS (no framework needed for MVP)
- Served as static file by FastAPI

### File Structure
```
frontend/
├── heatmap/
│   ├── index.html      # Main heatmap page
│   ├── heatmap.js      # Map logic
│   ├── heatmap.css     # Styles
│   └── legend.js       # Legend component
```

### Color Scheme
| Risk Level | Score Range | Color | Hex |
|------------|-------------|-------|-----|
| LOW | 0.0 - 0.3 | Green | #22c55e |
| MEDIUM | 0.3 - 0.5 | Yellow | #eab308 |
| HIGH | 0.5 - 0.7 | Orange | #f97316 |
| CRITICAL | 0.7 - 1.0 | Red | #ef4444 |

### Popup Content
On region click, show:
```
┌─────────────────────────┐
│ Maharashtra             │
│ ─────────────────────── │
│ Risk Score: 0.75 (HIGH) │
│ Disease: Dengue         │
│ Date: Jan 15, 2024      │
│                         │
│ Risk Drivers:           │
│ • Increasing cases      │
│ • Monsoon season        │
│                         │
│ [View Details →]        │
└─────────────────────────┘
```

---

## Backend Implementation

### New Files
```
backend/
├── routes/
│   └── geojson.py       # GeoJSON endpoints
├── schemas/
│   └── geojson.py       # GeoJSON Pydantic models
└── services/
    └── geojson.py       # GeoJSON transformation logic
```

### Database Changes
Add `geometry` field to regions collection:
```javascript
// regions collection update
{
  "region_id": "IN-MH",
  "region_name": "Maharashtra",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[72.6, 15.6], ...]]
  }
}
```

### Data Source for Boundaries
- Use Natural Earth Data (public domain)
- Or simplified GeoJSON from geojson-maps repository
- Store in MongoDB or as static JSON file

---

## Testing

### Unit Tests
```python
# tests/unit/test_geojson_service.py
def test_risk_to_geojson_feature():
    """Test conversion of risk score to GeoJSON feature."""
    
def test_geojson_color_mapping():
    """Test risk level to color mapping."""
```

### Integration Tests
```python
# tests/integration/test_geojson_api.py
def test_get_geojson_returns_feature_collection():
    """Test /risk/geojson returns valid GeoJSON."""
    
def test_geojson_filters_by_disease():
    """Test disease query parameter filtering."""
```

### Manual Testing
1. Start API: `python -m uvicorn backend.app:app --reload`
2. Open: `http://localhost:8000/heatmap/`
3. Verify map loads with colored regions
4. Click a region and verify popup
5. Change date slider and verify colors update
6. Filter by disease and verify

---

## Acceptance Criteria

- [ ] Map displays on page load
- [ ] Regions are color-coded correctly
- [ ] Clicking a region shows risk details
- [ ] Date slider changes displayed data
- [ ] Disease filter works
- [ ] All tests pass
- [ ] Works on Chrome and Firefox
