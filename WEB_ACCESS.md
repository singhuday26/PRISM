# 🌐 PRISM Web Access - Quick Reference

## 🚀 Start PRISM

### One-Command Start (Easiest)
```bash
python start_prism.py
```

This automatically starts:
- ✅ API Server on port 8000
- ✅ Streamlit Dashboard on port 8501

---

## 🌍 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **📊 Dashboard** | **http://localhost:8501** | **Main interactive interface** |
| **🔌 API Docs** | http://localhost:8000/docs | Swagger API documentation |
| **📖 ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **⚕️ Health** | http://localhost:8000/health | API health check |

---

## 🎯 What to Do First

1. **Visit Dashboard**: http://localhost:8501
   - Interactive disease surveillance interface
   - Multi-disease filtering
   - Visual analytics

2. **Select a Disease**: Use dropdown in sidebar
   - Choose from 10 pre-configured diseases
   - Or select "All Diseases"

3. **Explore Features**:
   - 🔥 View hotspots
   - ⚠️ Check risk scores
   - 🚨 See alerts
   - 📈 View forecasts
   - 💾 Export data

---

## 🛠️ Prerequisites

Make sure you have:
- ✅ Python 3.9+ installed
- ✅ MongoDB running
- ✅ Dependencies installed: `pip install -r requirements.txt`
- ✅ Environment configured: `.env` file exists

---

## 🔧 Alternative Start Methods

### Method 1: Run Dashboard Only
```bash
python run_dashboard.py
```
Opens: http://localhost:8501

### Method 2: Run API Only
```bash
python -m uvicorn backend.app:app --reload
```
Opens: http://localhost:8000

### Method 3: Manual Streamlit
```bash
streamlit run backend/dashboard/app.py
```

---

## 📱 Access from Other Devices

### On Same Network

1. **Find your IP address**:
   ```bash
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

2. **Start with network access**:
   ```bash
   # API
   python -m uvicorn backend.app:app --host 0.0.0.0
   
   # Dashboard
   streamlit run backend/dashboard/app.py --server.address 0.0.0.0
   ```

3. **Access from phone/tablet**:
   - http://YOUR_IP:8501 (Dashboard)
   - http://YOUR_IP:8000 (API)

---

## 🐛 Troubleshooting

### "Connection refused" in Dashboard
**Problem**: API not running  
**Solution**: Start API first
```bash
python -m uvicorn backend.app:app --reload
```

### "Port already in use"
**Problem**: Service already running  
**Solution**: Stop existing service or use different port
```bash
streamlit run backend/dashboard/app.py --server.port 8502
```

### "ModuleNotFoundError: No module named 'streamlit'"
**Problem**: Dependencies not installed  
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Dashboard loads but no data
**Problem**: MongoDB not running or empty database  
**Solution**: 
1. Start MongoDB
2. Load data: `python disease_manager.py load DENGUE Datasets/...`

---

## 📊 Dashboard Features

### Sidebar
- 🦠 **Disease Filter** - Select which disease to view
- 🔄 **Run Pipeline** - One-click full analysis
- ⚙️ **API Status** - Connection indicator

### Main Sections
1. **Hotspots** - Top regions by case count
2. **Risk Intelligence** - Latest risk scores
3. **Alerts** - High-risk notifications
4. **Forecast Viewer** - Predictive analytics
5. **Data Export** - Download CSV reports

---

## 🎨 Customize Dashboard

Edit `backend/dashboard/app.py` to:
- Change visualizations
- Add new metrics
- Modify layout
- Create custom pages

Streamlit auto-reloads on save! 🔄

---

## 🔐 Security Note

Default configuration:
- API accepts all origins (CORS: *)
- Dashboard on localhost only

For production, update:
- Set `CORS_ORIGINS` in `.env`
- Use proper authentication
- Enable HTTPS

See [SECURITY.md](../SECURITY.md) for details.

---

## 📚 More Information

- **Full Guide**: [Web Interface Guide](WEB_INTERFACE_GUIDE.md)
- **API Reference**: http://localhost:8000/docs (when running)
- **Multi-Disease**: [Multi-Disease Guide](MULTI_DISEASE_GUIDE.md)
- **Main README**: [README.md](../README.md)

---

## ✅ Quick Checklist

Before accessing the dashboard:
- [ ] MongoDB is running
- [ ] API is running (port 8000)
- [ ] Dashboard is running (port 8501)
- [ ] Browser open to http://localhost:8501

---

**Ready!** Your PRISM dashboard is at **http://localhost:8501** 🎉
