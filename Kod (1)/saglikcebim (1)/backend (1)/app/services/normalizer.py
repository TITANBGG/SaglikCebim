from __future__ import annotations

import re
import unicodedata


TEST_ALIASES = {
    "hgb": "hemoglobin",
    "hb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "hglb": "hemoglobin",
    "lokosit": "wbc",
    "lokositler": "wbc",
    "leukosit": "wbc",
    "wbc": "wbc",
    "plt": "trombosit",
    "platelet": "trombosit",
    "trombosit": "trombosit",
    "glukoz": "glukoz",
    "glucose": "glukoz",
    "blood sugar": "glukoz",
    "aclik kan sekeri": "glukoz",
    "açlık kan şekeri": "glukoz",
    "cholesterol": "kolesterol",
    "kolesterol": "kolesterol",
    "ldl": "ldl",
    "hdl": "hdl",
    "trigliserid": "trigliserid",
    "triglyceride": "trigliserid",
    "tsh": "tsh",
    "crp": "crp",
    "demir": "demir",
    "ferritin": "ferritin",
    "kreatinin": "kreatinin",
    "alt": "alt",
    "ast": "ast",
    "rbc": "eritrosit",
    "eritrosit": "eritrosit",
    "hct": "hematokrit",
    "hematokrit": "hematokrit",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "rdw": "rdw",
    "uric acid": "urik asit",
    "protein": "protein",
    "glukozu": "glukoz",
}


DISPLAY_NAMES = {
    "hemoglobin": "Hemoglobin",
    "wbc": "WBC",
    "trombosit": "Trombosit",
    "glukoz": "Glukoz",
    "kolesterol": "Kolesterol",
    "ldl": "LDL",
    "hdl": "HDL",
    "trigliserid": "Trigliserid",
    "tsh": "TSH",
    "crp": "CRP",
    "demir": "Demir",
    "ferritin": "Ferritin",
    "kreatinin": "Kreatinin",
    "alt": "ALT",
    "ast": "AST",
    "eritrosit": "Eritrosit",
    "hematokrit": "Hematokrit",
    "mcv": "MCV",
    "mch": "MCH",
    "mchc": "MCHC",
    "rdw": "RDW",
    "urik asit": "Urik Asit",
    "protein": "Protein",
}


def _fold_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.replace("ı", "i").replace("İ", "I")
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    normalized = normalized.lower()
    normalized = normalized.replace("\u00a0", " ")
    return normalized


def normalize_test_name(raw_name: str) -> str:
    folded = _fold_text(raw_name)
    compact = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    if not compact:
        return "unknown"

    for alias, canonical in sorted(TEST_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", compact):
            return canonical

    return compact.replace(" ", "_")


def calculate_status(value: float, ref_min: float | None, ref_max: float | None) -> str:
    if ref_min is not None and value < ref_min:
        return "low"
    if ref_max is not None and value > ref_max:
        return "high"
    return "normal"


def display_name_for(test_name: str) -> str:
    canonical = normalize_test_name(test_name)
    return DISPLAY_NAMES.get(canonical, canonical.replace("_", " ").title())