# 🚀 PRISM Quick Start Guide

Follow these steps to quickly start the project locally and verify the system.

### Option 1: One-Command Startup (Recommended)
This script will automatically start MongoDB (if local), the API server, and the Streamlit dashboard all in one terminal window.

```bash
# 1. Activate your environment
.venv\Scripts\activate

# 2. Run the start script
python scripts/start_prism.py
```
*   **React Frontend**: [http://localhost:8000](http://localhost:8000)
*   **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Manual Startup (For Development)

If you want to run the frontend in development mode (with Hot Module Replacement):

#### Terminal 1: Backend API
```bash
.venv\Scripts\activate
uvicorn backend.app:app --reload
```

#### Terminal 2: React Frontend
```bash
cd frontend
npm install   # Only needed once
npm run dev
```
*   Visit: [http://localhost:5173](http://localhost:5173)

---

### ✅ Self-Check Checklist

1.  [ ] **Environment**: Is your `.env` file created with a valid `MONGO_URI`?
2.  [ ] **Data**: Have you seeded the sample data? (`python -m backend.scripts.seed`)
3.  [ ] **Health**: Visit [http://localhost:8000/health](http://localhost:8000/health) — it should return "status": "ok".
4.  [ ] **Map**: Open the Frontend and verify if the heatmap loads.

---

### 🛑 Troubleshooting
*   **Port 8000 Busy**: Run `taskkill /IM uvicorn.exe /F` or use a different port.
*   **Module Not Found**: Ensure you are running commands from the **root directory** (`PRISM/`) and your virtual environment is active.
