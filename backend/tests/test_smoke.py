"""
Smoke Test Suite — Kritik E2E akışlar

Kapsam:
  1. Auth akışı (register → login → /me)
  2. Patient summary endpoint
  3. Anamnesis CRUD (profile, conditions, medications, allergies)
  4. Confidence calibrator (unit)
  5. Safety validator consistency rules (unit)
  6. Evidence engine smoke (no network)
  7. Roadmap fallback (LLM olmadan)
"""
import pytest
from fastapi.testclient import TestClient


# ── 1. Auth ──────────────────────────────────────────────────────────────────

class TestAuthSmoke:
    def test_register_login_me(self, client: TestClient):
        r = client.post("/auth/register", json={
            "email": "smoke@test.com", "password": "Smoke1234!", "full_name": "Smoke"
        })
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        assert token

        r2 = client.post("/auth/login", json={"email": "smoke@test.com", "password": "Smoke1234!"})
        assert r2.status_code == 200
        token2 = r2.json()["access_token"]

        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token2}"})
        assert me.status_code == 200
        assert me.json()["email"] == "smoke@test.com"

    def test_unauthorized_without_token(self, client: TestClient):
        r = client.get("/auth/me")
        assert r.status_code == 401


# ── 2. Patient Summary ────────────────────────────────────────────────────────

class TestPatientSummarySmoke:
    def test_empty_patient_summary(self, client: TestClient, auth_headers):
        r = client.get("/patient/summary/basic", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "completion_score" in data
        assert "has_profile" in data
        assert "has_lab" in data
        assert "has_radiology" in data
        assert "missing_modalities" in data
        # Yeni kullanıcı: tüm modüller eksik, skor 0
        assert data["completion_score"] == 0
        assert set(data["missing_modalities"]) == {"anamnez", "kan_tahlili", "radyoloji"}

    def test_unauthorized_summary(self, client: TestClient):
        r = client.get("/patient/summary/basic")
        assert r.status_code == 401


# ── 3. Anamnesis CRUD ─────────────────────────────────────────────────────────

class TestAnamnesisSmoke:
    def test_profile_create_and_get(self, client: TestClient, auth_headers):
        r = client.put("/api/v1/anamnesis/profile", json={
            "age": "30", "gender": "Male", "height": "175", "weight": "75", "blood_type": "A+"
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/api/v1/anamnesis/profile", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json().get("age") == "30"

    def test_condition_add_list(self, client: TestClient, auth_headers):
        r = client.post("/api/v1/anamnesis/conditions", json={
            "condition_name": "Hipertansiyon", "diagnosis_date": "2023-01-01"
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/api/v1/anamnesis/conditions", headers=auth_headers)
        assert r2.status_code == 200
        names = [c["condition_name"] for c in r2.json()]
        assert "Hipertansiyon" in names

    def test_medication_add_list(self, client: TestClient, auth_headers):
        r = client.post("/api/v1/anamnesis/medications", json={
            "medication_name": "Metformin", "dosage": "500mg"
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/api/v1/anamnesis/medications", headers=auth_headers)
        assert r2.status_code == 200
        assert any(m["medication_name"] == "Metformin" for m in r2.json())

    def test_allergy_add_list(self, client: TestClient, auth_headers):
        r = client.post("/api/v1/anamnesis/allergies", json={
            "allergen_name": "Penisilin", "reaction_type": "Anafilaksi"
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/api/v1/anamnesis/allergies", headers=auth_headers)
        assert r2.status_code == 200
        assert any(a["allergen_name"] == "Penisilin" for a in r2.json())

    def test_summary_score_after_profile(self, client: TestClient, auth_headers):
        """Profil doldurulduktan sonra completion_score > 0 olmalı."""
        client.put("/api/v1/anamnesis/profile", json={
            "age": "25", "gender": "Female", "height": "165", "weight": "60"
        }, headers=auth_headers)

        r = client.get("/patient/summary/basic", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["completion_score"] >= 34
        assert "anamnez" not in data["missing_modalities"]


# ── 4. Confidence Calibrator (unit) ──────────────────────────────────────────

class TestConfidenceCalibrator:
    def test_platt_scaling_monotonic(self):
        """high > medium > low kalibre edilmiş skorlar."""
        from app.services.clinical.confidence_calibrator import _platt_scale, _LABEL_SCORE
        scores = {label: _platt_scale(raw) for label, raw in _LABEL_SCORE.items()}
        assert scores["high"] > scores["medium"] > scores["low"]

    def test_calibrated_scores_in_range(self):
        from app.services.clinical.confidence_calibrator import _platt_scale, _LABEL_SCORE
        for raw in _LABEL_SCORE.values():
            s = _platt_scale(raw)
            assert 0.0 <= s <= 1.0

    def test_calibrate_ddx_sets_fields(self):
        from app.services.clinical.confidence_calibrator import calibrate_ddx
        from app.services.clinical.schemas import DDxItem

        items = [
            DDxItem(condition="Pnömoni", confidence="high", supporting_findings=[], against_findings=[], missing_information=[]),
            DDxItem(condition="Bronşit", confidence="low", supporting_findings=[], against_findings=[], missing_information=[]),
        ]
        calibrate_ddx(items, [])
        for item in items:
            assert item.raw_confidence is not None
            assert item.calibrated_confidence is not None
            assert item.evidence_support_score is not None
            assert 0.0 <= item.calibrated_confidence <= 1.0

    def test_evidence_boost_increases_score(self):
        from app.services.clinical.confidence_calibrator import calibrate_ddx
        from app.services.clinical.schemas import DDxItem, EvidenceRef

        item_no_evidence = DDxItem(condition="Pnömoni", confidence="medium",
                                   supporting_findings=[], against_findings=[], missing_information=[])
        item_with_evidence = DDxItem(condition="Pnömoni", confidence="medium",
                                     supporting_findings=[], against_findings=[], missing_information=[])

        refs = [EvidenceRef(source="PubMed", title="Community-acquired Pneumonia treatment")]
        calibrate_ddx([item_no_evidence], [])
        calibrate_ddx([item_with_evidence], refs)

        assert item_with_evidence.calibrated_confidence >= item_no_evidence.calibrated_confidence


# ── 5. Safety Validator (unit) ────────────────────────────────────────────────

class TestSafetyValidatorSmoke:
    def _make_roadmap(self, **kwargs):
        from app.services.clinical.schemas import ClinicalRoadmap, MonitoringPlan
        defaults = dict(
            risk_level="medium",
            immediate_action="Aile hekimine başvurun.",
            recommended_departments=["Aile Hekimi"],
            monitoring_plan=MonitoringPlan(),
            disclaimer="Test",
        )
        defaults.update(kwargs)
        return ClinicalRoadmap(**defaults)

    def test_clean_roadmap_passes(self):
        from app.services.clinical.safety_validator import validate
        roadmap = self._make_roadmap()
        is_valid, violations = validate(roadmap)
        assert is_valid
        assert violations == []

    def test_forbidden_pattern_detected(self):
        from app.services.clinical.safety_validator import validate
        roadmap = self._make_roadmap(
            immediate_action="Günde 2 defa 500mg alın."
        )
        is_valid, violations = validate(roadmap)
        assert not is_valid
        assert any("forbidden_pattern" in v for v in violations)

    def test_consistency_low_risk_many_red_flags(self):
        from app.services.clinical.safety_validator import check_consistency
        roadmap = self._make_roadmap(
            risk_level="low",
            red_flags=["Ateş", "Nefes darlığı", "Göğüs ağrısı", "Bayılma"],
        )
        warnings = check_consistency(roadmap)
        assert "low_risk_but_many_red_flags" in warnings

    def test_consistency_high_risk_missing_do_not_do(self):
        from app.services.clinical.safety_validator import check_consistency
        roadmap = self._make_roadmap(risk_level="high", do_not_do=[])
        warnings = check_consistency(roadmap)
        assert "high_risk_missing_do_not_do" in warnings


# ── 6. Evidence Engine (no network) ──────────────────────────────────────────

class TestEvidenceEngineSmoke:
    def test_engine_instantiates(self):
        from app.services.evidence.engine import EvidenceEngine
        engine = EvidenceEngine()
        assert engine is not None
        assert hasattr(engine, "search_all")

    def test_bm25_reranking_unit(self):
        from app.services.evidence.pubmed_provider import PubMedProvider
        from app.services.evidence.base import EvidenceResult

        provider = PubMedProvider()
        results = [
            EvidenceResult(source="PubMed", title="Pneumonia antibiotic treatment guidelines", summary="Clinical trial results"),
            EvidenceResult(source="PubMed", title="Hypertension blood pressure management", summary="Review article"),
            EvidenceResult(source="PubMed", title="Pneumonia chest X-ray findings", summary="Diagnostic imaging"),
        ]
        reranked = provider._rerank("pneumonia treatment", results, top_k=2)
        assert len(reranked) == 2
        # Pnömoni ile ilgili olanlar üstte olmalı
        titles = [r.title for r in reranked]
        assert any("Pneumonia" in t for t in titles)


# ── 7. Roadmap Fallback (no LLM) ─────────────────────────────────────────────

class TestRoadmapFallbackSmoke:
    def test_fallback_roadmap_valid_schema(self):
        from app.services.clinical.roadmap_generator import fallback_roadmap
        roadmap = fallback_roadmap()
        assert roadmap.risk_level in ("low", "medium", "high", "critical")
        assert isinstance(roadmap.recommended_departments, list)
        assert roadmap.disclaimer

    def test_safe_fallback_valid_schema(self):
        from app.services.clinical.roadmap_generator import safe_fallback
        roadmap = safe_fallback()
        assert roadmap.risk_level is not None
        assert "hekime" in roadmap.disclaimer.lower()
