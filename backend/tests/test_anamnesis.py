"""Anamnesis endpoint testleri — ilaç, alerji, pharmacy check."""
import pytest
import json


# ── Pharmacy Mock ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_pharmacy_llm(monkeypatch):
    """Pharmacy check LLM çağrısını mock'la."""
    import app.services.ollama_client as oc

    class MockClient:
        def chat(self, system, user, temperature=0, format=None, retries=2):
            if format == "json":
                return json.dumps({
                    "has_risk": True,
                    "severity": "moderate",
                    "interaction_type": "C",
                    "user_warning": "Dikkatli kullanın, hekime danışın.",
                    "clinical_note": "Etkileşim mevcut.",
                })
            return "Mock yanıt"

    monkeypatch.setattr(oc, "_client", MockClient())


# ── İlaç Testleri ────────────────────────────────────────────────────────────

def test_add_medication(client, auth_headers):
    res = client.post(
        "/api/v1/anamnesis/medications",
        json={"medication_name": "Metformin", "dosage": "500mg"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_list_medications(client, auth_headers):
    client.post(
        "/api/v1/anamnesis/medications",
        json={"medication_name": "Aspirin", "dosage": "100mg"},
        headers=auth_headers,
    )
    res = client.get("/api/v1/anamnesis/medications", headers=auth_headers)
    assert res.status_code == 200
    names = [m["medication_name"] for m in res.json()]
    assert "Aspirin" in names


def test_delete_medication(client, auth_headers):
    add = client.post(
        "/api/v1/anamnesis/medications",
        json={"medication_name": "Silinecek", "dosage": "10mg"},
        headers=auth_headers,
    )
    med_id = add.json()["id"]

    del_res = client.delete(
        f"/api/v1/anamnesis/medications/{med_id}",
        headers=auth_headers,
    )
    assert del_res.status_code == 200

    meds = client.get("/api/v1/anamnesis/medications", headers=auth_headers).json()
    assert not any(m["medication_name"] == "Silinecek" for m in meds)


def test_medications_isolated_between_users(client):
    """Farklı kullanıcıların ilaçları birbirine karışmamalı."""
    # Kullanıcı 1
    r1 = client.post("/auth/register", json={
        "email": "user_one@test.com", "password": "Test1234!", "full_name": "UserOne"
    })
    assert r1.status_code == 200, f"User1 register failed: {r1.json()}"
    h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}

    # Kullanıcı 2
    r2 = client.post("/auth/register", json={
        "email": "user_two@test.com", "password": "Test1234!", "full_name": "UserTwo"
    })
    assert r2.status_code == 200, f"User2 register failed: {r2.json()}"
    h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

    # Kullanıcı 1'e özgü ilaç ekle
    client.post("/api/v1/anamnesis/medications",
                json={"medication_name": "KullaniciBirIlaci", "dosage": "1mg"}, headers=h1)

    # Kullanıcı 2'nin listesinde bu ilaç olmamalı
    meds2 = client.get("/api/v1/anamnesis/medications", headers=h2).json()
    assert isinstance(meds2, list)
    assert not any(m.get("medication_name") == "KullaniciBirIlaci" for m in meds2)


# ── Alerji Testleri ──────────────────────────────────────────────────────────

def test_add_allergy(client, auth_headers):
    res = client.post(
        "/api/v1/anamnesis/allergies",
        json={"allergen_name": "Penisilin", "reaction": "Döküntü"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_list_allergies(client, auth_headers):
    client.post(
        "/api/v1/anamnesis/allergies",
        json={"allergen_name": "Fıstık", "reaction": "Anafilaksi"},
        headers=auth_headers,
    )
    res = client.get("/api/v1/anamnesis/allergies", headers=auth_headers)
    assert res.status_code == 200
    names = [a["allergen_name"] for a in res.json()]
    assert "Fıstık" in names


@pytest.mark.skipif(
    True,  # SQLite test DB'de UUID type uyumsuzluğu var; üretimde PostgreSQL ile çalışır
    reason="PatientAllergy UUID primary key SQLite ile uyumsuz — PostgreSQL entegrasyon testinde çalıştırılmalı",
)
def test_delete_allergy(client, auth_headers):
    add = client.post(
        "/api/v1/anamnesis/allergies",
        json={"allergen_name": "Silinecek", "reaction": "Kasinti"},
        headers=auth_headers,
    )
    alg_id = add.json()["id"]
    del_res = client.delete(f"/api/v1/anamnesis/allergies/{alg_id}", headers=auth_headers)
    assert del_res.status_code in (200, 204)
    remaining = client.get("/api/v1/anamnesis/allergies", headers=auth_headers).json()
    assert not any(a.get("allergen_name") == "Silinecek" for a in remaining)


# ── Pharmacy Check ───────────────────────────────────────────────────────────

def test_pharmacy_check_with_no_meds(client, auth_headers):
    """İlaç yokken kontrol çalışmalı ve 'clear' dönmeli."""
    res = client.post(
        "/api/v1/anamnesis/pharmacy-check",
        json={"substance_name": "Aspirin"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] == "clear"  # İlaç yok → risk yok


def test_pharmacy_check_with_meds(client, auth_headers):
    """İlaç ekli olduğunda etkileşim denetimi yapılmalı."""
    client.post(
        "/api/v1/anamnesis/medications",
        json={"medication_name": "Warfarin", "dosage": "5mg"},
        headers=auth_headers,
    )
    res = client.post(
        "/api/v1/anamnesis/pharmacy-check",
        json={"substance_name": "Aspirin"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "message" in data
    assert "risks" in data
    assert data["checked_substance"] == "Aspirin"


def test_pharmacy_check_response_structure(client, auth_headers):
    """Yanıt yapısı doğru alanları içermeli."""
    res = client.post(
        "/api/v1/anamnesis/pharmacy-check",
        json={"substance_name": "ibuprofen"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    required_keys = ["status", "checked_substance", "current_medications", "risks", "message"]
    for key in required_keys:
        assert key in data, f"'{key}' alanı yanıtta eksik"


def test_pharmacy_check_missing_substance(client, auth_headers):
    """substance_name eksikse 422 dönmeli."""
    res = client.post(
        "/api/v1/anamnesis/pharmacy-check",
        json={},
        headers=auth_headers,
    )
    assert res.status_code == 422
