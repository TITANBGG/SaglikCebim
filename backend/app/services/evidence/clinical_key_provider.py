import os
from typing import Any, Dict, List

import requests

from app.services.evidence.base import EvidenceProvider
from app.services.evidence.query_builder import QueryBuilder


class ClinicalKeyProvider(EvidenceProvider):
    """
    Elsevier ClinicalKey AI entegrasyonu.
    Akademik makaleler yerine dogrudan klinik tani ve tedavi ozetleri sunar.

    Yontem: .env icindeki CLINICAL_KEY_COOKIE ile mevcut oturumun test edilmesi.
    """

    def __init__(self):
        self.cookie = os.getenv("CLINICAL_KEY_COOKIE", "").strip()
        self.base_url = "https://www.clinicalkey.com/api/search/ai"

    def search_evidence(self, diagnosis_name: str, max_results: int = 1) -> List[str]:
        """
        ClinicalKey AI'dan profesyonel klinik ozet ceker.
        Donen deger, frontend'in 'Klinik Gorus' alaninda gosterecegi metindir.
        """
        return self._call_clinical_key(
            diagnosis_name,
            context="Professional clinical decision support",
            prefix="[ClinicalKey AI]",
        )

    def search_treatment_guidance(self, diagnosis_name: str, max_results: int = 1) -> List[str]:
        """
        ClinicalKey uzerinden genel tedavi yaklasimi bilgisi ceker.
        Ilac dozu/recete uretmez; sunumda karar destek ozetini gostermek icindir.
        """
        treatment_query = (
            f"{diagnosis_name} treatment management guideline clinical approach "
            "first line management red flags follow up"
        )
        return self._call_clinical_key(
            treatment_query,
            context=(
                "Professional clinical treatment overview. Provide general management, "
                "red flags, follow-up and referral points. Do not provide medication doses "
                "or patient-specific prescriptions."
            ),
            prefix="[ClinicalKey Treatment]",
        )

    def _call_clinical_key(self, query: str, context: str, prefix: str) -> List[str]:
        if not self._has_configured_cookie():
            return [
                "[CLINICAL_KEY] Aktif bir ClinicalKey cookie degeri bulunamadi. "
                "backend (1)/.env icindeki CLINICAL_KEY_COOKIE alanini doldurun."
            ]

        english_query = QueryBuilder.build_english_query(query)

        headers = {
            "Cookie": self.cookie,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        payload = {
            "query": english_query,
            "context": context,
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                answer = self._extract_answer_text(data)
                if answer:
                    return [f"{prefix}: {answer}"]

                return [
                    "[CLINICAL_KEY] ClinicalKey yaniti geldi ama beklenen "
                    "answer.text alani bulunamadi."
                ]

            if response.status_code in (401, 403):
                return [
                    "[CLINICAL_KEY] Cookie reddedildi veya oturum suresi doldu. "
                    "ClinicalKey'e tarayicida tekrar giris yapip yeni cookie alin."
                ]

            return [
                "[CLINICAL_KEY] ClinicalKey beklenmeyen HTTP yaniti dondu. "
                f"HTTP {response.status_code}: {response.text[:300]}"
            ]

        except Exception as e:
            print(f"[CLINICAL_KEY ERROR] Baglanti Hatasi: {e}")
            return [
                "[ClinicalKey AI]: Servis su an mesgul veya ag baglantisi yok. "
                "Lutfen PubMed referanslarini inceleyin."
            ]

    def get_structured_insight(self, diagnosis_name: str) -> Dict[str, Any]:
        """
        Daha yapilandirilmis veri donen gelismis metod.
        """
        results = self.search_evidence(diagnosis_name)
        return {
            "provider": "Elsevier ClinicalKey",
            "configured": self._has_configured_cookie(),
            "insight": results[0] if results else "Veri alinamadi.",
        }

    def _has_configured_cookie(self) -> bool:
        placeholders = {
            "",
            "your-clinical-key-cookie-here",
            "buraya_cookie_degerin",
            "senin_cookie_degerin",
        }
        return self.cookie.lower() not in placeholders

    @staticmethod
    def _extract_answer_text(data: Dict[str, Any]) -> str:
        answer = data.get("answer")
        if isinstance(answer, dict):
            text = answer.get("text")
            if isinstance(text, str):
                return text.strip()

        for key in ("text", "summary", "insight"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return ""
