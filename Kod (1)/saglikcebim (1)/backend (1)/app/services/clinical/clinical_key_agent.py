"""
ClinicalKey Integration Agent
Tanı ve tedavi önerileri için ClinicalKey'e bağlanır.
"""

import os
import json
from typing import Dict
from typing import Any
from dotenv import load_dotenv
import requests
from langchain_core.prompts import PromptTemplate
from app.services.evidence.clinicalkey_ai_provider import ClinicalKeyAIProvider

# .env dosyasını yükle
load_dotenv()


class ClinicalKeyAgent:
    """
    ClinicalKey entegrasyonu:
    - Cookie ile oturum yönetimi
    - Tanı bazlı tedavi önerileri
    - Klinik rehberler
    """

    def __init__(self):
        self.cookie = os.getenv("CLINICALKEY_COOKIE", "") or os.getenv("CLINICAL_KEY_COOKIE", "")
        self.is_demo_mode = self.cookie == "demo-cookie"
        self.is_available = bool(self.cookie and not self.is_demo_mode)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.provider = ClinicalKeyAIProvider()

    def search_treatment_guidance(self, diagnosis: str) -> Dict[str, any]:
        """
        ClinicalKey'de tanıya göre tedavi rehberi ara
        """
        if not self.cookie:
            return self._fallback_guidance(diagnosis)

        if self.is_demo_mode:
            # Demo mode
            return self._demo_guidance(diagnosis)

        # Gerçek ClinicalKey API çağrısı (kurumsal lisans için)
        return self._fetch_from_api(diagnosis)

    def _fetch_from_api(self, diagnosis: str) -> Dict:
        """
        ClinicalKey API'sine gerçek istek
        (Kurumsal lisans gerekir)
        """
        try:
            query = (
                "Clinical overview and evidence-based management approach for "
                f"suspected condition: {diagnosis}. "
                "What are recommended diagnostic workup and treatment considerations?"
            )
            results = self.provider.search_sync(query, max_results=3)
            if results:
                overview = results[0].summary or ""
                references = [
                    {
                        "title": item.title,
                        "url": item.url,
                        "evidence_level": item.evidence_level,
                        "year": item.year,
                    }
                    for item in results[1:]
                ]
                return {
                    "source": "ClinicalKey AI",
                    "diagnosis": diagnosis,
                    "treatment": {
                        "first_line": overview,
                        "note": "Generated from ClinicalKey AI conversation stream.",
                    },
                    "references": references,
                    "success": True,
                }
        except Exception as e:
            print(f"[CLINICAL_KEY API ERROR] {e}")

        return self._fallback_guidance(diagnosis)

    def _demo_guidance(self, diagnosis: str) -> Dict:
        """
        Demo mode: Llama3 ile simüle edilmiş ClinicalKey yanıtı
        """
        prompt_template = PromptTemplate(
            input_variables=["diagnosis"],
                        template="""Sen ClinicalKey'nin Türkçe tedavi rehberi asistanısın.
            
Tanı: {diagnosis}

Sadece aşağıdaki alanları içeren TEK KATMANLI JSON döndür.
Alan değerleri string olmalı, nesne veya dizi kullanma.

İstenen alanlar:
1. etiology
2. diagnostic_criteria
3. first_line_treatment
4. complications
5. follow_up

Cevapta JSON formatında ver:
{{
  "diagnosis": "{diagnosis}",
    "etiology": "kısa ve net",
    "diagnostic_criteria": "kısa ve net",
    "first_line_treatment": "kısa ve net",
    "complications": "kısa ve net",
    "follow_up": "kısa ve net"
}}
""",
        )

        formatted_prompt = prompt_template.format(diagnosis=diagnosis)

        try:
            response_text = self._invoke_llama3(formatted_prompt)
            data = self._extract_json_object(response_text)
            if data is None:
                return self._fallback_from_text(diagnosis, response_text)

            data = self._normalize_demo_payload(data)

            return {
                "source": "ClinicalKey (Demo Mode - Llama3)",
                "diagnosis": diagnosis,
                "treatment": {
                    "etiology": data.get("etiology", ""),
                    "criteria": data.get("diagnostic_criteria", ""),
                    "first_line": data.get("first_line_treatment", ""),
                    "complications": data.get("complications", ""),
                    "follow_up": data.get("follow_up", ""),
                },
                "success": True,
            }
        except Exception as e:
            print(f"[CLINICAL_KEY DEMO ERROR] {e}")
            return self._fallback_from_text(
                diagnosis,
                "Llama3 demo yanıtı alınamadı. Ollama servisinin ve llama3 modelinin çalıştığını kontrol edin.",
            )

        return self._fallback_from_text(
            diagnosis,
            "Llama3 demo yanıtı alınamadı. Ollama servisinin ve llama3 modelinin çalıştığını kontrol edin.",
        )

    def _invoke_llama3(self, prompt: str) -> str:
        """
        Local Ollama üzerinden Llama3 isteği yap.
        """
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("response", ""))

    def _extract_json_object(self, response_text: str) -> Dict[str, Any] | None:
        """
        Llama3 çıktısından JSON nesnesini ayıkla.
        """
        import re

        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            return None

        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return None

    def _normalize_demo_payload(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Nested veya beklenmeyen demo yanıtlarını düz string alanlara indirger.
        """
        def as_text(value: Any) -> str:
            if isinstance(value, str):
                return value.strip()
            if isinstance(value, dict):
                for key in ("description", "text", "value", "summary"):
                    if key in value and value[key]:
                        return as_text(value[key])
                return json.dumps(value, ensure_ascii=False)
            if isinstance(value, list):
                return ", ".join(as_text(item) for item in value if item)
            if value is None:
                return ""
            return str(value).strip()

        treatment = data.get("treatment") if isinstance(data.get("treatment"), dict) else {}
        return {
            "diagnosis": as_text(data.get("diagnosis") or data.get("name") or ""),
            "etiology": as_text(data.get("etiology") or treatment.get("etiology") or ""),
            "diagnostic_criteria": as_text(data.get("diagnostic_criteria") or treatment.get("criteria") or treatment.get("diagnostic_criteria") or ""),
            "first_line_treatment": as_text(data.get("first_line_treatment") or treatment.get("first_line") or treatment.get("first_line_treatment") or ""),
            "complications": as_text(data.get("complications") or treatment.get("complications") or ""),
            "follow_up": as_text(data.get("follow_up") or treatment.get("follow_up") or ""),
        }

    def _fallback_from_text(self, diagnosis: str, response_text: str) -> Dict:
        """
        JSON dönmezse ham Llama3 metnini kullanıcıya taşır.
        """
        clean_text = response_text.strip() or "Llama3 yanıtı alınamadı."
        return {
            "source": "ClinicalKey (Demo Mode - Llama3)",
            "diagnosis": diagnosis,
            "treatment": {
                "first_line": clean_text,
                "note": "Yanıt yapılandırılamadı; ham Llama3 çıktısı gösterildi.",
            },
            "success": True,
        }

    def _fallback_guidance(self, diagnosis: str) -> Dict:
        """
        Fallback: Temel rehber (Cookie olmadan)
        """
        return {
            "source": "ClinicalKey (Fallback)",
            "diagnosis": diagnosis,
            "treatment": {
                "first_line": "Hasta hekimi tarafından değerlendirilmesi önerilir.",
                "note": "Tam tedavi rehberi için ClinicalKey lisansı gerekir.",
            },
            "success": False,
        }

    def get_diagnostic_criteria(self, condition: str) -> str:
        """
        Klinik tanı kriterlerini getir
        """
        result = self.search_treatment_guidance(condition)
        if result.get("success"):
            criteria = result.get("treatment", {}).get("criteria", "")
            return criteria if criteria else "Kriterler alınamadı"
        return "Tanı kriterleri için lisans gerekli"

    def get_first_line_treatment(self, diagnosis: str) -> str:
        """
        İlk basamak tedavisi önerisi
        """
        result = self.search_treatment_guidance(diagnosis)
        if result.get("success"):
            treatment = result.get("treatment", {}).get("first_line", "")
            return treatment if treatment else "Tedavi bilgisi alınamadı"
        return "Tedavi önerisi için lisans gerekli"
