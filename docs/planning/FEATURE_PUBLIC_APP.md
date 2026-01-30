# 📱 Feature Spec: PRISM Public ("The Health Weather App")

> **Priority**: P2 (Product B Core)
> **Audience**: Citizens / General Public
> **Goal**: "Is it safe to go out today?"

---

## 1. Design Philosophy
**Simplicity > Detail.** 
Citizens don't care about "Incidence Rate per 100k". They care about **Safety**.
- **Interface**: Visual, colorful, big text.
- **Analogy**: Like a Weather App (AQI), but for Disease.

## 2. Key Features

### A. The "Risk Card" (Hero)
*The first thing they see.*
- **Visual**: Big Circle with Color (Green/Amber/Red).
- **Text**: "Medium Risk" (calculated from our customized `ResourceService` logic, normalized).
- **Subtext**: "Dengue cases are rising in [Your Location]."

### B. Actionable Advice
*What should I do?*
- Dynamic checklist based on risk level.
- **Green**: "Safe to go out. Keep water clean."
- **Red**: "Use repellent. Avoid dusk outdoor activities."

### C. Community Pulse
*Engagement loop.*
- "Verify Risk": User can click "I see mosquitos" (simulated for now).

## 3. Technology Stack: PWA
We don't need a separate native app. We'll build a **Progressive Web App (PWA)** inside the existing React codebase.

- **Route**: `/public` (separate layout from `/admin`).
- **Mobile First**: CSS Grid optimized for vertical screens.
- **Geolocation**: Uses browser API to fetch `region_id` automatically.

---

## 4. API Requirements (Reusing Core)

We need one new specialized endpoint for public consumption (lite payload):

`GET /public/risk-check?lat=19.0&long=72.8`

**Response:**
```json
{
  "region": "Mumbai Suburban",
  "overall_risk_level": "HIGH",
  "aqi": 145,
  "top_threat": {
    "disease": "Dengue",
    "trend": "rising"
  },
  "advice": [
    "Wear long sleeves",
    "Empty flower pots"
  ]
}
```

## 5. Development Roadmap

1.  **Frontend**: Create `PublicLayout.tsx` (Mobile container).
2.  **Location Service**: Map GPS coords to our `region_id`.
3.  **Advice Engine**: Simple mapping of `Risk Score -> String List`.
