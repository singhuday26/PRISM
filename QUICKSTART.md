# Quick Start Guide

This guide will get you up and running with PRISM in under 5 minutes.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] MongoDB running locally OR MongoDB Atlas account
- [ ] Git installed (optional)

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)

```bash
# Activate your virtual environment first (if using one)
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite editor
# Minimum required: Set MONGO_URI
```

**MongoDB Connection Strings:**

**Local MongoDB:**

```
MONGO_URI=mongodb://localhost:27017
```

**MongoDB Atlas (Cloud):**

```
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
```

### 3. Verify Setup (30 seconds)

```bash
# Test MongoDB connection
python -c "from backend.db import get_client; get_client().admin.command('ping'); print('✅ MongoDB connected!')"

# Test all imports
python -c "from backend.app import app; print('✅ All dependencies OK!')"
```

### 4. Load Sample Data (1 minute)

```bash
# Load the seed data
python -m backend.scripts.seed

# Expected output: "Inserted X regions and Y cases"
```

### 5. Start the API (30 seconds)

```bash
# Start development server
uvicorn backend.app:app --reload

# You should see:
# INFO: Application startup complete
# INFO: Uvicorn running on http://127.0.0.1:8000
```

### 6. Test the API (30 seconds)

Open your browser to:

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/

Or use curl:

```bash
# Health check
curl http://localhost:8000/health/

# List regions
curl http://localhost:8000/regions/

# Compute risk scores
curl -X POST http://localhost:8000/risk/compute

# Get latest risk scores
curl http://localhost:8000/risk/latest
```

### 7. Start Dashboard (Optional)

In a new terminal:

```bash
streamlit run backend/dashboard/app.py

# Opens browser to http://localhost:8501
```

## Common Issues

### "No module named 'backend'"

**Solution:** Make sure you're running from the project root directory.

### "Could not connect to MongoDB"

**Solutions:**

- Verify MongoDB is running: `mongod --version`
- Check MONGO_URI in .env file
- For Atlas: Verify IP is whitelisted

### "Port 8000 already in use"

**Solution:** Kill the process or use a different port:

```bash
uvicorn backend.app:app --port 8001 --reload
```

### Import errors

**Solution:** Reinstall dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

Now that PRISM is running:

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Load your data:** Use `python -m backend.scripts.load_csv yourdata.csv`
3. **Read the docs:** See [README.md](README.md) for full documentation
4. **Development:** See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed guide

## Quick Reference

### Useful Commands

```bash
# Start API (development)
uvicorn backend.app:app --reload

# Start API (production)
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4

# Start dashboard
streamlit run backend/dashboard/app.py

# Load seed data
python -m backend.scripts.seed

# Load CSV data
python -m backend.scripts.load_csv path/to/data.csv

# Create indexes manually
python -m backend.scripts.create_indexes

# Recompute risk scores
python -m backend.scripts.recompute_risk
```

### Key Endpoints

| Endpoint              | Method | Description                 |
| --------------------- | ------ | --------------------------- |
| `/health/`            | GET    | Health check with DB status |
| `/regions/`           | GET    | List all regions            |
| `/risk/compute`       | POST   | Compute risk scores         |
| `/risk/latest`        | GET    | Get latest risk scores      |
| `/alerts/generate`    | POST   | Generate alerts             |
| `/alerts/latest`      | GET    | Get latest alerts           |
| `/hotspots/`          | GET    | Get top hotspots            |
| `/forecasts/generate` | POST   | Generate forecasts          |
| `/forecasts/latest`   | GET    | Get latest forecasts        |

### Environment Variables Quick Reference

| Variable  | Required | Default  | Description               |
| --------- | -------- | -------- | ------------------------- |
| MONGO_URI | ✅ Yes   | -        | MongoDB connection string |
| DB_NAME   | No       | prism_db | Database name             |
| LOG_LEVEL | No       | INFO     | Logging level             |
| API_PORT  | No       | 8000     | API port                  |

See [.env.example](.env.example) for all options.

## Getting Help

- **Documentation:** [README.md](README.md)
- **Development Guide:** [DEVELOPMENT.md](DEVELOPMENT.md)
- **Security:** [SECURITY.md](SECURITY.md)
- **Changes:** [CHANGES.md](CHANGES.md)

## Success Checklist

After completing this guide, you should have:

- [x] ✅ All dependencies installed
- [x] ✅ MongoDB connected
- [x] ✅ Sample data loaded
- [x] ✅ API running at http://localhost:8000
- [x] ✅ API docs accessible
- [x] ✅ Health check passing
- [x] ✅ Dashboard running (optional)

**🎉 Congratulations! PRISM is now running successfully!**
