import pytest

from app.services.clinical.schemas import ClinicalRoadmap, MonitoringPlan
from app.services.clinical.safety_validator import validate, check_consistency


def test_forbidden_pattern_detected():
    roadmap = ClinicalRoadmap(
        risk_level="medium",
        red_flags=[],
        differential_diagnosis=[],
        recommended_departments=[],
        immediate_action="Günde 2 tablet kullanın",
        doctor_visit_plan="",
        tests_to_discuss=[],
        treatment_topics_to_discuss=["Aspirin başlangıcı"],
        treatment_phases=[],
        monitoring_plan=MonitoringPlan(parameters=[], frequency="", red_flag_thresholds=[]),
        lifestyle_modifications=[],
        do_not_do=[],
        follow_up_timeline="",
        evidence_references=[],
        safety_validated=False,
    )

    ok, violations = validate(roadmap)
    assert not ok
    assert any("forbidden_pattern" in v for v in violations)


def test_critical_requires_emergency_action():
    roadmap = ClinicalRoadmap(
        risk_level="critical",
        red_flags=["şiddetli göğüs ağrısı"],
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

    ok, violations = validate(roadmap)
    assert not ok
    assert any("critical_risk_without_emergency_action" in v for v in violations)


def test_treatment_without_evidence_adds_disclaimer(monkeypatch):
    """Kanıt kaynağı yokken violation yerine disclaimer notu ekleniyor (yeni davranış)."""
    roadmap = ClinicalRoadmap(
        risk_level="medium",
        red_flags=[],
        differential_diagnosis=[],
        recommended_departments=[],
        immediate_action="Lütfen hekime başvurun",
        doctor_visit_plan="",
        tests_to_discuss=[],
        treatment_topics_to_discuss=["Antibiyotik tedavisi"],
        treatment_phases=[],
        monitoring_plan=MonitoringPlan(parameters=[], frequency="", red_flag_thresholds=[]),
        lifestyle_modifications=[],
        do_not_do=[],
        follow_up_timeline="",
        evidence_references=[],
        safety_validated=False,
    )
    ok, violations = validate(roadmap)
    # Artık violation değil — disclaimer'a not ekleniyor
    assert ok is True
    assert not any("treatment_topics_without_evidence" in v for v in violations)
    # Disclaimer notu eklenmiş olmalı
    assert "kanıt" in roadmap.disclaimer.lower() or "erişilemedi" in roadmap.disclaimer.lower()


def test_check_consistency_low_risk_many_red_flags():
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
    assert any('low_risk_but_many_red_flags' in w for w in warnings)
