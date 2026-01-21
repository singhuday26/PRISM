# 🖥️ Feature Spec: PRISM Command Dashboard

> **Priority**: P0 (Product A Core)
> **Audience**: Health Authorities / Admins
> **Tech Stack**: React + Vite + Tailwind CSS + Shadcn UI

---

## 1. Design Philosophy: "Mission Control"
This is **NOT** a data exploration tool. It is an **Operational Dashboard**.
- **Dark Mode Default**: Reduces eye strain in 24/7 command centers.
- **High Contrast Alerts**: Problems must scream. Status quo should be quiet.
- **Density**: High information density, organized by urgency.

## 2. Page Layout Strategy

```
┌─────────────────┬──────────────────────────────────────────────────┐
│  PRISM COMMAND  │  [🚨 ALERT: Bed Shortage in Zone 4]      👤 Admin│
├─────────────────┼──────────────────────┬───────────────────────────┤
│  [Dashboard]    │  **CRITICAL METRICS**│  **OPERATIONAL MAP**      │
│  [Analysis]     │ ┌──────────────────┐ │                           │
│  [Resources]    │ │ 🏥 Bed Gap: -15  │ │  [Map View]               │
│  [Reports]      │ │ 🔴 ICU: 98% Full │ │  • Red Pins: Outbreaks    │
│  [Settings]     │ │ 📉 O2: 3 Days    │ │  • Blue Pins: Hospitals   │
│                 │ └──────────────────┘ │                           │
│                 ├──────────────────────┤                           │
│                 │  **ACTION FEED**     │                           │
│                 │  [10:00] Verify O2   │                           │
│                 │  [09:30] Deploy Team │                           │
└─────────────────┴──────────────────────┴───────────────────────────┘
```

## 3. Key Widgets & Data Sources

### A. Resource Gap Cards (The "Why")
*Displays the output of our `ResourceService`.*
- **Data**: `GET /resources/predict`
- **Visual**: Big Number + Trend Arrow.
- **Logic**: If `demand > capacity`, color = **RED**. Else **GREEN**.

### B. The Operational Map (The "Where")
*Visualizes the battlefield.*
- **Data**: `GET /risk/geojson` (Heatmap) + Hospital Locations (Static/DB).
- **Interactivity**: Clicking a region filters the "Resource Gap" cards to that region.
- **Tech**: `react-leaflet` with custom map layer.

### C. Alert Feed (The "When")
*Real-time situational awareness.*
- **Data**: `GET /alerts/latest`
- **Actions**: "Acknowledge", "Escalate".

## 4. Technology Choices for "Massive Scale"

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Framework** | **React + Vite** | Industry standard, massive ecosystem, high performance. |
| **UI Library** | **Shadcn UI** | Professional "Vercel-like" aesthetic, accessible, copy-paste code. |
| **State** | **TanStack Query** | Caching, easy API integration, loading states. |
| **Charts** | **Recharts** | Composable, responsive, React-native. |
| **Maps** | **React Leaflet** | Lightweight, sufficient for 2D geospatial. |

## 5. Development Roadmap

1.  **Scaffold**: `npm create vite@latest frontend -- --template react-ts`
2.  **The Shell**: Implement Sidebar + Header Layout.
3.  **API Client**: Setup Axios + TanStack Query hooks for our `resources` API.
4.  **Widget 1**: Build the "Bed Shortage" Card (connects to backend we just built).
5.  **Widget 2**: Build the Map.

---

## 6. Verification Criteria
- [ ] Dashboard loads in < 2 seconds.
- [ ] "Bed Gap" updates immediately when Region is changed.
- [ ] Mobile responsive (Health officers use tablets).
