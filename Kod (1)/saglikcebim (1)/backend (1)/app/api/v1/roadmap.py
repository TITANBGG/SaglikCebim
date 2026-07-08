"""
Roadmap API Router — POST /api/v1/roadmap/generate, GET /api/v1/roadmap/history
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_async_db
from app.core.dependencies import get_current_user
from app.models.roadmap_session import RoadmapSession
from app.services.clinical.roadmap_generator import RoadmapGenerator, fallback_roadmap
from app.services.clinical.schemas import ClinicalRoadmap
from app.services.clinical.streaming_roadmap import stream_roadmap

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class RoadmapGenerateRequest(BaseModel):
    message: str = Field(description="Klinik yol haritası oluşturmak için kullanıcı mesajı")
    use_evidence: bool = Field(default=True, description="Kanıt kaynaklarını kullan")


class EvidenceTestRequest(BaseModel):
    query: str = Field(description="Evidence engine için arama sorgusu")


# ---------------------------------------------------------------------------
# POST /roadmap/generate
# ---------------------------------------------------------------------------

@router.post("/roadmap/generate", response_model=ClinicalRoadmap, tags=["roadmap"])
async def generate_roadmap(
    payload: RoadmapGenerateRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kullanıcı mesajından yapılandırılmış ClinicalRoadmap üretir.
    JWT auth zorunlu.
    """
    try:
        user_id = int(current_user_id)

        # Hasta bağlamını oluştur
        from app.services.clinical.context_builder import ClinicalContextBuilder
        context_builder = ClinicalContextBuilder(db, user_id)
        context = context_builder.build_full_context(payload.message)

        # Evidence kullanımına göre context'e flag ekle
        context["use_evidence"] = payload.use_evidence

        # Roadmap üret
        generator = RoadmapGenerator()
        roadmap = generator.generate(context)

        # DB'ye kaydet
        try:
            session = RoadmapSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                risk_level=roadmap.risk_level,
                chief_complaint=payload.message[:500],
                roadmap_json=roadmap.model_dump(mode="json"),
                safety_validated=roadmap.safety_validated,
            )
            db.add(session)
            db.commit()
        except Exception as db_exc:
            print(f"[Roadmap API] DB kayıt hatası (devam ediliyor): {db_exc}")
            db.rollback()

        return roadmap

    except Exception as exc:
        print(f"[Roadmap API] Hata: {exc}")
        return fallback_roadmap()


# ---------------------------------------------------------------------------
# GET /roadmap/history
# ---------------------------------------------------------------------------

@router.get("/roadmap/history", tags=["roadmap"])
async def get_roadmap_history(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Son 10 roadmap kaydını döndürür. JWT auth zorunlu."""
    try:
        user_id = int(current_user_id)
        sessions = (
            db.query(RoadmapSession)
            .filter(RoadmapSession.user_id == user_id)
            .order_by(RoadmapSession.created_at.desc())
            .limit(10)
            .all()
        )
        return [
            {
                "id": s.id,
                "risk_level": s.risk_level,
                "chief_complaint": s.chief_complaint,
                "safety_validated": s.safety_validated,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "roadmap": s.roadmap_json,
            }
            for s in sessions
        ]
    except Exception as exc:
        print(f"[Roadmap History] Hata: {exc}")
        raise HTTPException(status_code=500, detail="Geçmiş roadmap'ler alınamadı.")


# ---------------------------------------------------------------------------
# POST /evidence/test (Auth yok — test amaçlı)
# ---------------------------------------------------------------------------

@router.post("/roadmap/evidence/test", tags=["evidence"])
async def test_evidence(payload: EvidenceTestRequest):
    """Evidence engine'i test eder. Auth gerektirmez."""
    try:
        from app.services.evidence.engine import EvidenceEngine

        engine = EvidenceEngine()
        if not engine.is_any_available():
            return {"available": False, "results": [], "message": "Hiçbir evidence provider aktif değil."}

        results = await engine.search_all(payload.query, max_per_source=3)
        return {
            "available": True,
            "query": payload.query,
            "count": len(results),
            "results": [
                {
                    "source": r.source,
                    "title": r.title,
                    "url": getattr(r, "url", None),
                    "pmid": getattr(r, "pmid", None),
                    "evidence_level": getattr(r, "evidence_level", None),
                    "year": getattr(r, "year", None),
                    "summary": getattr(r, "summary", None),
                }
                for r in results
            ],
        }
    except ImportError:
        return {"available": False, "results": [], "message": "Evidence engine import edilemedi."}
    except Exception as exc:
        return {"available": False, "results": [], "message": str(exc)}


# ---------------------------------------------------------------------------
# POST /roadmap/stream (SSE streaming endpoint)
# ---------------------------------------------------------------------------

@router.post("/roadmap/stream", tags=["roadmap"])
async def stream_roadmap_endpoint(
    payload: RoadmapGenerateRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    SSE streaming üzerinden ClinicalRoadmap üretir.
    JWT auth zorunlu.
    
    Gelen olaylar:
    - event: status → {"step": str, "message": str}
    - event: token → {"content": str}
    - event: safety_warning → {"violations": [str]}
    - event: roadmap → {ClinicalRoadmap JSON}
    - event: done → {"status": "success"|"error"}
    - event: error → {"message": str}
    """
    user_id = int(current_user_id)
    
    async def generate():
        async for event_chunk in stream_roadmap(user_id, payload.message, db):
            yield event_chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# POST /roadmap/stream-test (SSE streaming endpoint — NO AUTH for testing)
# ---------------------------------------------------------------------------

@router.post("/roadmap/stream-test", tags=["roadmap"])
async def stream_roadmap_test_endpoint(
    payload: RoadmapGenerateRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Test endpoint — NO JWT REQUIRED. For development/testing only."""
    user_id = 1  # Dummy user for testing
    
    async def generate():
        async for event_chunk in stream_roadmap(user_id, payload.message, db):
            yield event_chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
