from app.services.normalizer import calculate_status, normalize_test_name
from app.services.pdf_parser import parse_test_results


def test_parse_pattern1():
    text = "Hemoglobin  13.5  g/dL  12.0-16.0"
    results = parse_test_results(text)
    assert len(results) > 0
    assert results[0]["value"] == 13.5


def test_parse_pattern2():
    text = "HGB: 13.5 (g/dL) [12-16]"
    results = parse_test_results(text)
    assert len(results) > 0


def test_normalize_test_name():
    assert normalize_test_name("HGB") == "hemoglobin"
    assert normalize_test_name("hgb") == "hemoglobin"
    assert normalize_test_name("lokosit") == "wbc"
    assert normalize_test_name("PLT") == "trombosit"


def test_calculate_status_normal():
    assert calculate_status(13.5, 12.0, 16.0) == "normal"


def test_calculate_status_low():
    assert calculate_status(10.0, 12.0, 16.0) == "low"


def test_calculate_status_high():
    assert calculate_status(18.0, 12.0, 16.0) == "high"


def test_calculate_status_boundary():
    assert calculate_status(12.0, 12.0, 16.0) == "normal"
    assert calculate_status(16.0, 12.0, 16.0) == "normal"


def test_parse_empty_text():
    assert parse_test_results("") == []


def test_parse_no_match():
    results = parse_test_results("Bu metin hicbir test sonucu icermiyor.")
    assert results == []


def test_parse_multiline_result_rows():
    text = (
        "Hemoglobin (HGB)\n"
        "Sonuc: 13.5 g/dL  Referans: 12.0 - 16.0\n"
        "Glukoz (Aclik)\n"
        "Sonuc: 95 mg/dL   Referans: 70 - 100"
    )

    results = parse_test_results(text)

    assert [result["test_name"] for result in results] == ["hemoglobin", "glukoz"]
    assert results[0]["value"] == 13.5
    assert results[1]["value"] == 95.0


def test_parse_qualitative_urine_rows():
    text = (
        "Renk  Sari  -  Sari\n"
        "pH  6.0  -  5.0-8.0\n"
        "Dansite  1.025  -  1.005-1.030\n"
        "Protein  Negatif  -  Negatif\n"
        "Glukoz  Negatif  -  Negatif"
    )

    results = parse_test_results(text)

    assert [result["test_name"] for result in results] == ["renk", "ph", "dansite", "protein", "glukoz"]
