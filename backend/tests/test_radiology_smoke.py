"""
Radyoloji Smoke Test — Upload → Analyze → Findings zinciri
AI modeli (DenseNet) yokken mock kullanır.
"""
import io
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock radiology_ai analiz sonucu
_MOCK_FINDINGS = [
    {
        "finding_type": "Consolidation",
        "tr_name": "Konsolidasyon",
        "description": "Akciğer parankiminde konsolidasyon",
        "confidence": 0.82,
        "severity": "moderate",
        "location": "Sol alt lob",
        "suggested_actions": ["Akciğer grafisi kontrolü", "Enfeksiyon markerleri"],
    },
    {
        "finding_type": "Pleural Effusion",
        "tr_name": "Plevral Efüzyon",
        "description": "Sol plevral boşlukta sıvı birikimi",
        "confidence": 0.61,
        "severity": "mild",
        "location": "Sol hemitoraks",
        "suggested_actions": ["Ultrasonografi"],
    },
]


def _make_png_bytes() -> bytes:
    """1×1 piksel geçerli PNG — gerçek dosya simülasyonu."""
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
        0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82,
    ])


class TestRadiologySmoke:

    @patch("app.api.v1.radiology.radiology_ai")
    def test_upload_returns_findings(self, mock_ai, client: TestClient, auth_headers, tmp_path):
        """Upload → AI analiz → response'da findings dönmeli."""
        mock_ai.analyze.return_value = (_MOCK_FINDINGS, None)

        png = _make_png_bytes()
        response = client.post(
            "/radiology/upload",
            files={"file": ("chest.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "image_id" in data
        assert data["status"] == "analyzed"
        assert isinstance(data["findings"], list)
        assert len(data["findings"]) == 2

    @patch("app.api.v1.radiology.radiology_ai")
    def test_upload_finding_fields(self, mock_ai, client: TestClient, auth_headers):
        """Her finding'de beklenen alanlar mevcut olmalı."""
        mock_ai.analyze.return_value = (_MOCK_FINDINGS, None)

        png = _make_png_bytes()
        response = client.post(
            "/radiology/upload",
            files={"file": ("xray.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )
        assert response.status_code == 200
        for f in response.json()["findings"]:
            assert "finding_type" in f
            assert "confidence" in f
            assert 0.0 <= f["confidence"] <= 1.0
            assert "severity" in f
            assert "suggested_actions" in f

    @patch("app.api.v1.radiology.radiology_ai")
    def test_upload_then_list(self, mock_ai, client: TestClient, auth_headers):
        """Upload sonrası liste endpoint'i görüntüyü göstermeli."""
        mock_ai.analyze.return_value = (_MOCK_FINDINGS, None)

        png = _make_png_bytes()
        client.post(
            "/radiology/upload",
            files={"file": ("scan.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )

        list_res = client.get("/radiology/", headers=auth_headers)
        assert list_res.status_code == 200
        images = list_res.json()
        assert len(images) >= 1
        assert any(img["original_filename"] == "scan.png" for img in images)

    @patch("app.api.v1.radiology.radiology_ai")
    def test_upload_then_detail(self, mock_ai, client: TestClient, auth_headers):
        """Upload sonrası detail endpoint findings'i döndürmeli."""
        mock_ai.analyze.return_value = (_MOCK_FINDINGS, None)

        png = _make_png_bytes()
        up = client.post(
            "/radiology/upload",
            files={"file": ("detail_test.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )
        assert up.status_code == 200
        image_id = up.json()["image_id"]

        detail = client.get(f"/radiology/{image_id}", headers=auth_headers)
        assert detail.status_code == 200
        d = detail.json()
        assert d["image_id"] == image_id
        assert isinstance(d["findings"], list)
        assert len(d["findings"]) == 2

    @patch("app.api.v1.radiology.radiology_ai")
    def test_upload_ai_error_graceful(self, mock_ai, client: TestClient, auth_headers):
        """AI analizi patlarsa graceful fallback — status 200, findings boş."""
        mock_ai.analyze.side_effect = RuntimeError("Model yüklenemedi")

        png = _make_png_bytes()
        response = client.post(
            "/radiology/upload",
            files={"file": ("error_test.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "analyzed"
        assert response.json()["findings"] == []

    def test_upload_wrong_extension_rejected(self, client: TestClient, auth_headers):
        """PDF uzantılı dosya 400 dönmeli."""
        response = client.post(
            "/radiology/upload",
            files={"file": ("report.pdf", io.BytesIO(b"fake pdf"), "application/pdf")},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_list_unauthorized(self, client: TestClient):
        """Token olmadan liste 401 dönmeli."""
        response = client.get("/radiology/")
        assert response.status_code == 401

    @patch("app.api.v1.radiology.radiology_ai")
    def test_patient_summary_radiology_flag(self, mock_ai, client: TestClient, auth_headers):
        """Radyoloji yüklendikten sonra patient summary has_radiology=True olmalı."""
        mock_ai.analyze.return_value = ([], None)

        png = _make_png_bytes()
        client.post(
            "/radiology/upload",
            files={"file": ("flag_test.png", io.BytesIO(png), "image/png")},
            headers=auth_headers,
        )

        summary = client.get("/patient/summary/basic", headers=auth_headers)
        assert summary.status_code == 200
        data = summary.json()
        assert data["has_radiology"] is True
        assert "radyoloji" not in data["missing_modalities"]
        assert data["completion_score"] >= 33
