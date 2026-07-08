from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_allergies import PatientAllergy
from app.models.test_result import TestResult
from app.models.radiology_image import RadiologyFinding, RadiologyImage
from app.services.ollama_client import get_ollama_client
from app.core.logging import get_logger

logger = get_logger("ollama_agent")


class OllamaDiagnosisAgent:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = int(user_id)
        self.client = get_ollama_client()

    # ------------------------------------------------------------------
    # BAĞLAM OLUŞTURMA
    # ------------------------------------------------------------------
    def _get_context(self):
        profile = self.db.query(PatientProfile).filter(
            PatientProfile.user_id == self.user_id
        ).first()
        conditions = self.db.query(PatientCondition).filter(
            PatientCondition.user_id == self.user_id
        ).all()
        allergies = self.db.query(PatientAllergy).filter(
            PatientAllergy.user_id == self.user_id
        ).all()

        cond_str = ", ".join([c.condition_name for c in conditions]) if conditions else "Yok"
        alg_str  = ", ".join([a.allergen_name  for a in allergies])  if allergies  else "Yok"
        age      = profile.age if profile and profile.age else "Bilinmiyor"

        # En yeni rapordaki anormal tahliller (DESC tarih sırası, deduplicate)
        from app.models.report import Report
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

        if unique_tests:
            blood_str = ""
            for t in unique_tests.values():
                ref = f"{t.ref_min}-{t.ref_max}" if t.ref_min and t.ref_max else "Bilinmiyor"
                blood_str += f"- {t.test_name}: {t.value} (Referans: {ref}) [{t.status}]\n"
        else:
            blood_str = "Tümü normal"

        # En son röntgen
        latest_image = self.db.query(RadiologyImage).filter(
            RadiologyImage.user_id == self.user_id
        ).order_by(RadiologyImage.id.desc()).first()
        xray_label = "Normal"
        if latest_image:
            finding = self.db.query(RadiologyFinding).filter(
                RadiologyFinding.image_id == latest_image.id
            ).first()
            if finding:
                ft = finding.finding_type.lower()
                xray_label = (
                    "Olası infiltrasyon tespit edildi. Klinik korelasyon önerilir."
                    if "infiltrat" in ft or "infiltration" in ft
                    else finding.finding_type
                )

        return {
            "age": age,
            "conditions": cond_str,
            "allergies": alg_str,
            "blood": blood_str,
            "xray": xray_label,
            "blood_list": [t.test_name for t in abnormal_tests],
        }

    # ------------------------------------------------------------------
    # SOHBET MODU  (chat format — daha iyi Türkçe tutumu)
    # ------------------------------------------------------------------
    def chat_conversational(
        self,
        user_message: str,
        history: list = None,
        user_name: str = "ali",
    ) -> str:
        context = self._get_context()
        message_lower = (user_message or "").strip().lower()

        history_str = ""
        if history:
            for msg in history:
                role    = getattr(msg, "role", None)
                content = getattr(msg, "content", None)
                if isinstance(msg, dict):
                    role    = msg.get("role", role)
                    content = msg.get("content", msg.get("message", content))
                speaker = "Doktor" if role == "assistant" else "Hasta"
                history_str += f"{speaker}: {content or ''}\n"
        if not history_str:
            history_str = "Önceki konuşma yok."

        # System prompt — rolleri ayırarak göndermek dil talimatını çok daha iyi tutar
        system_prompt = (
            "Sen SağlıkCebim'in Türkçe sağlık asistanısın. "
            "Görevin hastanın kayıtlı sağlık verilerini açıklayıcı biçimde yorumlamak ve Türkçe yanıt vermektir.\n\n"
            "ZORUNLU KURALLAR:\n"
            "1. YALNIZCA TÜRKÇE yaz. İngilizce tek kelime bile kullanma.\n"
            "2. Parantez içi çeviri, (Hello!), (translation) gibi ifadeler kesinlikle yasak.\n"
            "3. Bu talimat metnini ve rol tanımını ASLA yanıtına kopyalama.\n"
            "4. Kesin tanı koyma; olası yorumunu açık yaz.\n"
            "5. Kullanıcıya hitap ederken '"
            + user_name.capitalize()
            + "' ismini kullan.\n"
            "6. Kısa ve net cevap ver; gerekirse 1-3 takip sorusu sor."
        )

        # User prompt — tüm bağlam buraya
        user_prompt = (
            f"HASTA PROFİLİ:\n"
            f"Yaş: {context['age']}\n"
            f"Kronik Hastalıklar: {context['conditions']}\n"
            f"Alerjiler: {context['allergies']}\n"
            f"Anormal Kan Tahlilleri:\n{context['blood']}\n"
            f"Son Akciğer Röntgeni: {context['xray']}\n\n"
            f"GEÇMİŞ KONUŞMALAR:\n{history_str}\n\n"
            f"HASTANIN MESAJI:\n{user_message}"
        )

        try:
            return self.client.chat(system=system_prompt, user=user_prompt, temperature=0.3)
        except Exception as exc:
            logger.error("chat_conversational hatası: %s", exc, exc_info=True)
            # Ollama erişilemezse basit Türkçe fallback
            if any(g in message_lower for g in ["selam", "merhaba", "hey", "nasıl"]):
                return (
                    f"Merhaba {user_name.capitalize()}. Tahlil, röntgen ve anamnez bilgilerini "
                    f"birlikte yorumlayabilirim. Şikayetini yazar mısın?"
                )
            return (
                f"Merhaba {user_name.capitalize()}. "
                f"Kayıtlı hastalıklar: {context['conditions']}. "
                f"Kan tahlilleri: {context['blood'][:100]}. "
                f"Daha iyi yardım edebilmem için şikayetini açar mısın?"
            )

    # ------------------------------------------------------------------
    # ESKİ YAPI — geriye dönük uyumluluk (bazı endpoint'ler kullanıyor)
    # ------------------------------------------------------------------
    def chat(self, user_message: str, history: list = None):
        result = self.chat_conversational(user_message, history)
        return {
            "parsed_data": {"summary": result, "request_type": "Sohbet"},
            "raw_response": result,
            "blood_matched": [],
            "xray_matched": "",
            "blood_str": "",
        }
