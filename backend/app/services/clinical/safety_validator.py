import re
from app.services.clinical.schemas import ClinicalRoadmap, TreatmentPhase

FORBIDDEN_PATTERNS = [
    r"\b\d+\s*(mg|ml|mcg|ünite|tablet|kapsül)\b",
    r"\bgünde\s+\d+\s*(kez|defa|tablet)\b",
    r"\b(amoksisilin|augmentin|metformin|aspirin|ibuprofen|parol|coumadin|warfarin)\b",
    r"kesin(likle)?\s+(teşhis|tanı|zatürre|diyabet|kanser|enfarktüs)",
    r"doktora\s+gerek\s+yok",
    r"antibiyotik\s+(başla|al|kullan|iç)",
    r"(ilaç|tedavi)\s+(yaz|ver|başlat|kes)",
    r"reçete",
    r"evde\s+tedavi\s+edebilirsiniz",
    r"hastaneye\s+gitme(nize)?\s+gerek\s+yok",
]

EMERGENCY_KEYWORDS = [
    "göğüs ağrısı", "nefes darlığı", "bilinç", "felç",
    "inme", "kalp", "kan kusma", "siyah dışkı", "intihar"
]


def validate(roadmap: ClinicalRoadmap) -> tuple[bool, list[str]]:
    violations: list[str] = []
    raw = roadmap.model_dump_json().lower()

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, raw, re.IGNORECASE):
            violations.append(f"forbidden_pattern: {pattern}")

    if roadmap.red_flags:
        emergency_referral_exists = any(
            "acil" in item.lower() or "112" in item
            for item in roadmap.recommended_departments + [roadmap.immediate_action]
        )
        if not emergency_referral_exists and roadmap.risk_level in ("high", "critical"):
            violations.append("red_flag_without_emergency_referral")

    if roadmap.risk_level == "critical":
        if "acil" not in roadmap.immediate_action.lower() and "112" not in roadmap.immediate_action:
            violations.append("critical_risk_without_emergency_action")

    if roadmap.treatment_topics_to_discuss and not roadmap.evidence_references:
        # Kanıt kaynağı bulunamadıysa analizi silmek yerine disclaimer'a not ekle
        roadmap.disclaimer += " (Kanıt kaynakları bu sorguda erişilemedi; öneriler genel tıp bilgisine dayanmaktadır.)"

    return len(violations) == 0, violations


def check_consistency(roadmap: ClinicalRoadmap) -> list[str]:
    """
    Semantik tutarlılık kuralları.
    Her kural: (koşul, violation_key) çifti.
    """
    warnings: list[str] = []
    action_lower = roadmap.immediate_action.lower()
    depts_lower  = " ".join(roadmap.recommended_departments).lower()

    # Kural 1: Düşük risk + çok kırmızı bayrak çelişkisi
    if roadmap.risk_level == "low" and len(roadmap.red_flags) > 2:
        warnings.append("low_risk_but_many_red_flags")

    # Kural 2: Yüksek/kritik risk ama "yapılmaması gerekenler" boş
    if roadmap.risk_level in ("high", "critical") and not roadmap.do_not_do:
        warnings.append("high_risk_missing_do_not_do")

    # Kural 3: Kritik risk ama immediate_action boş veya muğlak
    if roadmap.risk_level == "critical" and len(action_lower.strip()) < 10:
        warnings.append("critical_risk_empty_immediate_action")

    # Kural 4: Tedavi önerileri var ama hiç bölüm yönlendirmesi yok
    if roadmap.treatment_topics_to_discuss and not roadmap.recommended_departments:
        warnings.append("treatment_topics_without_department_referral")

    # Kural 5: Yüksek risk ama "bekle/gözlemle" tipi muğlak eylem
    _wait_words = ["gözlemle", "bekleyin", "birkaç gün", "bir süre bekle", "bekleme süresi"]
    if roadmap.risk_level in ("high", "critical") and any(w in action_lower for w in _wait_words):
        warnings.append("high_risk_with_wait_and_see_action")

    # Kural 6: Kırmızı bayrak var ama acil bölüm yok
    if roadmap.red_flags and "acil" not in depts_lower and roadmap.risk_level in ("high", "critical"):
        warnings.append("red_flags_without_emergency_department")

    # Kural 7: Diferansiyel tanı var ama güven skoru çok düşük (boş veya "low")
    # Sadece risk_level high/critical'da geçerli
    if (
        roadmap.risk_level in ("high", "critical")
        and roadmap.differential_diagnosis
        and all(
            getattr(d, "confidence", "medium") in ("low", None, "")
            for d in roadmap.differential_diagnosis
        )
    ):
        warnings.append("high_risk_all_ddx_low_confidence")

    return warnings


class SafetyValidator:
    FORBIDDEN_PATTERNS = FORBIDDEN_PATTERNS
    EMERGENCY_KEYWORDS = EMERGENCY_KEYWORDS

    def validate(self, roadmap: ClinicalRoadmap) -> ClinicalRoadmap:
        is_valid, violations = validate(roadmap)
        consistency_warnings = check_consistency(roadmap)
        all_violations = violations + [f"consistency_warning: {w}" for w in consistency_warnings]

        if all_violations:
            roadmap.safety_validated = False
            roadmap.safety_violations = all_violations

            if roadmap.risk_level == "critical":
                has_emergency_action = (
                    "acil" in roadmap.immediate_action.lower() or "112" in roadmap.immediate_action
                )
                if not has_emergency_action:
                    roadmap.red_flags.insert(
                        0,
                        "🚨 DİKKAT: Belirtileriniz kritik seviyededir. Derhal 112'yi arayınız.",
                    )
                    if not roadmap.treatment_phases:
                        roadmap.treatment_phases.append(
                            TreatmentPhase(
                                phase="immediate",
                                timeframe="Hemen",
                                actions=["Acil servise başvurun."],
                            )
                        )
                    else:
                        roadmap.treatment_phases[0].actions.insert(
                            0,
                            "Lütfen en yakın acil servise başvurun.",
                        )

            if any("forbidden_pattern" in violation for violation in violations):
                roadmap.do_not_do.insert(
                    0,
                    "Yapay zeka analizinde teknik bir ihlal saptanmıştır; bu analizdeki dozaj/ilaç bilgilerini dikkate almayınız.",
                )
        else:
            roadmap.safety_validated = True
            roadmap.safety_violations = []

        return roadmap
