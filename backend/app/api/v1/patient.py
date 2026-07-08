"""
Patient summary endpoint — GET /patient/summary/basic

Anamnesis + Lab (reports) + Radyoloji verilerini birleştirerek
modalite bayrakları ve kısa özet döndürür.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_medications import PatientMedication
from app.models.patient_allergies import PatientAllergy
from app.models.report import Report
from app.models.radiology_image import RadiologyImage
from app.models.test_result import TestResult

router = APIRouter()


@router.get("/summary/basic")
def get_patient_summary(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Hasta modalite bayrakları ve özet verisi.

    Döndürür:
    - has_profile: Anamnez profili mevcut mu
    - has_lab: En az bir analiz edilmiş kan tahlili var mı
    - has_radiology: En az bir radyoloji görüntüsü var mı
    - completion_score: 0-100 arası veri tamlık puanı
    - profile: Yaş, cinsiyet, boy, kilo, kan grubu
    - conditions_count, medications_count, allergies_count
    - last_lab_date, last_radiology_date
    - abnormal_lab_count: Anormal test sonucu sayısı
    """
    user_id = int(current_user_id)

    # ── Anamnesis ─────────────────────────────────────────────────────────────
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    conditions = db.query(PatientCondition).filter(PatientCondition.user_id == user_id).all()
    medications = db.query(PatientMedication).filter(PatientMedication.user_id == user_id).all()
    allergies  = db.query(PatientAllergy).filter(PatientAllergy.user_id == user_id).all()

    has_profile = profile is not None and any([
        profile.age, profile.gender, profile.height, profile.weight
    ])

    # ── Lab Reports ───────────────────────────────────────────────────────────
    last_report = (
        db.query(Report)
        .filter(Report.user_id == user_id, Report.status == "analyzed")
        .order_by(Report.created_at.desc())
        .first()
    )
    has_lab = last_report is not None

    abnormal_count = 0
    if has_lab:
        abnormal_count = (
            db.query(TestResult)
            .filter(
                TestResult.report_id == last_report.id,
                TestResult.status.in_(["High", "Low"]),
            )
            .count()
        )

    # ── Radiology ─────────────────────────────────────────────────────────────
    last_radio = (
        db.query(RadiologyImage)
        .filter(RadiologyImage.user_id == user_id)
        .order_by(RadiologyImage.created_at.desc())
        .first()
    )
    has_radiology = last_radio is not None

    # ── Completion Score (0-100) ──────────────────────────────────────────────
    # Her modalite 33 puan; profil tam ise +1 bonus
    score = 0
    if has_profile:
        score += 34
    if has_lab:
        score += 33
    if has_radiology:
        score += 33
    score = min(score, 100)

    # ── Missing modalities (rehberli yönlendirme için) ────────────────────────
    missing = []
    if not has_profile:
        missing.append("anamnez")
    if not has_lab:
        missing.append("kan_tahlili")
    if not has_radiology:
        missing.append("radyoloji")

    return {
        "has_profile": has_profile,
        "has_lab": has_lab,
        "has_radiology": has_radiology,
        "completion_score": score,
        "missing_modalities": missing,
        "profile": {
            "age": profile.age if profile else None,
            "gender": profile.gender if profile else None,
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "blood_type": profile.blood_type if profile else None,
        },
        "conditions_count": len(conditions),
        "medications_count": len(medications),
        "allergies_count": len(allergies),
        "last_lab_date": last_report.created_at.isoformat() if last_report and last_report.created_at else None,
        "last_radiology_date": last_radio.created_at.isoformat() if last_radio and last_radio.created_at else None,
        "abnormal_lab_count": abnormal_count,
    }
