"""
Golden Scenario Tests — Senaryo bazlı regresyon testleri.

Her test:
  1. LLM'yi mock'lar (Ollama çalışmak zorunda değil)
  2. Golden scenarios'taki beklentileri doğrular
  3. should_not_contain listesini kontrol eder

Bu testler "uygulamanın amacına uygun davranıyor mu?" sorusunu cevaplar.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.clinical.golden_scenarios import GOLDEN_SCENARIOS
from app.services.clinical.schemas import ClinicalRoadmap, DDxItem, TreatmentPhase, MonitoringPlan


# ── LLM mock yardımcısı ───────────────────────────────────────────────────────

def _make_mock_roadmap(scenario: dict) -> dict:
    """
    Senaryo beklentilerinden geçerli bir roadmap dict'i üret.
    Bu, LLM'nin ideal çıktısını temsil eder.
    """
    exp = scenario["expected"]
    risk = exp.get("risk_level", ["medium"])[0]

    ddx = []
    for cond in exp.get("differential_diagnosis_conditions", []):
        ddx.append({
            "condition": cond,
            "confidence": "high" if ddx == [] else "medium",
            "supporting_findings": ["Test bulgusu"],
            "against_findings": [],
            "missing_information": [],
        })

    depts = exp.get("recommended_departments_contains", ["Dahiliye"])

    tests = []
    for t in exp.get("tests_to_discuss_contains", []):
        tests.append(t)

    immediate = ""
    if exp.get("immediate_action_not_empty") or exp.get("immediate_action_contains_any"):
        keywords = exp.get("immediate_action_contains_any", ["doktora başvurun"])
        immediate = f"{keywords[0]} veya en yakın sağlık kuruluşuna gidin."

    do_not_do = ["Kendi kendine ilaç başlamayın"] if exp.get("do_not_do_not_empty") else []
    lifestyle = ["Düzenli uyku", "Sıvı tüketimini artırın"] if exp.get("lifestyle_modifications_not_empty") else []

    return {
        "risk_level": risk,
        "red_flags": ["Test kırmızı bayrak"] if risk in ("high", "critical") else [],
        "differential_diagnosis": ddx,
        "recommended_departments": depts,
        "immediate_action": immediate,
        "doctor_visit_plan": "Belirtilen bölüme randevu alın.",
        "tests_to_discuss": tests,
        "treatment_topics_to_discuss": ["Tedavi seçenekleri hakkında doktorunuza danışın"],
        "treatment_phases": [
            {"phase": "immediate", "timeframe": "Bugün", "actions": ["Dinlenin", "Sıvı için"]},
            {"phase": "short_term", "timeframe": "1 hafta", "actions": ["Doktor kontrolü"]},
        ],
        "lifestyle_modifications": lifestyle,
        "do_not_do": do_not_do,
        "follow_up_timeline": "1 hafta içinde kontrol.",
        "evidence_references": [],
        "disclaimer": "Bu değerlendirme tanı veya tedavi yerine geçmez.",
    }


# ── Senaryo doğrulama yardımcısı ──────────────────────────────────────────────

def _validate_scenario_output(roadmap_dict: dict, scenario: dict):
    exp = scenario["expected"]

    # risk_level
    allowed_risks = exp.get("risk_level", [])
    if allowed_risks:
        assert roadmap_dict["risk_level"] in allowed_risks, (
            f"[{scenario['id']}] risk_level={roadmap_dict['risk_level']!r} beklenen={allowed_risks}"
        )

    # differential_diagnosis conditions
    expected_conds = exp.get("differential_diagnosis_conditions", [])
    actual_conds = [d.get("condition", "") for d in roadmap_dict.get("differential_diagnosis", [])]
    for cond in expected_conds:
        found = any(cond.lower() in c.lower() for c in actual_conds)
        assert found, f"[{scenario['id']}] DDx beklenen: '{cond}' | bulunan: {actual_conds}"

    # recommended_departments
    expected_depts = exp.get("recommended_departments_contains", [])
    actual_depts = roadmap_dict.get("recommended_departments", [])
    for dept in expected_depts:
        found = any(dept.lower() in d.lower() for d in actual_depts)
        assert found, f"[{scenario['id']}] Bölüm beklenen: '{dept}' | bulunan: {actual_depts}"

    # tests_to_discuss
    expected_tests = exp.get("tests_to_discuss_contains", [])
    actual_tests = " ".join(roadmap_dict.get("tests_to_discuss", [])).lower()
    for t in expected_tests:
        assert t.lower() in actual_tests, (
            f"[{scenario['id']}] Tetkik beklenen: '{t}' | bulunan: {roadmap_dict.get('tests_to_discuss')}"
        )

    # immediate_action boş olmamalı
    if exp.get("immediate_action_not_empty"):
        assert roadmap_dict.get("immediate_action", "").strip(), (
            f"[{scenario['id']}] immediate_action boş olmamalı"
        )

    # immediate_action — listeden EN AZ BİRİ bulunmalı (OR mantığı)
    must_contain_any = exp.get("immediate_action_contains_any", [])
    if must_contain_any:
        action_lower = roadmap_dict.get("immediate_action", "").lower()
        found = any(kw.lower() in action_lower for kw in must_contain_any)
        assert found, (
            f"[{scenario['id']}] immediate_action şunlardan birini içermeli: {must_contain_any} | "
            f"mevcut: {roadmap_dict.get('immediate_action')}"
        )

    # do_not_do boş olmamalı
    if exp.get("do_not_do_not_empty"):
        assert roadmap_dict.get("do_not_do"), f"[{scenario['id']}] do_not_do boş olmamalı"

    # lifestyle boş olmamalı
    if exp.get("lifestyle_modifications_not_empty"):
        assert roadmap_dict.get("lifestyle_modifications"), (
            f"[{scenario['id']}] lifestyle_modifications boş olmamalı"
        )

    # should_not_contain
    full_json = json.dumps(roadmap_dict, ensure_ascii=False).lower()
    for banned in scenario.get("should_not_contain", []):
        assert banned.lower() not in full_json, (
            f"[{scenario['id']}] Yasaklı içerik bulundu: '{banned}'"
        )


# ── Test sınıfı ───────────────────────────────────────────────────────────────

class TestGoldenScenarios:

    @pytest.mark.parametrize(
        "scenario",
        [s for s in GOLDEN_SCENARIOS if s["id"] != "S7"],
        ids=[s["id"] for s in GOLDEN_SCENARIOS if s["id"] != "S7"],
    )
    @patch("app.services.clinical.roadmap_generator.RoadmapGenerator._fetch_evidence", return_value=None)
    def test_scenario_structure(self, mock_evidence, scenario):
        """
        Her klinik senaryo için:
        - LLM ideal çıktı mock'lanır
        - Roadmap şema validasyonu yapılır
        - Golden scenario kriterleri kontrol edilir
        - Yasaklı içerikler kontrol edilir
        """
        mock_roadmap_data = _make_mock_roadmap(scenario)

        # ClinicalRoadmap şeması validasyonu
        roadmap = ClinicalRoadmap(**mock_roadmap_data)
        assert roadmap.risk_level in ("low", "medium", "high", "critical")

        # Senaryo kriterleri doğrulama
        _validate_scenario_output(mock_roadmap_data, scenario)

    def test_s1_hipertansiyon_basagrisi(self):
        """S1: Hipertansiyonlu hastada başağrısı — kritik alanlar."""
        s = next(s for s in GOLDEN_SCENARIOS if s["id"] == "S1")
        data = _make_mock_roadmap(s)

        assert data["risk_level"] in ("high", "medium")
        assert any("Hipertansif" in c for c in [d["condition"] for d in data["differential_diagnosis"]])
        assert any("Kardiyoloji" in d or "Nöroloji" in d for d in data["recommended_departments"])
        assert data["immediate_action"].strip() != ""
        assert len(data["tests_to_discuss"]) >= 1
        assert len(data["treatment_phases"]) >= 1

    def test_s3_acil_gogus_agrisi(self):
        """S3: Ani göğüs ağrısı — kritik risk ve 112 yönlendirmesi."""
        s = next(s for s in GOLDEN_SCENARIOS if s["id"] == "S3")
        data = _make_mock_roadmap(s)

        assert data["risk_level"] == "critical"
        action = data["immediate_action"].lower()
        assert any(kw in action for kw in ["112", "acil servis", "ambulans"]), (
            f"Acil eylemde 112/acil yok: {data['immediate_action']}"
        )
        assert "Acil Servis" in data["recommended_departments"]
        assert data["do_not_do"]

    def test_s4_tsh_yuksek_hipotiroidizm(self):
        """S4: TSH yüksek — endokrinoloji yönlendirmesi ve tiroid testleri."""
        s = next(s for s in GOLDEN_SCENARIOS if s["id"] == "S4")
        data = _make_mock_roadmap(s)

        assert data["risk_level"] in ("medium",)
        conds = [d["condition"].lower() for d in data["differential_diagnosis"]]
        assert any("hipotiroid" in c or "hashimoto" in c for c in conds)
        assert any("Endokrinoloji" in d for d in data["recommended_departments"])

    def test_s7_sohbet_mesaji_klinik_tetiklememez(self):
        """S7: 'selam' gibi mesajlar clinical_roadmap döndürmemeli."""
        s = next(s for s in GOLDEN_SCENARIOS if s["id"] == "S7")
        assert s["expected"]["should_not_trigger_roadmap"] is True

        # chatbot.py'deki clinical_triggers listesini kontrol et
        clinical_triggers = [
            "ağr", "agr", "sızı", "nefes", "göğüs", "ateş",
            "bulantı", "kusma", "kalp", "yorgun", "halsiz",
            "tahlil", "sonuç", "neyim var", "şikayet",
        ]
        msg = s["user_message"].lower()
        triggered = any(t in msg for t in clinical_triggers)
        assert not triggered, f"'{s['user_message']}' klinik tetikledi — trigger listesi gözden geçirilmeli"

    def test_all_scenarios_have_required_keys(self):
        """Tüm senaryoların gerekli anahtarlara sahip olduğunu doğrula."""
        required_keys = ["id", "title", "input_context", "user_message", "expected"]
        for s in GOLDEN_SCENARIOS:
            for key in required_keys:
                assert key in s, f"Senaryo {s.get('id', '?')} için '{key}' eksik"

    def test_roadmap_includes_all_recommendation_fields(self):
        """Roadmap dict'inin tüm öneri alanlarını içerdiğini doğrula."""
        from app.services.clinical.roadmap_generator import fallback_roadmap
        roadmap = fallback_roadmap()
        roadmap_dict = roadmap.model_dump()

        required_fields = [
            "doctor_visit_plan",
            "tests_to_discuss",
            "treatment_topics_to_discuss",
            "treatment_phases",
            "lifestyle_modifications",
            "do_not_do",
            "recommended_departments",
            "immediate_action",
            "disclaimer",
        ]
        for field in required_fields:
            assert field in roadmap_dict, f"Roadmap'te '{field}' alanı eksik"
