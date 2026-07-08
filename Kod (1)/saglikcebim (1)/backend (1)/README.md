# 🏥 SaglikCebim Backend

FastAPI-based health analysis platform backend.

## 🚀 Quick Start

### 1️⃣ **Fastest Way - Click to Start**

**Option A: Windows batch file (easiest)**
```
Double-click: START-BACKEND.cmd
```

**Option B: Windows batch file (alternative)**
```
Double-click: START.bat
```

**Option C: Python script**
```powershell
python quick-start.py
```

### 2️⃣ **Command Line**

```powershell
# Activate venv
.\venv\Scripts\activate.bat

# Run server
python run.py
```

### 3️⃣ **Access the API**

Once server is running, visit:
- **API:** `http://127.0.0.1:8001`
- **Swagger Docs:** `http://127.0.0.1:8001/docs` (Interactive testing)
- **ReDoc:** `http://127.0.0.1:8001/redoc` (API documentation)

---

## 📦 Installation (One-Time Only)

```powershell
# Create virtual environment
py -m venv venv

# Activate it
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

---

## 📚 API Endpoints (26 Total)

### Auth (3)
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Reports (11)
- `POST /reports/upload` - Upload PDF report
- `GET /reports/` - List all reports
- `GET /reports/{id}/results` - Get test results
- `POST /reports/{id}/parse` - Parse PDF
- And 7 more...

### Articles (3)
- `GET /articles/daily` - Get daily PubMed articles
- `POST /articles/search` - Search PubMed
- `POST /articles/chat` - AI chat about articles

### Notifications (7)
- `POST /notifications/subscribe` - Web push subscription
- `GET /notifications/` - List notifications
- And 5 more...

### Radiology (1)
- `POST /radiology/upload` - Analyze X-ray

### Other (1)
- `GET /health` - Health check

---

## 🔧 Development

### Run with Auto-Reload
```powershell
uvicorn app.main:app --reload
```

### Monitoring and Logs
- Runtime traces are written to `backend_logs/`.
- `upload_trace.log` captures report upload calls.
- `token_trace.log` captures auth token checks.
- Dashboard monitoring is available at `GET /reports/monitoring`.

### Quick Smoke Test
```powershell
python test_e2e_detailed.py
python test_e2e_final.py
```

### Run Tests
```powershell
pytest
pytest -v  # Verbose
pytest --cov=app  # With coverage
```

### Database

Database is auto-initialized on startup.

To manually initialize:
```powershell
python init_db.py
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py      # Auth endpoints
│   │       ├── reports.py   # Report endpoints
│   │       ├── articles.py  # Article endpoints
│   │       └── ...
│   ├── core/
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── security.py      # JWT & hashing
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── scheduler.py     # Background tasks
│   ├── models/
│   │   ├── user.py
│   │   ├── report.py
│   │   └── ...              # 14 ORM models
│   ├── schemas/             # Pydantic request/response
│   └── services/            # Business logic
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── run.py                  # Simple entry point
├── START.bat               # Quick start (batch)
└── quick-start.py          # Quick start (Python)
```

---

## 🐳 Docker

Run full stack (frontend + backend + database):

```powershell
cd ..
docker-compose up
```

---

## 🆘 Troubleshooting

### Port 8000 already in use
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Virtual environment not found
```powershell
py -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Module import error
Ensure you're in the `backend (1)` directory and venv is activated.

---

## 📖 Documentation

- [QUICKSTART.md](../QUICKSTART.md) - Full system setup guide
- [README_Sistemle_ilgili.md](../README_Sistemle_ilgili.md) - System details
- [DEVELOPER_README.md](DEVELOPER_README.md) - Short developer notes

---

**Status:** ✅ Backend framework complete and ready for use.
