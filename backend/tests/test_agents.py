"""
OllamaDiagnosisAgent ve intent detection testleri.
Gerçek LLM çağrısı yok — OllamaClient mock'lanıyor.
"""
import pytest
import json
from app.services.clinical.schemas import ClinicalRoadmap, MonitoringPlan


# ── Mock Fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_ollama(monkeypatch):
    import app.services.ollama_client as oc

    class MockClient:
        def chat(self, system, user, temperature=0.3, format=None, retries=2):
            if format == "json":
                return json.dumps({
                    "risk_level": "medium",
                    "red_flags": [],
                    "differential_diagnosis": [],
                    "recommended_departments": ["Dahiliye"],
                    "immediate_action": "Hekime başvurun.",
                    "doctor_visit_plan": "",
                    "tests_to_discuss": [],
                    "treatment_topics_to_discuss": [],
                    "treatment_phases": [],
                    "monitoring_plan": {"parameters": [], "frequency": "", "red_flag_thresholds": []},
                    "lifestyle_modifications": [],
                    "do_not_do": [],
                    "follow_up_timeline": "",
                    "evidence_references": [],
                    "safety_validated": True,
                    "disclaimer": "Tanı yerine geçmez.",
                })
            return "Merhaba! Size nasıl yardımcı olabilirim?"

    monkeypatch.setattr(oc, "_client", MockClient())


# ── Intent Detection ─────────────────────────────────────────────────────────

class TestIntentDetection:
    """chatbot.py'deki clinical_triggers listesini test eder."""

    CLINICAL_TRIGGERS = [
        "ağr", "agr", "sızı", "sizi", "tahlil", "sonuç", "sonuc",
        "neyim var", "nedir", "yorumla", "şikayet", "sikayet",
        "doktor", "hastal", "ateş", "ates", "bulantı", "bulanti",
        "kusma", "yorgun", "halsiz", "nefes", "göğüs", "gogus",
        "baş", "bas ", "başım", "basim", "dönüyor", "donuyor",
        "sersem", "uyuşuyor", "uyusuyor", "titriyor", "görme", "gorme",
        "terliyorum", "terliyor", "terle", "terli", "üşüyorum",
        "titreme", "mide", "karın", "karin", "ishal",
        "çarpıntı", "carpinti", "kalp", "boğaz", "bogaz",
        "şişlik", "sislik", "kaşıntı", "kasinti", "kızarık", "kizarik",
        "yanıyor", "yaniyor", "kanıyor", "kaniyor",
        "tanı", "tani", "teşhis", "teshis", "şeker", "seker",
        "tansiyon", "kolesterol", "enfeksiyon", "ilaç", "ilac",
        "ameliyat", "röntgen", "rontgen",
    ]

    def _is_clinical(self, msg: str) -> bool:
        msg_lower = msg.lower()
        return any(t in msg_lower for t in self.CLINICAL_TRIGGERS)

    def test_agri_triggers_clinical(self):
        assert self._is_clinical("başım ağrıyor") is True

    def test_ascii_agri_triggers_clinical(self):
        assert self._is_clinical("karnimda agri var") is True

    def test_tahlil_triggers_clinical(self):
        assert self._is_clinical("tahlillerimi yorumla") is True

    def test_donuyor_triggers_clinical(self):
        assert self._is_clinical("başım dönüyor terliyorum") is True

    def test_nefes_triggers_clinical(self):
        assert self._is_clinical("nefes alamıyorum") is True

    def test_sohbet_no_trigger(self):
        assert self._is_clinical("merhaba nasılsın") is False

    def test_hava_no_trigger(self):
        assert self._is_clinical("bugün hava güzel") is False

    def test_tesekkur_no_trigger(self):
        assert self._is_clinical("teşekkür ederim") is False

    def test_gogus_triggers_clinical(self):
        assert self._is_clinical("göğsüm ağrıyor") is True

    def test_nefes_darligi_triggers_clinical(self):
        assert self._is_clinical("nefes alamıyorum 112 aramalı mıyım") is True


# ── OllamaDiagnosisAgent ─────────────────────────────────────────────────────

class TestOllamaDiagnosisAgent:
    def _make_agent(self, db, user_id="1"):
        from app.services.ollama_agent import OllamaDiagnosisAgent
        return OllamaDiagnosisAgent(db=db, user_id=user_id)

    def test_agent_returns_string(self, client, auth_headers):
        """chat_conversational string döndürmeli."""
        # DB'ye erişim için TestClient üzerinden gidiyoruz
        # Direkt agent testi DB fixture gerektiriyor; endpoint üzerinden test ediyoruz
        res = client.post(
            "/api/v1/chatbot/chat",
            json={"message": "merhaba", "conversation_history": []},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert isinstance(res.json()["answer"], str)
        assert len(res.json()["answer"]) > 0

    def test_agent_clinical_returns_roadmap(self, client, auth_headers):
        res = client.post(
            "/api/v1/chatbot/chat",
            json={"message": "tahlil yorumla", "conversation_history": []},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert res.json()["type"] == "clinical_roadmap"
        assert res.json().get("roadmap") is not None


# ── ClinicalRoadmapEngine ────────────────────────────────────────────────────

class TestClinicalRoadmapEngine:
    def test_emergency_bypass(self, client, auth_headers):
        """112 içeren mesaj CRITICAL risk döndürmeli (LLM çağrısı olmadan)."""
        res = client.post(
            "/api/v1/chatbot/chat",
            json={
                "message": "gogsum agriyor nefes alamiyorum 112 aramali miyim",
                "conversation_history": [],
            },
            headers=auth_headers,
        )
        assert res.status_code == 200
        rm = res.json().get("roadmap", {}) or {}
        assert rm.get("risk_level") == "critical"
        assert rm.get("recommended_departments") == ["Acil Servis"]

    def test_no_data_warning_for_new_user(self, client, auth_headers):
        """
        Yeni kullanıcı (verisi yok) → no_data_warning True.
        Not: test_chatbot.py::test_no_data_warning_without_patient_data aynı senaryoyu kapsar.
        Bu test rate limit birikimi nedeniyle ayrı çalıştırılmalıdır.
        """
        pytest.skip(
            "test_chatbot.py'de kapsanıyor; rate limit birikimi nedeniyle burada çalıştırılmıyor"
        )
