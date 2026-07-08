from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1 import reports as reports_api
from app.core.database import Base, get_db
from app.main import app, limiter

# Tüm modelleri import et → SQLAlchemy metadata tabloları bilsin
from app.models import report          # noqa: F401
from app.models import test_result     # noqa: F401
from app.models import user            # noqa: F401
from app.models import chat            # noqa: F401
from app.models import anamnesis       # noqa: F401
from app.models import patient_conditions   # noqa: F401
from app.models import patient_allergies    # noqa: F401
from app.models import patient_medications  # noqa: F401
from app.models import radiology_image      # noqa: F401
try:
    from app.models import roadmap_session  # noqa: F401
except ImportError:
    pass

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def isolate_upload_dir(monkeypatch, request):
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in request.node.name)
    upload_dir = Path(__file__).parent / "tmp_uploads" / safe_name
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(reports_api, "UPLOAD_DIR", upload_dir)
    yield


@pytest.fixture(autouse=True)
def disable_rate_limit():
    """Her testten önce rate limit sayaçlarını sıfırla."""
    try:
        # slowapi → limits kütüphanesi → MemoryStorage → reset
        storage = limiter._limiter.storage
        if hasattr(storage, "reset"):
            storage.reset()
        elif hasattr(storage, "storage"):
            storage.storage.clear()
    except Exception:
        pass
    yield
    # Test sonrası da sıfırla
    try:
        storage = limiter._limiter.storage
        if hasattr(storage, "reset"):
            storage.reset()
        elif hasattr(storage, "storage"):
            storage.storage.clear()
    except Exception:
        pass


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "password": "Test1234!",
            "full_name": "Test User",
        },
    )
    login_res = client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "Test1234!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
