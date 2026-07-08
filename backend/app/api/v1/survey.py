"""
SUS (System Usability Scale) anketi endpoint'leri.
10 standart SUS sorusu, 1-5 Likert ölçeği.
SUS skoru formülü: ((tek sorular toplamı - 5) + (25 - çift sorular toplamı)) × 2.5
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.sus_survey import SusSurvey

router = APIRouter()

SUS_QUESTIONS = [
    "Bu sistemi sık sık kullanmak isterdim.",
    "Bu sistemi gereksiz yere karmaşık buldum.",
    "Bu sistemi kullanması kolay buldum.",
    "Bu sistemi kullanmak için bir uzmandan destek almam gerektiğini düşünüyorum.",
    "Bu sistemin çeşitli fonksiyonlarının iyi entegre edildiğini gördüm.",
    "Bu sistemde çok fazla tutarsızlık olduğunu düşünüyorum.",
    "Çoğu insanın bu sistemi kullanmayı çabuk öğreneceğini hayal edebiliyorum.",
    "Bu sistemi kullanmayı çok hantal buldum.",
    "Bu sistemi kullanırken kendimi güvende hissettim.",
    "Bu sistemi kullanmaya başlamadan önce çok şey öğrenmem gerektiğini hissettim.",
]


class SurveySubmit(BaseModel):
    scores: dict[str, int] = Field(
        description="q1..q10, her biri 1-5 arasında"
    )
    role: str | None = None
    comment: str | None = Field(default=None, max_length=500)


def _calc_sus(scores: dict[str, int]) -> float:
    """Standart SUS formülü: 0-100 arası skor."""
    odd  = sum(scores.get(f"q{i}", 3) - 1 for i in [1, 3, 5, 7, 9])
    even = sum(5 - scores.get(f"q{i}", 3) for i in [2, 4, 6, 8, 10])
    return (odd + even) * 2.5


@router.post("/submit")
def submit_survey(
    data: SurveySubmit,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sus_score = _calc_sus(data.scores)
    row = SusSurvey(
        user_id=int(current_user_id),
        scores=data.scores,
        sus_score=round(sus_score, 1),
        role=data.role,
        comment=data.comment,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "sus_score": row.sus_score,
        "grade": _sus_grade(row.sus_score),
        "message": "Geri bildiriminiz için teşekkürler!",
    }


@router.get("/results")
def get_survey_results(
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ortalama SUS skoru ve dağılım özeti."""
    rows = db.query(SusSurvey).all()
    if not rows:
        return {"count": 0, "mean_sus": None, "grade": None, "distribution": []}

    scores = [r.sus_score for r in rows]
    mean = round(sum(scores) / len(scores), 1)
    return {
        "count": len(scores),
        "mean_sus": mean,
        "min_sus": round(min(scores), 1),
        "max_sus": round(max(scores), 1),
        "grade": _sus_grade(mean),
        "distribution": sorted(scores),
    }


@router.get("/questions")
def get_questions():
    return {"questions": [{"id": f"q{i+1}", "text": q} for i, q in enumerate(SUS_QUESTIONS)]}


def _sus_grade(score: float) -> str:
    if score >= 85: return "A (Mükemmel)"
    if score >= 72: return "B (İyi)"
    if score >= 52: return "C (Orta)"
    if score >= 38: return "D (Zayıf)"
    return "F (Kullanılamaz)"
