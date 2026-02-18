# PRISM — Quick Start

> **Prerequisites:** Python 3.9+, Node.js 18+, MongoDB (local or Atlas)

---

## 1. Clone & enter the project

```bash
git clone https://github.com/singhuday26/PRISM.git
cd PRISM
```

---

## 2. Python environment & dependencies

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate
# Activate — macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 3. Environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set `MONGO_URI`:

```
# Local MongoDB
MONGO_URI=mongodb://localhost:27017

# MongoDB Atlas
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

---

## 4. Seed sample data

> Run all commands below from the project root `PRISM/`

```bash
python -m backend.scripts.seed
```

---

## 5. Start the API — Terminal 1

```bash
uvicorn backend.app:app --reload
```

- API → http://localhost:8000
- Docs → http://localhost:8000/docs

---

## 6. Start the frontend — Terminal 2

```bash
cd frontend
npm install
npm run dev
```

- Frontend → http://localhost:5173

---

## 7. Start the dashboard (optional) — Terminal 3

```bash
streamlit run backend/dashboard/app.py
```

- Dashboard → http://localhost:8501

---

## One-command start (API + Dashboard)

```bash
python start_prism.py
```

---

## Other useful commands

```bash
# Verify MongoDB connection
python -c "from backend.db import get_client; get_client().admin.command('ping'); print('MongoDB OK')"

# Create DB indexes
python -m backend.scripts.create_indexes

# Recompute risk scores
python -m backend.scripts.recompute_risk

# Load a custom CSV
python -m backend.scripts.load_csv path/to/data.csv

# Run backend tests
python -m pytest tests/ -v

# Kill all PRISM processes (Windows)
powershell -File kill_prism.ps1
```

---

## Troubleshooting

| Problem                        | Fix                                                 |
| ------------------------------ | --------------------------------------------------- |
| `No module named 'backend'`    | Run commands from the project root `PRISM/`         |
| `Could not connect to MongoDB` | Start `mongod` or check `MONGO_URI` in `.env`       |
| `Port 8000 already in use`     | `uvicorn backend.app:app --port 8001 --reload`      |
| Import errors                  | `pip install -r requirements.txt --force-reinstall` |
