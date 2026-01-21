# PRISM - Faculty Review Presentation
## NoSQL Course Project Review

---

# 1. What is PRISM?

**PRISM** = **P**redictive **R**isk **I**ntelligence & **S**urveillance **M**odel

> An open-source disease outbreak prediction and surveillance platform.

### The Problem
- Disease outbreaks kill millions (COVID: 7M+ deaths)
- Enterprise tools like **BlueDot** detected COVID 9 days before WHO — but cost $100K+
- Local health departments, NGOs, developing nations have **no access** to predictive tools

### Our Solution
**"BlueDot for the rest of us"** — democratizing epidemic intelligence through open-source technology.

---

# 2. Why MongoDB? (NoSQL Justification)

## Data Characteristics

| Aspect | Why NoSQL Wins |
|--------|----------------|
| **Schema Flexibility** | Disease data varies by source (WHO vs local CSV vs news) |
| **Nested Documents** | Risk scores with embedded climate info, drivers arrays |
| **Time-Series Data** | Daily cases, forecasts — document model fits naturally |
| **Geospatial** | Built-in GeoJSON support for heatmaps |
| **Horizontal Scaling** | Health crises = data spikes (COVID: billions of records) |

## Our Collections

```javascript
// Dynamic schema for multi-disease support
{
  "region_id": "IN-MH",
  "disease": "dengue",        // Varies per document
  "confirmed": 150,
  "climate_info": {           // Embedded document
    "season": "monsoon",
    "multiplier": 1.5
  },
  "drivers": ["increasing_cases", "monsoon"]  // Flexible array
}
```

**Why NOT SQL?**
- Fixed schema would require ALTER TABLE for each new disease
- Nested climate_info would need JOINs (slower)
- Arrays would need junction tables

---

# 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    CLIENTS                          │
│  [Streamlit Dashboard]  [REST API]  [Future: React] │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│              FastAPI Backend (Python)               │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐          │
│  │   Risk   │ │  Alert   │ │  Forecast  │          │
│  │ Service  │ │ Service  │ │  (ARIMA)   │          │
│  └────┬─────┘ └────┬─────┘ └─────┬──────┘          │
└───────┼────────────┼─────────────┼──────────────────┘
        │            │             │
┌───────▼────────────▼─────────────▼──────────────────┐
│                  MongoDB                            │
│  ┌─────────┐ ┌───────────┐ ┌────────────┐          │
│  │ regions │ │cases_daily│ │risk_scores │          │
│  └─────────┘ └───────────┘ └────────────┘          │
│  ┌─────────┐ ┌───────────┐                         │
│  │ alerts  │ │ forecasts │                         │
│  └─────────┘ └───────────┘                         │
└─────────────────────────────────────────────────────┘
```

---

# 4. Current Implementation Status

| Component | Status | Details |
|-----------|--------|---------|
| **MongoDB Integration** | ✅ Done | Connection pooling, indexes, CRUD |
| **Risk Scoring** | ✅ Done | With climate boost multipliers |
| **Alert Generation** | ✅ Done | Threshold-based triggering |
| **ARIMA Forecasting** | ✅ Done | 7-day prediction horizon |
| **Multi-Disease** | ✅ Done | Dengue, COVID, configurable |
| **REST API** | ✅ Done | FastAPI with Swagger docs |
| **Dashboard** | ✅ Done | Streamlit (basic) |
| **Testing** | ✅ Done | pytest unit + integration |

### MongoDB Features Used
- **Indexes**: Compound indexes on (region_id, date)
- **Aggregation Pipeline**: For hotspot detection, analytics
- **Upserts**: Idempotent data ingestion
- **TTL Indexes**: Auto-expire old forecasts (planned)

---

# 5. Live Demo Points

**Show these in your review:**

1. **API Swagger UI**: `http://localhost:8000/docs`
   - Show the endpoints structure
   - Execute `/health/` to show MongoDB connection

2. **MongoDB Collections**: Show in Compass
   - `cases_daily` — time-series documents
   - `risk_scores` — nested climate_info

3. **Risk Computation Flow**:
   ```
   POST /risk/compute?date=2024-01-15
   → Reads cases_daily (aggregation)
   → Applies climate multiplier
   → Writes to risk_scores
   → Returns JSON response
   ```

4. **Dashboard**: `http://localhost:8501`
   - Show visualizations reading from MongoDB

---

# 6. Roadmap to Viability

## Phase 1: MVP Complete ✅ (Now)
- Core risk scoring
- Basic forecasting
- API + Dashboard

## Phase 2: Differentiation (Next 2 Months)
| Feature | MongoDB Usage |
|---------|---------------|
| **Interactive Heatmap** | GeoJSON queries, geospatial indexes |
| **PDF Reports** | Aggregation for summaries |
| **Email Notifications** | New `subscribers` collection |

## Phase 3: Intelligence (3-6 Months)
| Feature | MongoDB Usage |
|---------|---------------|
| **News Ingestion** | Text search, NLP signals collection |
| **Enhanced ML** | Model performance tracking collection |
| **LLM Insights** | RAG with MongoDB Atlas Vector Search |

## Phase 4: Scale (6-12 Months)
- MongoDB Atlas deployment
- Multi-tenant (sharding by organization)
- Real-time with Change Streams

---

# 7. Competitive Advantage

| Platform | Access | Cost | Open-Source |
|----------|--------|------|-------------|
| **BlueDot** | Enterprise | $$$$ | ❌ |
| **HealthMap** | Public | Free | Partial |
| **PRISM** | Self-host | **Free** | **✅ Yes** |

### Our Unique Position
- **Affordable**: Free, self-hostable
- **Extensible**: Python ecosystem
- **Transparent**: Open-source, auditable
- **Modern**: FastAPI, MongoDB, React (coming)

---

# 8. Technical Highlights for NoSQL Faculty

### Query Examples

**Aggregation - Find Hotspots:**
```javascript
db.cases_daily.aggregate([
  { $match: { disease: "dengue" } },
  { $group: { 
      _id: "$region_id", 
      total: { $sum: "$confirmed" } 
  }},
  { $sort: { total: -1 } },
  { $limit: 5 }
])
```

**Geospatial - Nearby Regions:**
```javascript
db.regions.find({
  geometry: {
    $near: {
      $geometry: { type: "Point", coordinates: [72.8, 19.0] },
      $maxDistance: 100000
    }
  }
})
```

**Schema Flexibility:**
```javascript
// Dengue has climate info
{ disease: "dengue", climate_info: { season: "monsoon" } }

// COVID has variant info
{ disease: "covid", variant: "omicron", vaccine_coverage: 0.65 }
```

---

# 9. Questions Faculty May Ask

| Question | Answer |
|----------|--------|
| **Why not PostgreSQL?** | Schema flexibility for multi-disease, embedded documents, native GeoJSON, horizontal scaling for crisis data spikes |
| **How do you handle consistency?** | Single document atomicity sufficient for our use case; no cross-document transactions needed |
| **Scaling plan?** | MongoDB Atlas with sharding by region_id for geographic distribution |
| **Backup strategy?** | mongodump daily + Atlas continuous backup (planned) |

---

# 10. Summary

> **PRISM democratizes epidemic intelligence using MongoDB's flexibility to track any disease, anywhere, with predictive analytics.**

### Key Takeaways
1. ✅ MongoDB chosen for schema flexibility, geospatial, scaling
2. ✅ Working MVP with risk scoring, forecasting, alerts
3. ✅ Clear roadmap to production viability
4. ✅ Open-source positioning against $100K+ competitors

---

*Prepared for NoSQL Faculty Review - January 22, 2026*
