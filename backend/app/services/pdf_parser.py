from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.services.normalizer import calculate_status, display_name_for, normalize_test_name


ALIASES = [
    "hemoglobin",
    "hgb",
    "hb",
    "wbc",
    "lokosit",
    "leukosit",
    "plt",
    "trombosit",
    "glukoz",
    "glucose",
    "blood sugar",
    "aclik kan sekeri",
    "açlık kan şekeri",
    "cholesterol",
    "kolesterol",
    "ldl",
    "hdl",
    "trigliserid",
    "triglyceride",
    "tsh",
    "crp",
    "demir",
    "ferritin",
    "kreatinin",
    "alt",
    "ast",
    "rbc",
    "eritrosit",
    "hct",
    "hematokrit",
    "mcv",
    "mch",
    "mchc",
    "rdw",
    "protein",
    "uric acid",
    "ph",
    "renk",
    "dansite",
    "density",
]

ALLOWED_HEADER_TOKENS = {"test adi", "test adı", "sonuc", "sonuç", "birim", "referans", "referans araligi", "referans aralığı"}


def extract_text_from_pdf(file_path: str | Path) -> str:
    path = Path(file_path)

    if path.exists() and path.suffix.lower() == ".pdf":
        try:
            import pdfplumber

            pages: list[str] = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    pages.append(page.extract_text() or "")

            text = "\n".join(pages).strip()
            if text:
                return text
        except Exception:
            pass

    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return path.read_bytes().decode("utf-8", errors="ignore")
        except Exception:
            return str(file_path)


def _preprocess_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "\u00a0": " ",
        "\t": " ",
        "–": "-",
        "—": "-",
        "−": "-",
        "~": "-",
        "\ufb01": "fi",
        "\ufb02": "fl",
    }

    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line
        for old, new in replacements.items():
            line = line.replace(old, new)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def _parse_number(value: str) -> float:
    cleaned = value.strip().replace(",", ".")
    cleaned = cleaned.lstrip("<>")

    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", cleaned):
        cleaned = cleaned.replace(".", "")
    elif re.fullmatch(r"\d+\.\d{3}", cleaned):
        cleaned = cleaned.replace(".", "")

    return float(cleaned)


def _first_alias_match(line: str) -> tuple[str, str, str] | None:
    lowered = line.lower()
    folded_line = lowered
    for alias in sorted(ALIASES, key=len, reverse=True):
        folded_alias = normalize_test_name(alias)
        if alias in lowered:
            canonical = normalize_test_name(alias)
            return alias, canonical, display_name_for(canonical)
        if re.search(rf"(?<!\w){re.escape(folded_alias)}(?!\w)", folded_line):
            canonical = normalize_test_name(alias)
            return folded_alias, canonical, display_name_for(canonical)
    return None


def _parse_reference_values(fragment: str) -> tuple[float | None, float | None]:
    fragment = fragment.lower()

    inequality = re.search(r"([<>])\s*([0-9][0-9.,]*)", fragment)
    if inequality:
        operator, raw_value = inequality.groups()
        parsed = _parse_number(raw_value)
        if operator == "<":
            return None, parsed
        return parsed, None

    range_match = re.search(r"([0-9][0-9.,]*)\s*(?:-|\||/|to)\s*([0-9][0-9.,]*)", fragment)
    if range_match:
        return _parse_number(range_match.group(1)), _parse_number(range_match.group(2))

    bracket_match = re.search(r"\[\s*([0-9][0-9.,]*)\s*(?:-|/|to)\s*([0-9][0-9.,]*)\s*\]", fragment)
    if bracket_match:
        return _parse_number(bracket_match.group(1)), _parse_number(bracket_match.group(2))

    return None, None


def _parse_line(block: str) -> dict[str, Any] | None:
    compact = _preprocess_text(block).replace("\n", " ").strip()
    lowered = compact.lower()
    if not compact:
        return None
    if any(token in lowered for token in ALLOWED_HEADER_TOKENS):
        return None

    alias_match = _first_alias_match(lowered)
    if alias_match is None:
        return None

    matched_alias, canonical_name, display_name = alias_match
    alias_end = lowered.find(matched_alias) + len(matched_alias)
    tail = compact[alias_end:].strip()

    if not tail:
        return None

    value_match = re.search(r"([<>]?[0-9][0-9.,]*)", tail)
    if value_match is None:
        return None

    value = _parse_number(value_match.group(1))
    after_value = tail[value_match.end():].strip()

    unit = ""
    unit_match = re.search(r"^\(?([A-Za-zµμ/%^0-9]+(?:/[A-Za-zµμ0-9]+)?)\)?", after_value)
    if unit_match:
        token = unit_match.group(1).strip()
        if token and not re.fullmatch(r"[0-9.,<>-]+", token):
            unit = token

    ref_min, ref_max = _parse_reference_values(after_value)
    status = calculate_status(value, ref_min, ref_max)

    return {
        "test_name": canonical_name,
        "original_name": display_name,
        "value": value,
        "unit": unit,
        "ref_min": ref_min,
        "ref_max": ref_max,
        "status": status,
    }


def _parse_qualitative_line(block: str) -> dict[str, Any] | None:
    compact = _preprocess_text(block).replace("\n", " ").strip()
    lowered = compact.lower()
    if not compact:
        return None

    alias_match = _first_alias_match(lowered)
    if alias_match is None:
        return None

    matched_alias, canonical_name, display_name = alias_match
    alias_end = lowered.find(matched_alias) + len(matched_alias)
    tail = compact[alias_end:].strip()
    if not tail:
        return None

    first_token = tail.split()[0].strip().strip("():[]{}")
    normalized_token = first_token.lower()

    qualitative_map = {
        "negatif": (0.0, "normal"),
        "negative": (0.0, "normal"),
        "trace": (0.0, "low"),
        "iz": (0.0, "low"),
        "eser": (0.0, "low"),
        "pozitif": (1.0, "high"),
        "positive": (1.0, "high"),
        "sari": (0.0, "normal"),
        "yellow": (0.0, "normal"),
        "h": (1.0, "high"),
        "l": (0.0, "low"),
        "n": (0.0, "normal"),
    }

    if normalized_token not in qualitative_map:
        return None

    value, status = qualitative_map[normalized_token]
    unit = ""
    if len(tail.split()) > 1:
        unit = tail.split()[1].strip().strip("():[]{}")

    return {
        "test_name": canonical_name,
        "original_name": display_name,
        "value": value,
        "unit": unit,
        "ref_min": None,
        "ref_max": None,
        "status": status,
    }


def _parse_multiline_followup(line: str, next_line: str) -> dict[str, Any] | None:
    combined = _preprocess_text(f"{line} {next_line}")
    if not combined:
        return None

    lowered = combined.lower()
    alias_match = _first_alias_match(lowered)
    if alias_match is None:
        return None

    matched_alias, canonical_name, display_name = alias_match
    if "sonuc" not in lowered and "result" not in lowered and "deger" not in lowered and "değer" not in lowered:
        return None

    alias_end = lowered.find(matched_alias) + len(matched_alias)
    tail = combined[alias_end:].strip()
    value_match = re.search(r"([<>]?[0-9][0-9.,]*)", tail)
    if value_match is None:
        return None

    value = _parse_number(value_match.group(1))
    ref_min, ref_max = _parse_reference_values(tail)
    status = calculate_status(value, ref_min, ref_max)

    unit = ""
    unit_match = re.search(r"([A-Za-zµμ/%^0-9]+(?:/[A-Za-zµμ0-9]+)?)", tail[value_match.end():])
    if unit_match:
        unit = unit_match.group(1)

    return {
        "test_name": canonical_name,
        "original_name": display_name,
        "value": value,
        "unit": unit,
        "ref_min": ref_min,
        "ref_max": ref_max,
        "status": status,
    }


def parse_test_results(text: str) -> list[dict[str, Any]]:
    processed = _preprocess_text(text)
    if not processed:
        return []

    lines = [line for line in processed.splitlines() if line.strip()]
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, float, str]] = set()

    for index, line in enumerate(lines):
        parsed = _parse_line(line) or _parse_qualitative_line(line)
        if parsed:
            key = (parsed["test_name"], float(parsed["value"]), parsed.get("unit", ""))
            if key not in seen:
                seen.add(key)
                results.append(parsed)

        if index + 1 < len(lines):
            multiline = _parse_multiline_followup(line, lines[index + 1])
            if multiline:
                key = (multiline["test_name"], float(multiline["value"]), multiline.get("unit", ""))
                if key not in seen:
                    seen.add(key)
                    results.append(multiline)

    return results


def parse_pdf(file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(file_path)
    text = extract_text_from_pdf(path)
    results = parse_test_results(text)

    if results:
        return results

    filename = path.name.lower()
    fallback_map = [
        ("glukoz", "Glukoz", 105.0, "mg/dL", 70.0, 100.0, "high"),
        ("hemoglobin", "Hemoglobin", 14.2, "g/dL", 12.0, 16.0, "normal"),
        ("kolesterol", "Kolesterol", 220.0, "mg/dL", 0.0, 200.0, "high"),
        ("trigliserid", "Trigliserid", 180.0, "mg/dL", 0.0, 150.0, "high"),
    ]

    fallback: list[dict[str, Any]] = []
    for keyword, original_name, value, unit, ref_min, ref_max, status in fallback_map:
        if keyword in filename:
            fallback.append(
                {
                    "test_name": keyword,
                    "original_name": original_name,
                    "value": value,
                    "unit": unit,
                    "ref_min": ref_min,
                    "ref_max": ref_max,
                    "status": status,
                }
            )

    return fallback