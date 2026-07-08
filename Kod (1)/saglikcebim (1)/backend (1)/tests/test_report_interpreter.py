from app.services.report_interpreter import build_report_interpretation


def test_report_interpreter_detects_metabolic_pattern():
    interpretation = build_report_interpretation(
        [
            {
                "test_name": "glukoz",
                "original_name": "Glukoz",
                "value": 142,
                "unit": "mg/dL",
                "ref_min": 70,
                "ref_max": 100,
                "status": "high",
            },
            {
                "test_name": "trigliserid",
                "original_name": "Trigliserid",
                "value": 235,
                "unit": "mg/dL",
                "ref_min": 0,
                "ref_max": 150,
                "status": "high",
            },
        ]
    )

    assert interpretation["abnormal_count"] == 2
    assert interpretation["priority"] in {"attention", "routine"}
    assert interpretation["combinations"][0]["code"] == "metabolic_risk"
    assert "Metabolik" in interpretation["combinations"][0]["title"]
    assert interpretation["patient_report"]


def test_report_interpreter_detects_iron_deficiency_pattern():
    interpretation = build_report_interpretation(
        [
            {
                "test_name": "hemoglobin",
                "original_name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "ref_min": 12,
                "ref_max": 16,
                "status": "low",
            },
            {
                "test_name": "ferritin",
                "original_name": "Ferritin",
                "value": 8,
                "unit": "ng/mL",
                "ref_min": 20,
                "ref_max": 200,
                "status": "low",
            },
        ]
    )

    assert interpretation["combinations"][0]["code"] == "iron_deficiency_pattern"
    assert any(item["test_name"] == "hemoglobin" for item in interpretation["recommendations"])
