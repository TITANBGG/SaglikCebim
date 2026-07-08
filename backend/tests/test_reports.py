import io

from app.api.v1 import reports as reports_api


def test_upload_pdf(client, auth_headers):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    fake_pdf.name = "test.pdf"
    res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["filename"].endswith("test.pdf")


def test_upload_non_pdf(client, auth_headers):
    fake_txt = io.BytesIO(b"not a pdf")
    res = client.post(
        "/reports/upload",
        files={"file": ("test.txt", fake_txt, "text/plain")},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_get_reports_empty(client, auth_headers):
    res = client.get("/reports/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_get_reports_after_upload(client, auth_headers):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    res = client.get("/reports/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_delete_report(client, auth_headers):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    del_res = client.delete(f"/reports/{report_id}", headers=auth_headers)
    assert del_res.status_code == 200


def test_delete_other_users_report(client, auth_headers):
    client.post(
        "/auth/register",
        json={
            "email": "other@test.com",
            "password": "OtherPass123!",
            "full_name": "Other User",
        },
    )
    login_other = client.post(
        "/auth/login",
        json={"email": "other@test.com", "password": "OtherPass123!"},
    )
    other_headers = {"Authorization": f"Bearer {login_other.json()['access_token']}"}

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    del_res = client.delete(f"/reports/{report_id}", headers=other_headers)
    assert del_res.status_code == 404


def test_download_pdf_requires_parsed_report(client, auth_headers):
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    download_res = client.get(f"/reports/{report_id}/download-pdf", headers=auth_headers)
    assert download_res.status_code == 400


def test_download_pdf_success(client, auth_headers, monkeypatch):
    def fake_parse_pdf(_):
        return [
            {
                "test_name": "hemoglobin",
                "original_name": "Hemoglobin",
                "value": 13.5,
                "unit": "g/dL",
                "ref_min": 12.0,
                "ref_max": 16.0,
                "status": "normal",
            }
        ]

    monkeypatch.setattr(reports_api, "parse_pdf", fake_parse_pdf)
    monkeypatch.setattr(
        reports_api,
        "build_pdf_report",
        lambda **_: b"%PDF-1.4 test-pdf",
    )

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    parse_res = client.post(f"/reports/{report_id}/parse", headers=auth_headers)
    assert parse_res.status_code == 200

    download_res = client.get(f"/reports/{report_id}/download-pdf", headers=auth_headers)
    assert download_res.status_code == 200
    assert download_res.headers["content-type"].startswith("application/pdf")
    assert "attachment;" in download_res.headers["content-disposition"].lower()
    assert download_res.content == b"%PDF-1.4 test-pdf"


def test_get_recommendations_report_not_found(client, auth_headers):
    res = client.get("/reports/999999/recommendations", headers=auth_headers)
    assert res.status_code == 404


def test_get_recommendations_success(client, auth_headers, monkeypatch):
    def fake_parse_pdf(_):
        return [
            {
                "test_name": "glukoz",
                "original_name": "Glukoz",
                "value": 145.0,
                "unit": "mg/dL",
                "ref_min": 70.0,
                "ref_max": 100.0,
                "status": "high",
            },
            {
                "test_name": "hemoglobin",
                "original_name": "Hemoglobin",
                "value": 14.0,
                "unit": "g/dL",
                "ref_min": 12.0,
                "ref_max": 16.0,
                "status": "normal",
            },
        ]

    monkeypatch.setattr(reports_api, "parse_pdf", fake_parse_pdf)

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    parse_res = client.post(f"/reports/{report_id}/parse", headers=auth_headers)
    assert parse_res.status_code == 200

    rec_res = client.get(f"/reports/{report_id}/recommendations", headers=auth_headers)
    assert rec_res.status_code == 200
    body = rec_res.json()
    assert body["count"] == 1
    assert "glukoz" in body["data"]
    assert body["data"]["glukoz"]["status"] == "high"
    assert body["data"]["glukoz"]["eat"]
    assert body["interpretation"]["abnormal_count"] == 1


def test_parse_report_returns_interpretation(client, auth_headers, monkeypatch):
    def fake_parse_pdf(_):
        return [
            {
                "test_name": "glukoz",
                "original_name": "Glukoz",
                "value": 145.0,
                "unit": "mg/dL",
                "ref_min": 70.0,
                "ref_max": 100.0,
                "status": "high",
            },
            {
                "test_name": "trigliserid",
                "original_name": "Trigliserid",
                "value": 220.0,
                "unit": "mg/dL",
                "ref_min": 0.0,
                "ref_max": 150.0,
                "status": "high",
            },
        ]

    monkeypatch.setattr(reports_api, "parse_pdf", fake_parse_pdf)

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]

    parse_res = client.post(f"/reports/{report_id}/parse", headers=auth_headers)
    assert parse_res.status_code == 200
    body = parse_res.json()
    assert body["interpretation"]["abnormal_count"] == 2
    assert body["interpretation"]["combinations"][0]["code"] == "metabolic_risk"

    interpretation_res = client.get(f"/reports/{report_id}/interpretation", headers=auth_headers)
    assert interpretation_res.status_code == 200
    assert interpretation_res.json()["interpretation"]["combinations"][0]["code"] == "metabolic_risk"


def test_monitoring_empty_payload(client, auth_headers):
    res = client.get("/reports/monitoring", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["window_days"] == 30
    assert body["kpis"]
    assert body["status_breakdown"] == {"normal": 0, "high": 0, "low": 0}
    assert body["gauges"] == []
    assert body["focus_trends"] == []
    assert body["latest_results_table"] == []


def test_monitoring_payload_with_data(client, auth_headers, monkeypatch):
    def fake_parse_pdf(_):
        return [
            {
                "test_name": "glukoz",
                "original_name": "Glukoz",
                "value": 121.0,
                "unit": "mg/dL",
                "ref_min": 70.0,
                "ref_max": 100.0,
                "status": "high",
            },
            {
                "test_name": "hemoglobin",
                "original_name": "Hemoglobin",
                "value": 14.1,
                "unit": "g/dL",
                "ref_min": 12.0,
                "ref_max": 16.0,
                "status": "normal",
            },
        ]

    monkeypatch.setattr(reports_api, "parse_pdf", fake_parse_pdf)

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    upload_res = client.post(
        "/reports/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers,
    )
    report_id = upload_res.json()["id"]
    parse_res = client.post(f"/reports/{report_id}/parse", headers=auth_headers)
    assert parse_res.status_code == 200

    res = client.get(
        "/reports/monitoring?window_days=30&focus_tests=glukoz,hemoglobin&limit_rows=10",
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["focus_tests"] == ["glukoz", "hemoglobin"]
    assert body["status_breakdown"]["high"] >= 1
    assert body["kpis"]
    assert body["gauges"]
    assert body["focus_trends"]
    assert body["latest_results_table"]


def test_monitoring_invalid_window_days(client, auth_headers):
    res = client.get("/reports/monitoring?window_days=3", headers=auth_headers)
    assert res.status_code == 422
