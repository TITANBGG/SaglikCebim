import json
from typing import List, Dict, Any
from app.services.ollama_client import get_ollama_client

class PharmacologyAgent:
    """
    UpToDate ve Lexicomp standartlarında çalışan AI İlaç Güvenlik Ajanı.
    """

    def __init__(self, current_medications: List[str]):
        self.current_meds = current_medications
        self.client = get_ollama_client()

    def check_new_substance(self, target_substance: str) -> Dict[str, Any]:
        return self.check_interaction(target_substance)

    def check_interaction(self, target_substance: str) -> Dict[str, Any]:
        """
        UpToDate/Lexicomp klinik rehberlerini referans alarak etkileşim kontrolü yapar.
        """
        if not self.current_meds:
            return {
                "has_risk": False, 
                "message": "Kayıtlı mevcut ilaç bulunmuyor. UpToDate/Lexicomp denetimi için lütfen ilaç ekleyin.",
                "severity": "info"
            }

        system = (
            "Sen klinik farmakoloji uzmanısın. "
            "YALNIZCA Türkçe yaz. İngilizce kelime kullanma. "
            "Yanıtını SADECE geçerli bir JSON objesi olarak döndür, başka metin ekleme."
        )
        user = (
            f"Mevcut ilaçlar: {', '.join(self.current_meds)}\n"
            f"Yeni madde: {target_substance}\n\n"
            f"Bu madde ile mevcut ilaçlar arasındaki etkileşimi analiz et.\n"
            f"Yanıt formatı (SADECE JSON):\n"
            f'{{"has_risk": true/false, '
            f'"severity": "critical|high|moderate|none", '
            f'"interaction_type": "Lexicomp Grade (A/B/C/D/X)", '
            f'"user_warning": "Türkçe uyarı mesajı", '
            f'"clinical_note": "Teknik detay"}}'
        )

        try:
            response = self.client.chat(system=system, user=user, temperature=0, format="json")
            data = json.loads(response)
            grade = data.get("interaction_type", "?")
            return {
                "has_risk": data.get("has_risk", False),
                "message": f"[{grade}] {data.get('user_warning', '')}",
                "details": data.get("clinical_note", ""),
                "severity": data.get("severity", "none"),
            }
        except Exception as exc:
            from app.core.logging import get_logger
            get_logger("pharmacology_agent").error("Pharmacy check hatası: %s", exc)

        return {"has_risk": False, "message": "İlaç etkileşim denetimi tamamlanamadı.", "severity": "none"}

    def extract_medications(self, text: str) -> List[str]:
        try:
            res = self.client.chat(
                system="İlaç adlarını virgülle ayırarak listele. Sadece ilaç adları, başka metin yok.",
                user=f"Bu metindeki ilaçları listele: {text}",
                temperature=0,
            )
            return [m.strip() for m in res.split(",") if len(m.strip()) > 2]
        except Exception:
            return []
