from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.services.clinical.context_builder import ClinicalContextBuilder
from app.services.clinical.roadmap_generator import RoadmapGenerator, symptom_smart_fallback
from app.services.clinical.safety_validator import SafetyValidator
from app.services.clinical.clinical_key_agent import ClinicalKeyAgent
from app.core.logging import get_logger

logger = get_logger("clinical_engine")

_EMERGENCY_KEYWORDS = [
    # Genel acil
    "112", "ambulans",
    # Göğüs / kardiyak (ACS, PE, aort)
    "göğüs ağrı", "gogus agri",
    "göğsüm ağrı", "gogsum agri",
    "göğsüm sıkı", "gogsum siki",
    "göğsüm bask", "gogsum bask",   # "göğsümde baskı"
    "göğüs bask", "gogus bask",
    "sol koluma", "sol kolum",       # ACS'de yayılım
    "soğuk terleme", "soguk terleme",
    "kalp krizi", "enfarktüs", "enfarktus",
    # Nörolojik acil (İnme — FAST)
    "felç", "felc", "inme",
    "konuşmam bozuldu", "konusmam bozuldu",
    "konuşmakta zorlan", "konusmakta zorlan",
    "güçsüzlük var", "gucsuzluk var",
    "kol güçsüz", "kol gucsuz",
    "yüzüm uyuş", "yuzum uyus",
    # Solunum / anafilaksi
    "nefes alam", "nefes alamıyorum", "nefes alamiyorum",
    "nefes almakta zorlan",          # "nefes almakta zorlanıyorum"
    "boğazım şiş", "bogzim sis", "bogazim sis",
    "boğazım kapan", "bogazim kapan",
    # Obstetrik acil
    "hamileyim ve kanam", "hamileyim ve ağr",
    "gebeyim ve kanam",
    "hamileyim kanam",
    # Bilinç / senkop
    "bayıl", "bayil", "bayıldım", "bayildim",
    "bilincini kayb", "bilinci kayb",
    # Kanama
    "kan kusma", "kus kan",
    # Genel şiddetli / ani
    "çok şiddetli ağrı", "cok siddetli agri",
    "dayanılmaz ağrı", "dayanilmaz agri",
    "ani başladı", "ani basladi",
    # Psikolojik acil
    "intihar", "kendime zarar",
    "yaşamak istemiyorum", "yasamak istemiyorum",
    "ölmek istiyorum", "olmek istiyorum",
]


class ClinicalRoadmapEngine:
    """
    Saf Llama Modu + ClinicalKey Tedavi Rehberi
    """
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.context_builder = ClinicalContextBuilder(db, user_id)
        self.generator = RoadmapGenerator()
        self.validator = SafetyValidator()
        self.clinical_key_agent = ClinicalKeyAgent()

    def process_clinical_request(self, message: str, history: List[Any] | None = None) -> Dict[str, Any]:
        try:
            # 1. Bağlam Oluştur
            context = self.context_builder.build_full_context(message, history or [])

            # 2. Hasta verisi tamamen boşsa LLM çağrısı yapma
            _empty_history = context.get("medical_history", "").strip() in (
                "Kronik Hastalıklar: Yok\nAlerjiler: Yok\nMevcut İlaçlar: Yok", ""
            )
            _empty_labs = context.get("lab_anomalies", "").strip() in (
                "Anormal kan tahlili bulgusu yok.", ""
            )
            _empty_radio = context.get("radiology_findings", "").strip() in (
                "Kayıtlı radyoloji görüntüsü yok.", ""
            )
            msg_norm = (
                message.lower()
                .replace("ı", "i").replace("ğ", "g").replace("ü", "u")
                .replace("ş", "s").replace("ö", "o").replace("ç", "c")
                .replace("â", "a").replace("î", "i").replace("û", "u")
            )
            is_emergency = any(kw in msg_norm for kw in _EMERGENCY_KEYWORDS)

            if _empty_history and _empty_labs and _empty_radio and not is_emergency:
                fallback = symptom_smart_fallback(message)
                result = fallback.model_dump()
                result["no_data_warning"] = False
                result["disclaimer"] = (
                    (result.get("disclaimer") or "") +
                    " Anamnez, tahlil veya radyoloji verilerinizi ekleyerek daha kişiselleştirilmiş analiz alabilirsiniz."
                )
                return result

            if is_emergency:
                return {
                    "risk_level": "critical",
                    "red_flags": ["Acil belirti tespit edildi"],
                    "differential_diagnosis": [],
                    "recommended_departments": ["Acil Servis"],
                    "immediate_action": "HEMEN 112'yi ARAYIN veya en yakın acil servise gidin. Bu belirtiler hayatı tehdit edebilir.",
                    "treatment_guidance": None,
                    "do_not_do": ["Tek başınıza araç kullanmayın", "Beklemeyin"],
                    "no_data_warning": False,
                    "disclaimer": "Bu değerlendirme tıbbi tavsiye değildir. Acil durumda derhal 112'yi arayın.",
                }
            
            # 2. Doğrudan Llama Üretimi
            roadmap = self.generator.generate(context, original_message=message)
            
            # 3. Güvenlik Denetimi
            safe_roadmap = self.validator.validate(roadmap)
            
            # 4. ClinicalKey Tedavi Rehberi Ekle
            if safe_roadmap.differential_diagnosis:
                treatment_guidance = []
                for ddx in safe_roadmap.differential_diagnosis:
                    guidance = self.clinical_key_agent.get_first_line_treatment(ddx.condition)
                    if guidance:
                        treatment_guidance.append(f"{ddx.condition}: {guidance}")
                if treatment_guidance:
                    safe_roadmap.treatment_guidance = treatment_guidance

            return safe_roadmap.model_dump()
        except Exception as e:
            logger.error("[ENGINE ERROR] %s", e, exc_info=True)
            raise e
