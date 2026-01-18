# Development Guide

## Getting Started

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.4 or higher (local or Atlas)
- Git

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd PRISM
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .\.venv\Scripts\activate

   # Unix/MacOS
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and set MONGO_URI
   ```

5. **Verify installation**
   ```bash
   python -c "import fastapi, pymongo, pydantic; print('All dependencies installed!')"
   ```

## Running the Application

### Development Server

```bash
uvicorn backend.app:app --reload --log-level debug
```

### Production Server

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Dashboard

```bash
streamlit run backend/dashboard/app.py
```

## Database Setup

### MongoDB Atlas (Cloud)

1. Create free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create database user
3. Whitelist IP address
4. Copy connection string to `MONGO_URI`

### Local MongoDB

```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data

# Set MONGO_URI in .env
MONGO_URI=mongodb://localhost:27017
```

## Loading Data

### Seed Sample Data

```bash
python -m backend.scripts.seed
```

### Load CSV Data

```bash
python -m backend.scripts.load_csv Datasets/covid_19_data.csv
```

CSV must have columns: `region_id,date,confirmed,deaths,recovered`

### Create Indexes

```bash
python -m backend.scripts.create_indexes
```

## Testing

### Manual API Testing

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

### Health Check

```bash
curl http://localhost:8000/health/
```

### Example API Calls

```bash
# List regions
curl http://localhost:8000/regions/

# Compute risk scores
curl -X POST http://localhost:8000/risk/compute

# Get latest risk scores
curl http://localhost:8000/risk/latest

# Generate alerts
curl -X POST http://localhost:8000/alerts/generate

# Get hotspots
curl http://localhost:8000/hotspots/?limit=10
```

## Code Style

### Python Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for functions and classes

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:

```python
import logging
from typing import Optional

from fastapi import APIRouter
from pymongo import DESCENDING

from backend.db import get_db
```

## Common Tasks

### Adding a New Route

1. Create route file in `backend/routes/`
2. Import and register in `backend/app.py`
3. Add error handling and logging
4. Add input validation

### Adding a New Service

1. Create service file in `backend/services/`
2. Add comprehensive error handling
3. Add logging for key operations
4. Import and use in routes

### Adding a New Schema

1. Create schema in `backend/schemas/`
2. Use Pydantic models with validation
3. Add field descriptions and constraints

## Troubleshooting

### MongoDB Connection Issues

- Verify MongoDB is running
- Check connection string format
- Verify network access/firewall
- Check credentials

### Missing Dependencies

```bash
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Unix/MacOS
lsof -ti:8000 | xargs kill -9
```

### Import Errors

- Ensure virtual environment is activated
- Run from project root directory
- Use `python -m` for module execution

## Project Structure

```
PRISM/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── config.py           # Configuration management
│   ├── db.py               # Database connection
│   ├── logging_config.py   # Logging setup
│   ├── routes/             # API endpoints
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic
│   ├── scripts/            # Utility scripts
│   └── utils/              # Helper functions
├── Datasets/               # Sample data
├── frontend/               # Static UI files
├── logs/                   # Application logs (auto-created)
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Example environment config
├── .gitignore              # Git ignore patterns
├── requirements.txt        # Python dependencies
└── README.md               # Project overview
```
