from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.api.v1 import articles
from app.api.v1 import auth
from app.api.v1 import radiology
from app.api.v1 import reports
from app.api.v1 import anamnesis
from app.api.v1 import chatbot
from app.api.v1 import evidence
from app.api.v1 import notifications
from app.api.v1 import roadmap
from app.api.v1 import survey
from app.api.v1 import patient
from app.core.database import init_db
from app.services.scheduler import start_scheduler, stop_scheduler
from fastapi.staticfiles import StaticFiles
import os


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models.roadmap_session import RoadmapSession  # noqa: F401
    from app.models.sus_survey import SusSurvey            # noqa: F401
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


limiter = Limiter(key_func=get_remote_address)


def _parse_csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]

app = FastAPI(
    title="SaglikCebim API",
    description="🏥 Tibbi Tahlil Analiz Platformu - Health Analysis Platform\n\n" +
    "API Endpoints:\n" +
    "- **Auth**: User registration, login, profile management\n" +
    "- **Reports**: PDF/Image upload, listing, analysis\n" +
    "- **Radiology**: X-Ray and imaging analysis\n" +
    "- **Articles**: Medical articles and resources\n" +
    "- **Notifications**: User notifications\n\n" +
    "For API documentation visit: /docs (Swagger UI) or /redoc (ReDoc)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_csv_env("CORS_ALLOW_ORIGINS", []),
    allow_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX") or None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "SaglikCebim API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(radiology.router, prefix="/radiology", tags=["radiology"])
app.include_router(anamnesis.router, prefix="/api/v1/anamnesis", tags=["anamnesis"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(roadmap.router, prefix="/api/v1", tags=["roadmap"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(survey.router, prefix="/api/v1/survey", tags=["survey"])
app.include_router(patient.router, prefix="/patient", tags=["patient"])
