from sqlalchemy.orm import Session
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_allergies import PatientAllergy
from app.models.test_result import TestResult
from app.models.report import Report
from app.models.patient_medications import PatientMedication
from app.models.radiology_image import RadiologyFinding, RadiologyImage
from typing import Dict, Any, List

class ClinicalContextBuilder:
    """
    Kullanıcının dağınık sağlık verilerini (Tahliller, Röntgenler, Profil, Alerjiler)
    tek bir yapılandırılmış bağlama (Context) dönüştürür.
    """
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_patient_profile(self) -> str:
        profile = self.db.query(PatientProfile).filter(PatientProfile.user_id == self.user_id).first()
        if not profile:
            return "Yaş/Cinsiyet: Bilinmiyor"
        age = profile.age if profile.age else "Bilinmiyor"
        gender = profile.gender if hasattr(profile, 'gender') and profile.gender else "Belirtilmemiş"
        return f"Yaş: {age}, Cinsiyet: {gender}"

    def get_medical_history(self) -> str:
        conditions = self.db.query(PatientCondition).filter(PatientCondition.user_id == self.user_id).all()
        allergies = self.db.query(PatientAllergy).filter(PatientAllergy.user_id == self.user_id).all()
        meds = self.db.query(PatientMedication).filter(PatientMedication.user_id == self.user_id).all()
        
        cond_str = ", ".join([c.condition_name for c in conditions]) if conditions else "Yok"
        alg_str = ", ".join([a.allergen_name for a in allergies]) if allergies else "Yok"
        med_str = ", ".join([m.medication_name for m in meds]) if meds else "Yok"
        
        return f"Kronik Hastalıklar: {cond_str}\nAlerjiler: {alg_str}\nMevcut İlaçlar: {med_str}"

    def get_lab_anomalies(self) -> str:
        from sqlalchemy import desc
        abnormal_tests = (
            self.db.query(TestResult)
            .join(Report, TestResult.report_id == Report.id)
            .filter(Report.user_id == self.user_id, TestResult.status != "Normal")
            .order_by(desc(Report.created_at))
            .all()
        )

        unique_tests: dict = {}
        for t in abnormal_tests:
            if t.test_name not in unique_tests:
                unique_tests[t.test_name] = t

        if not unique_tests:
            return "Anormal kan tahlili bulgusu yok."

        lines = []
        for t in unique_tests.values():
            ref = f"{t.ref_min}-{t.ref_max}" if t.ref_min and t.ref_max else "?"
            status_emoji = "⬆️" if t.status and "high" in t.status.lower() else ("⬇️" if t.status and "low" in t.status.lower() else "⚠️")
            lines.append(f"  {status_emoji} {t.test_name}: {t.value} (ref {ref}) [{t.status}]")

        return "\n".join(lines)

    def get_all_recent_labs(self) -> str:
        """Son rapordaki tüm tahlil değerlerini (normal dahil) döndürür."""
        from sqlalchemy import desc
        latest_report = (
            self.db.query(Report)
            .filter(Report.user_id == self.user_id)
            .order_by(desc(Report.created_at))
            .first()
        )
        if not latest_report:
            return ""

        all_tests = (
            self.db.query(TestResult)
            .filter(TestResult.report_id == latest_report.id)
            .all()
        )
        if not all_tests:
            return ""

        lines = []
        for t in all_tests:
            ref = f"{t.ref_min}-{t.ref_max}" if t.ref_min and t.ref_max else "?"
            marker = "" if t.status and t.status.lower() == "normal" else f" [{t.status}] ⚠️"
            lines.append(f"  {t.test_name}: {t.value} (ref {ref}){marker}")

        return "\n".join(lines)

    def get_radiology_findings(self) -> str:
        latest_image = self.db.query(RadiologyImage).filter(RadiologyImage.user_id == self.user_id).order_by(RadiologyImage.id.desc()).first()
        if not latest_image:
            return "Kayıtlı radyoloji görüntüsü yok."
            
        finding = self.db.query(RadiologyFinding).filter(RadiologyFinding.image_id == latest_image.id).first()
        if not finding:
            return "Son radyoloji görüntüsünde anormal bulgu raporlanmadı."
            
        finding_text = finding.finding_type
        if "infiltrat" in finding_text.lower() or "infiltration" in finding_text.lower():
            finding_text = f"Olası İnfiltrasyon: {finding_text}. Klinik bulgularla korelasyon önerilir."
            
        return finding_text

    def build_full_context(self, current_message: str, history: List[Any] = None) -> Dict[str, str]:
        """Tüm verileri LLM'e beslenecek formata getirir."""

        history_str = ""
        if history:
            for msg in history:
                msg_role = getattr(msg, "role", None)
                msg_content = getattr(msg, "content", None)
                if isinstance(msg, dict):
                    msg_role = msg.get("role", msg_role)
                    msg_content = msg.get("content", msg.get("message", msg_content))
                role = "Doktor:" if msg_role == "assistant" else "Hasta:"
                history_str += f"{role} {msg_content or ''}\n"
        if not history_str:
            history_str = "Önceki konuşma yok."

        abnormal_labs = self.get_lab_anomalies()
        all_labs = self.get_all_recent_labs()

        # LLM için birleşik tahlil bloğu: anormallar öne, tümü arkaya
        if all_labs:
            labs_block = f"ANORMAL:\n{abnormal_labs}\nTÜM DEĞERLER:\n{all_labs}" if abnormal_labs != "Anormal kan tahlili bulgusu yok." else f"Tüm değerler normal sınırlarda.\nTÜM DEĞERLER:\n{all_labs}"
        else:
            labs_block = abnormal_labs

        return {
            "patient_profile": self.get_patient_profile(),
            "medical_history": self.get_medical_history(),
            "lab_anomalies": abnormal_labs,
            "labs_full": labs_block,
            "radiology_findings": self.get_radiology_findings(),
            "chat_history": history_str,
            "current_message": current_message,
        }
