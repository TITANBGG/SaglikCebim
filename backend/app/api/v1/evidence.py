from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.services.evidence.engine import EvidenceEngine


router = APIRouter()


class EvidenceTestRequest(BaseModel):
    query: str = Field(default="pneumonia treatment guidelines", description="Evidence engine arama sorgusu")


@router.post("/test")
async def test_evidence(payload: EvidenceTestRequest, current_user_id: str = Depends(get_current_user)):
    """Evidence motorunu test eder ve birleşik kaynak sonuçlarını döndürür."""
    engine = EvidenceEngine()
    results = await engine.search_all(payload.query)
    return {
        "query": payload.query,
        "results_count": len(results),
        "sources": sorted({r.source for r in results}),
        "results": [r.model_dump() for r in results],
    }
