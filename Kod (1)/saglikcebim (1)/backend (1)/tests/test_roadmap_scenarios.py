"""
Roadmap Generator senaryoları — yeni mimari (symptom_smart_fallback + LLM personalization).

Yeni akış:
  1. symptom_smart_fallback → temel yapı (garanti çalışır)
  2. Hasta verisi varsa → _personalize_with_llm (basit metin format)
  3. LLM yanıtı merge edilir — risk sadece artar, asla düşmez
"""
from app.services.clinical.roadmap_generator import RoadmapGenerator, symptom_smart_fallback
from app.services.clinical.safety_validator import check_consistency
from app.services.clinical.schemas import ClinicalRoadmap, MonitoringPlan


class _FakeLLM:
    """LLM mock — yeni yapılandırılmış metin formatında yanıt döndürür."""

    def __init__(self, risk: str = "ORTA", uyarilar: str = "YOK",
                 tekikler: str = "YOK", yorum: str = "YOK", soru: str = "YOK"):
        self.risk = risk
        self.uyarilar = uyarilar
        self.tekikler = tekikler
        self.yorum = yorum
        self.soru = soru

    def chat(self, system=None, user=None, temperature=0, format=None, retries=2) -> str:
        return (
            f"RİSK: {self.risk}\n"
            f"UYARILAR: {self.uyarilar}\n"
            f"TEKİKLER: {self.tekikler}\n"
            f"YORUM: {self.yorum}\n"
            f"SORU: {self.soru}"
        )


def _base_context() -> dict:
    return {
        "current_message": "Göğüs ağrısı ve nefes darlığı var",
        "medical_history": "Kronik Hastalıklar: Hipertansiyon\nAlerjiler: Yok\nMevcut İlaçlar: Yok",
        "lab_anomalies": "Troponin: 0.8 (ref 0-0.04) [HIGH]",
    }


def _no_data_context() -> dict:
    return {"current_message": "başım ağrıyor"}


# ── Temel yapı testleri ──────────────────────────────────────────────────────

def test_smart_fallback_cardiac_keywords():
    """Kardiyak kelime → HIGH risk ve kardiyoloji."""
    rm = symptom_smart_fallback("kalbim ağrıyor çarpıntı var")
    assert rm.risk_level == "high"
    assert any("ardiyoloji" in d for d in rm.recommended_departments)


def test_smart_fallback_neuro_keywords():
    """Nörolojik kelime → MEDIUM risk ve nöroloji."""
    rm = symptom_smart_fallback("başım dönüyor sersemlik var")
    assert rm.risk_level == "medium"
    assert rm.tests_to_discuss  # en az 1 tetkik önerilmeli


def test_smart_fallback_always_has_tests():
    """Her fallback sonucunda tetkik önerisi olmalı."""
    for msg in ["mide ağrım var", "nefes darlığım var", "yorgunluk ve halsizlik"]:
        rm = symptom_smart_fallback(msg)
        assert rm.tests_to_discuss, f"Tetkik yok: {msg}"


def test_smart_fallback_safety_validated():
    """symptom_smart_fallback her zaman safety_validated=True döndürmeli."""
    rm = symptom_smart_fallback("başım ağrıyor")
    assert rm.safety_validated is True


# ── Hasta verisi olmadan ─────────────────────────────────────────────────────

def test_generate_no_patient_data_uses_base(monkeypatch):
    """Hasta verisi yoksa temel fallback döner, LLM çağrılmaz."""
    call_count = {"n": 0}

    class CountingLLM:
        def chat(self, **_):
            call_count["n"] += 1
            return "RİSK: ORTA\nUYARILAR: YOK\nTEKİKLER: YOK\nYORUM: YOK\nSORU: YOK"

    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client", CountingLLM())
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_no_data_context())
    assert call_count["n"] == 0  # LLM çağrılmamalı
    assert roadmap.safety_validated is True


# ── Kişiselleştirme testleri ─────────────────────────────────────────────────

def test_personalization_risk_escalation(monkeypatch):
    """LLM KRİTİK dönünce risk yükselir."""
    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client", _FakeLLM(risk="KRİTİK", uyarilar="Troponin yüksek"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert roadmap.risk_level == "critical"


def test_personalization_risk_never_decreases(monkeypatch):
    """LLM düşük risk dönse bile temel risk seviyesi korunur."""
    gen = RoadmapGenerator()
    # Kardiyak mesaj → base risk=high; LLM DÜŞÜK dönüyor
    monkeypatch.setattr(gen, "_client", _FakeLLM(risk="DÜŞÜK"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    ctx = {**_base_context(), "current_message": "kalbim ağrıyor göğsüm sıkıyor"}
    roadmap = gen.generate(ctx)
    assert roadmap.risk_level in ("high", "critical")  # Asla low olmamalı


def test_personalization_adds_patient_specific_tests(monkeypatch):
    """LLM'den gelen testler roadmap'e eklenir."""
    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client",
                        _FakeLLM(risk="YÜKSEK", tekikler="Troponin I | Ekokardiyografi"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert "Troponin I" in roadmap.tests_to_discuss
    assert "Ekokardiyografi" in roadmap.tests_to_discuss


def test_personalization_adds_warnings_as_red_flags(monkeypatch):
    """LLM'den gelen hasta özel uyarılar red_flags'e eklenir."""
    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client",
                        _FakeLLM(risk="YÜKSEK", uyarilar="Hipertansiyonlu hastada kardiyak risk artmış"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert any("ipertansiyon" in f or "ardiyak" in f for f in roadmap.red_flags)


def test_personalization_adds_comment_to_topics(monkeypatch):
    """LLM yorumu treatment_topics_to_discuss'a eklenir."""
    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client",
                        _FakeLLM(risk="YÜKSEK", yorum="Diyabetik hastada troponin yüksekliği acil değerlendirme gerektirir"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert any("iyabetik" in t or "roponin" in t for t in roadmap.treatment_topics_to_discuss)


def test_personalization_question_added_to_plan(monkeypatch):
    """LLM'in sorduğu soru doctor_visit_plan'a eklenir."""
    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client",
                        _FakeLLM(risk="ORTA", soru="Ağrı sol kola yayılıyor mu?"))
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert "sol kola" in roadmap.doctor_visit_plan.lower()


def test_personalization_llm_failure_returns_base(monkeypatch):
    """LLM başarısız olunca temel fallback döner, hata fırlatılmaz."""

    class BrokenLLM:
        def chat(self, **_):
            raise ConnectionError("Ollama bağlantı hatası")

    gen = RoadmapGenerator()
    monkeypatch.setattr(gen, "_client", BrokenLLM())
    monkeypatch.setattr(gen, "_fetch_evidence", lambda _: None)

    roadmap = gen.generate(_base_context())
    assert roadmap is not None
    assert roadmap.recommended_departments  # Temel yapı korunmalı


# ── Tutarlılık testleri ──────────────────────────────────────────────────────

def test_scenario_low_risk_consistency_warning():
    """LOW risk + çok kırmızı bayrak → tutarsızlık uyarısı."""
    roadmap = ClinicalRoadmap(
        risk_level="low",
        red_flags=["a", "b", "c"],
        differential_diagnosis=[],
        recommended_departments=[],
        immediate_action="",
        doctor_visit_plan="",
        tests_to_discuss=[],
        treatment_topics_to_discuss=[],
        treatment_phases=[],
        monitoring_plan=MonitoringPlan(parameters=[], frequency="", red_flag_thresholds=[]),
        lifestyle_modifications=[],
        do_not_do=[],
        follow_up_timeline="",
        evidence_references=[],
        safety_validated=False,
    )

    warnings = check_consistency(roadmap)
    assert "low_risk_but_many_red_flags" in warnings
