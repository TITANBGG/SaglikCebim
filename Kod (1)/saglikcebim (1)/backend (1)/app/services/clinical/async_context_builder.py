from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_medications import PatientMedication
from app.models.patient_allergies import PatientAllergy
from app.models.test_result import TestResult
from app.models.report import Report
from app.models.radiology_image import RadiologyImage
from app.models.anamnesis_audit_log import AnamnesisAuditLog
from app.models.patient_family_history import PatientFamilyHistory
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta


@dataclass
class PatientContext:
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    chronic_conditions: list[str] = None
    medications: list[str] = None
    allergies: list[str] = None
    abnormal_labs: list[dict] = None
    radiology_findings: list[str] = None
    chief_complaint: Optional[str] = None
    recent_complaints: list[str] = None
    family_history: list[str] = None

    def __post_init__(self):
        if self.chronic_conditions is None:
            self.chronic_conditions = []
        if self.medications is None:
            self.medications = []
        if self.allergies is None:
            self.allergies = []
        if self.abnormal_labs is None:
            self.abnormal_labs = []
        if self.radiology_findings is None:
            self.radiology_findings = []
        if self.recent_complaints is None:
            self.recent_complaints = []
        if self.family_history is None:
            self.family_history = []

    def to_prompt_text(self) -> str:
        lines = []
        if self.age:
            lines.append(f"Hasta: {self.age} yaşında {self.gender or 'cinsiyet belirtilmemiş'}")
        if self.chronic_conditions:
            lines.append(f"Kronik hastalıklar: {', '.join(self.chronic_conditions)}")
        if self.medications:
            lines.append(f"Kullandığı ilaçlar: {', '.join(self.medications)}")
        if self.allergies:
            lines.append(f"Alerjiler: {', '.join(self.allergies)}")
        if self.abnormal_labs:
            lab_str = ", ".join(
                f"{l['name']} {l['value']} {l.get('unit', '')} ({l['status']})"
                for l in self.abnormal_labs
            )
            lines.append(f"Anormal lab değerleri: {lab_str}")
        if self.radiology_findings:
            lines.append(f"Radyoloji bulguları: {', '.join(self.radiology_findings)}")
        if self.recent_complaints:
            recent_str = "; ".join(self.recent_complaints[-5:])
            lines.append(f"Son 90 gün şikayetleri: {recent_str}")
        if self.family_history:
            lines.append(f"Aile hikayesi: {', '.join(self.family_history)}")
        
        return "\n".join(lines) if lines else "Hasta bilgisi bulunamadı."


class AsyncContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build(self, user_id: int) -> PatientContext:
        profile = await self._get_profile(user_id)
        conditions = await self._get_conditions(user_id)
        medications = await self._get_medications(user_id)
        allergies = await self._get_allergies(user_id)
        abnormal_labs = await self._get_abnormal_labs(user_id)
        radiology = await self._get_radiology(user_id)
        chief_complaint, recent_complaints = await self._get_complaints(user_id)
        family_history = await self._get_family_history(user_id)

        return PatientContext(
            patient_id=str(user_id),
            age=profile.age if profile else None,
            gender=profile.gender if profile else None,
            chronic_conditions=conditions,
            medications=medications,
            allergies=allergies,
            abnormal_labs=abnormal_labs,
            radiology_findings=radiology,
            chief_complaint=chief_complaint,
            recent_complaints=recent_complaints,
            family_history=family_history,
        )

    async def _get_profile(self, user_id: int) -> Optional[PatientProfile]:
        result = await self.db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user_id).limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_conditions(self, user_id: int) -> list[str]:
        try:
            result = await self.db.execute(
                select(PatientCondition).where(PatientCondition.patient_id == user_id)
            )
            rows = result.scalars().all()
            return [c.condition_name for c in rows if c.condition_name]
        except Exception as e:
            print(f"[AsyncContextBuilder._get_conditions] Error: {e}")
            return []

    async def _get_medications(self, user_id: int) -> list[str]:
        try:
            result = await self.db.execute(
                select(PatientMedication).where(PatientMedication.patient_id == user_id)
            )
            rows = result.scalars().all()
            return [m.medication_name for m in rows if m.medication_name]
        except Exception as e:
            print(f"[AsyncContextBuilder._get_medications] Error: {e}")
            return []

    async def _get_allergies(self, user_id: int) -> list[str]:
        try:
            result = await self.db.execute(
                select(PatientAllergy).where(PatientAllergy.patient_id == user_id)
            )
            rows = result.scalars().all()
            return [a.allergen for a in rows if a.allergen]
        except Exception as e:
            print(f"[AsyncContextBuilder._get_allergies] Error: {e}")
            return []

    async def _get_abnormal_labs(self, user_id: int) -> list[dict]:
        try:
            result = await self.db.execute(
                select(TestResult)
                .join(Report, Report.id == TestResult.report_id)
                .where(
                    and_(
                        Report.user_id == user_id,
                        TestResult.status.in_(["High", "Low"])
                    )
                )
                .order_by(desc(TestResult.created_at))
                .limit(20)
            )
            rows = result.scalars().all()
            return [
                {
                    "name": r.test_name,
                    "value": str(r.value),
                    "unit": r.unit or "",
                    "status": r.status,
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[AsyncContextBuilder._get_abnormal_labs] Error: {e}")
            return []

    async def _get_radiology(self, user_id: int) -> list[str]:
        try:
            result = await self.db.execute(
                select(RadiologyImage)
                .where(RadiologyImage.patient_id == user_id)
                .order_by(desc(RadiologyImage.created_at))
                .limit(3)
            )
            rows = result.scalars().all()
            findings = []
            for r in rows:
                if hasattr(r, "findings") and r.findings:
                    if isinstance(r.findings, list):
                        findings.extend(r.findings)
                    else:
                        findings.append(str(r.findings))
            return findings
        except Exception as e:
            print(f"[AsyncContextBuilder._get_radiology] Error: {e}")
            return []

    async def _get_complaints(self, user_id: int) -> tuple[Optional[str], list[str]]:
        try:
            cutoff = datetime.now() - timedelta(days=90)
            result = await self.db.execute(
                select(AnamnesisAuditLog)
                .where(
                    and_(
                        AnamnesisAuditLog.patient_id == user_id,
                        AnamnesisAuditLog.created_at >= cutoff
                    )
                )
                .order_by(desc(AnamnesisAuditLog.created_at))
                .limit(10)
            )
            rows = result.scalars().all()
            if not rows:
                return None, []
            
            latest_complaint = None
            if hasattr(rows[0], "chief_complaint"):
                latest_complaint = rows[0].chief_complaint
            
            recent = []
            for r in rows:
                if hasattr(r, "chief_complaint") and r.chief_complaint:
                    recent.append(str(r.chief_complaint))
            
            return latest_complaint, recent
        except Exception as e:
            print(f"[AsyncContextBuilder._get_complaints] Error: {e}")
            return None, []

    async def _get_family_history(self, user_id: int) -> list[str]:
        try:
            result = await self.db.execute(
                select(PatientFamilyHistory).where(PatientFamilyHistory.patient_id == user_id)
            )
            rows = result.scalars().all()
            return [r.condition if hasattr(r, "condition") else str(r) for r in rows]
        except Exception:
            return []
