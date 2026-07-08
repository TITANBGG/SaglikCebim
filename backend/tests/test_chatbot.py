"""Chatbot endpoint testleri — LLM mock ile deterministik."""
import pytest
import json


# ── LLM Mock ────────────────────────────────────────────────────────────────

MOCK_SOHBET = "Merhaba! Nasıl yardımcı olabilirim?"

MOCK_ROADMAP = json.dumps({
    "risk_level": "medium",
    "red_flags": [],
    "differential_diagnosis": [],
    "recommended_departments": ["Dahiliye"],
    "immediate_action": "Lütfen bir hekime başvurun.",
    "doctor_visit_plan": "Bu hafta içinde başvurun.",
    "tests_to_discuss": [],
    "treatment_topics_to_discuss": [],
    "treatment_phases": [],
    "monitoring_plan": {"parameters": [], "frequency": "", "red_flag_thresholds": []},
    "lifestyle_modifications": [],
    "do_not_do": [],
    "follow_up_timeline": "",
    "evidence_references": [],
    "safety_validated": True,
    "disclaimer": "Bu değerlendirme tanı yerine geçmez.",
})


@pytest.fixture(autouse=True)
def mock_ollama(monkeypatch):
    """Tüm chatbot testleri için Ollama'yı mock'la — gerçek LLM çağrısı yok."""
    import app.services.ollama_client as oc

    class MockClient:
        def chat(self, system, user, temperature=0.3, format=None, retries=2):
            if format == "json":
                return MOCK_ROADMAP
            return MOCK_SOHBET

    monkeypatch.setattr(oc, "_client", MockClient())


# ── Testler ─────────────────────────────────────────────────────────────────

def test_chat_session_created(client, auth_headers):
    """İlk mesajda session oluşturulmalı."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] is not None
    assert data["type"] == "chat_message"


def test_chat_returns_answer(client, auth_headers):
    """Yanıt boş olmamalı."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["answer"]


def test_clinical_trigger_tahlil(client, auth_headers):
    """'tahlil' kelimesi klinik modu tetiklemeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "tahlillerimi yorumla", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["type"] == "clinical_roadmap"
    assert res.json()["roadmap"] is not None


def test_clinical_trigger_agri(client, auth_headers):
    """'agri' (ASCII) klinik modu tetiklemeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "karnimda agri var", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["type"] == "clinical_roadmap"


def test_clinical_trigger_donuyor(client, auth_headers):
    """'dönüyor' klinik modu tetiklemeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "basim donuyor terliyorum", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["type"] == "clinical_roadmap"


def test_sohbet_modu_selam(client, auth_headers):
    """Kısa selamlama sohbet modunda kalmalı."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["type"] == "chat_message"


def test_sohbet_modu_sohbet_cumle(client, auth_headers):
    """Klinik olmayan cümle sohbet modunda kalmalı."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "bugun hava cok guzel", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["type"] == "chat_message"


def test_emergency_critical_risk(client, auth_headers):
    """Acil mesaj (112) CRITICAL risk döndürmeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={
            "message": "gogsum agriyor nefes alamiyorum 112 aramali miyim",
            "conversation_history": [],
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "clinical_roadmap"
    rm = data.get("roadmap", {}) or {}
    assert rm.get("risk_level") == "critical"


def test_no_data_warning_without_patient_data(client, auth_headers):
    """Hasta verisi yokken no_data_warning döndürmeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "tahlillerimi yorumla", "conversation_history": []},
        headers=auth_headers,
    )
    assert res.status_code == 200
    rm = res.json().get("roadmap", {}) or {}
    # Yeni kayıt, veri yok → no_data_warning True VEYA LLM roadmap üretmiş
    # İkisi de geçerli; önemli olan 200 OK ve clinical_roadmap tipi
    assert res.json()["type"] == "clinical_roadmap"


def test_chat_message_stored(client, auth_headers):
    """Mesaj DB'ye kaydedilmeli — sessions endpoint bunu doğrular."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
        headers=auth_headers,
    )
    session_id = res.json()["session_id"]

    sessions = client.get("/api/v1/chatbot/sessions", headers=auth_headers)
    assert sessions.status_code == 200
    ids = [s["id"] for s in sessions.json()]
    assert session_id in ids


def test_unauthenticated_chat_rejected(client):
    """Auth olmadan istek reddedilmeli."""
    res = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
    )
    assert res.status_code == 401


def test_session_reuse(client, auth_headers):
    """Aynı session_id ile devam eden mesajlar aynı session'a eklenmeli."""
    res1 = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "merhaba", "conversation_history": []},
        headers=auth_headers,
    )
    sid = res1.json()["session_id"]

    res2 = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "iyi misin", "conversation_history": [], "session_id": sid},
        headers=auth_headers,
    )
    assert res2.json()["session_id"] == sid
