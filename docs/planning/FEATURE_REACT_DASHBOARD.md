# ⚛️ Feature Spec: Modern React Dashboard

> **Priority**: P1 (High)  
> **Estimated Effort**: 2-3 weeks  
> **Dependencies**: P0 features (heatmap, reports)

---

## Overview

Replace Streamlit dashboard with a production-grade React SPA featuring real-time updates, modern UI, and mobile responsiveness.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 + Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Maps | Leaflet + react-leaflet |
| State | React Query (TanStack) |
| Routing | React Router v6 |
| Icons | Lucide React |

---

## Page Structure

```
/                    → Dashboard (overview cards + mini charts)
/risk                → Risk heatmap (full page map)
/risk/:regionId      → Region detail view
/alerts              → Alert list + filters
/forecasts           → Forecast charts by region
/reports             → Report list + generate new
/settings            → Configuration (optional)
```

---

## Component Hierarchy

```
App
├── Layout
│   ├── Sidebar (navigation)
│   ├── Header (search, notifications, user)
│   └── Main
│       └── [Page Content]
├── Pages
│   ├── Dashboard
│   │   ├── StatsCards (risk count, alerts, regions)
│   │   ├── MiniHeatmap
│   │   ├── RecentAlerts
│   │   └── TrendChart
│   ├── RiskMap
│   │   ├── MapContainer
│   │   ├── RegionPopup
│   │   ├── DateSlider
│   │   └── DiseaseFilter
│   ├── Alerts
│   │   ├── AlertFilters
│   │   └── AlertTable
│   ├── Forecasts
│   │   ├── RegionSelector
│   │   └── ForecastChart
│   └── Reports
│       ├── ReportList
│       └── GenerateModal
└── Shared
    ├── Card
    ├── Button
    ├── Select
    ├── DatePicker
    └── LoadingSpinner
```

---

## Key Features

### Dashboard Home
- 4 stat cards: Total Regions, High Risk Count, Active Alerts, Forecast Accuracy
- Mini heatmap (clickable to full map)
- Recent alerts list (last 5)
- 7-day trend sparklines

### Risk Heatmap
- Full-screen Leaflet map
- Color-coded regions
- Click for details popup
- Date range selector
- Disease dropdown filter
- Download as image

### Alerts Page
- Filterable table (date, region, disease, risk level)
- Sort by risk score
- Bulk acknowledge
- Export to CSV

### Forecasts Page
- Region selector dropdown
- Line chart with confidence intervals
- Compare actual vs predicted
- Multiple disease overlay

---

## API Integration

Use React Query for data fetching:

```typescript
// hooks/useRiskScores.ts
export function useRiskScores(date: string, disease?: string) {
  return useQuery({
    queryKey: ['risk', date, disease],
    queryFn: () => api.get(`/risk/latest?date=${date}&disease=${disease}`),
    staleTime: 60_000, // 1 minute
  });
}
```

### Required Endpoints
All existing PRISM endpoints + `/risk/geojson` from P0.

---

## File Structure

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   └── client.ts       # Axios/fetch wrapper
│   ├── components/
│   │   ├── layout/
│   │   ├── shared/
│   │   └── charts/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── RiskMap.tsx
│   │   ├── Alerts.tsx
│   │   └── Forecasts.tsx
│   ├── hooks/
│   │   ├── useRiskScores.ts
│   │   └── useAlerts.ts
│   └── styles/
│       └── globals.css
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Design Requirements

### Colors
| Purpose | Light | Dark |
|---------|-------|------|
| Background | #f8fafc | #0f172a |
| Card | #ffffff | #1e293b |
| Primary | #3b82f6 | #60a5fa |
| Risk Low | #22c55e | #4ade80 |
| Risk Medium | #eab308 | #facc15 |
| Risk High | #f97316 | #fb923c |
| Risk Critical | #ef4444 | #f87171 |

### Responsive Breakpoints
- Mobile: < 640px (single column, hamburger nav)
- Tablet: 640-1024px (collapsible sidebar)
- Desktop: > 1024px (full sidebar)

---

## Setup Commands

```bash
# Initialize project
cd C:\0001_Project\PRISM
npx -y create-vite@latest frontend-react --template react-ts
cd frontend-react
npm install

# Add dependencies
npm install @tanstack/react-query react-router-dom recharts leaflet react-leaflet lucide-react
npm install -D tailwindcss postcss autoprefixer @types/leaflet
npx tailwindcss init -p
```

---

## Acceptance Criteria

- [ ] Dashboard loads with stats cards
- [ ] Risk map displays colored regions
- [ ] Alerts table filters and sorts
- [ ] Forecasts chart renders
- [ ] Dark/light mode toggle
- [ ] Mobile responsive
- [ ] API errors handled gracefully
- [ ] Loading states shown
