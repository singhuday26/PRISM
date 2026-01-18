# 🌐 PRISM Web Interface Guide

## 🎯 Quick Access

PRISM has **two web interfaces**:

### 1. 📊 Streamlit Dashboard (Main UI)

**URL**: http://localhost:8501

**Features**:

- Interactive disease surveillance dashboard
- Multi-disease filtering
- Risk intelligence visualization
- Hotspot mapping
- Forecast viewer
- Alerts feed
- One-click pipeline execution

**Start Command**:

```bash
python run_dashboard.py
```

OR manually:

```bash
streamlit run backend/dashboard/app.py
```

---

### 2. 🔌 FastAPI Backend (API & Docs)

**URL**: http://localhost:8000

**Interactive API Docs**: http://localhost:8000/docs

**Features**:

- RESTful API endpoints
- Disease management
- Data ingestion
- Risk computation
- Forecast generation
- Interactive Swagger documentation

**Start Command**:

```bash
python -m uvicorn backend.app:app --reload
```

---

## 🚀 Complete Startup

### Option 1: Run Everything (Recommended)

Create this file: `start_prism.py`

```python
import subprocess
import sys
import time

# Start API in background
print("🔌 Starting API server...")
api = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "backend.app:app",
    "--reload"
])

# Wait for API to start
time.sleep(3)

# Start Streamlit
print("📊 Starting Streamlit dashboard...")
subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "backend/dashboard/app.py"
])
```

Then run:

```bash
python start_prism.py
```

### Option 2: Separate Terminals

**Terminal 1 - API Server**:

```bash
python -m uvicorn backend.app:app --reload
```

**Terminal 2 - Streamlit Dashboard**:

```bash
python run_dashboard.py
```

---

## 🌍 Access URLs

Once both are running:

| Service                 | URL                          | Description                   |
| ----------------------- | ---------------------------- | ----------------------------- |
| **Streamlit Dashboard** | http://localhost:8501        | Main interactive UI           |
| **API Docs (Swagger)**  | http://localhost:8000/docs   | Interactive API documentation |
| **API Redoc**           | http://localhost:8000/redoc  | Alternative API docs          |
| **API Root**            | http://localhost:8000        | Redirects to /ui/             |
| **Health Check**        | http://localhost:8000/health | API health status             |

---

## 🎨 Streamlit Dashboard Features

### Sidebar Controls

- **🦠 Disease Filter Dropdown** - Select disease to filter all views
- **🔄 One-Click Pipeline** - Run full analysis with one button
- **⚙️ API Connection Status**

### Main Sections

1. **🔥 Hotspots**
   - Top 10 regions by case count
   - Sortable data table
   - Disease-filtered

2. **⚠️ Risk Intelligence**
   - Latest risk scores for all regions
   - Color-coded severity (Low/Medium/High)
   - Downloadable CSV export

3. **🚨 Latest Alerts**
   - High-risk region notifications
   - Reason and date
   - Expandable details

4. **📈 Forecast Viewer**
   - Select region and horizon
   - Line chart visualization
   - Forecast vs historical data

5. **💾 Export Options**
   - CSV download for all data types
   - Timestamped filenames
   - Disease-specific exports

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=prism_db
API_HOST=0.0.0.0
API_PORT=8000

# For Streamlit
API_URL=http://localhost:8000
```

### Streamlit Config (Optional)

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "localhost"
headless = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

---

## 🐛 Troubleshooting

### Dashboard shows "Connection Error"

**Problem**: API not running  
**Solution**: Start API first

```bash
python -m uvicorn backend.app:app --reload
```

### "Port already in use"

**Problem**: Another service on port 8501  
**Solution**: Use different port

```bash
streamlit run backend/dashboard/app.py --server.port=8502
```

### "No module named 'streamlit'"

**Problem**: Streamlit not installed  
**Solution**: Install dependencies

```bash
pip install streamlit
# OR
pip install -r requirements.txt
```

### Dashboard loads but shows no data

**Problem**: MongoDB not running or no data loaded  
**Solution**:

1. Start MongoDB
2. Load data: `python backend/scripts/load_dengue_data.py`

---

## 📱 Access from Other Devices

### Same Network Access

1. **Find your local IP**:

   ```bash
   # Windows
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

2. **Start with network binding**:

   ```bash
   # API
   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

   # Streamlit
   streamlit run backend/dashboard/app.py --server.address=0.0.0.0
   ```

3. **Access from other device**:
   - Dashboard: http://192.168.1.100:8501
   - API: http://192.168.1.100:8000

### Update API_URL in Dashboard

If API is on different host, set environment variable:

```bash
# Windows
set API_URL=http://192.168.1.100:8000

# Linux/Mac
export API_URL=http://192.168.1.100:8000

# Then run dashboard
streamlit run backend/dashboard/app.py
```

---

## 🎯 Quick Test

After starting both services:

1. **Check API**: Visit http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **Check Dashboard**: Visit http://localhost:8501
   - Should show PRISM dashboard with disease dropdown

3. **Test Disease Filter**:
   - Select a disease from dropdown
   - All sections should update automatically

4. **Test Pipeline**:
   - Click "Run Full Pipeline" button
   - Watch progress in real-time

---

## 🌟 Pro Tips

1. **Keep API running** - Dashboard depends on it
2. **Use disease filter** - Narrows down data for faster loading
3. **Export data** - Download CSV for offline analysis
4. **Monitor logs** - Both terminals show useful debug info
5. **Refresh strategically** - Use browser refresh if data seems stale

---

## 📊 Default Ports

- **Streamlit Dashboard**: 8501
- **FastAPI Backend**: 8000
- **MongoDB**: 27017

Make sure these ports are available!

---

## 🎨 Customizing the Dashboard

Edit `backend/dashboard/app.py` to:

- Add new visualizations
- Modify color schemes
- Add custom metrics
- Create new pages

Streamlit auto-reloads on file changes! 🔄

---

## 📚 Related Documentation

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../QUICKSTART.md) - Getting started guide
- [MULTI_DISEASE_GUIDE.md](docs/MULTI_DISEASE_GUIDE.md) - Multi-disease features

---

## ✅ Checklist

Before accessing the dashboard:

- [ ] MongoDB is running
- [ ] Data is loaded (at least one disease)
- [ ] API server is running (port 8000)
- [ ] Streamlit is running (port 8501)
- [ ] Browser is open to http://localhost:8501

---

**Happy Monitoring!** 🎉

Your PRISM dashboard is now accessible at **http://localhost:8501**
