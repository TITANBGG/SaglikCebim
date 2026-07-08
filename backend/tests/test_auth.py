"""Auth endpoint testleri — register, login, token."""
import pytest


VALID_PASSWORD = "Test1234!"


def test_register_success(client):
    res = client.post("/auth/register", json={
        "email": "user@test.com",
        "password": VALID_PASSWORD,
        "full_name": "Test User",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": VALID_PASSWORD, "full_name": "Test"}
    client.post("/auth/register", json=payload)
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert any(w in detail for w in ["kayitli", "zaten", "registered", "already", "exists"])


def test_register_short_password(client):
    res = client.post("/auth/register", json={
        "email": "short@test.com",
        "password": "abc",
        "full_name": "Test",
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "email": "login@test.com",
        "password": VALID_PASSWORD,
        "full_name": "Test",
    })
    res = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": VALID_PASSWORD,
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrong@test.com",
        "password": VALID_PASSWORD,
        "full_name": "Test",
    })
    res = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "YanlisParola1!",
    })
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/auth/login", json={
        "email": "yok@test.com",
        "password": VALID_PASSWORD,
    })
    assert res.status_code == 401


def test_me_authenticated(client, auth_headers):
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@test.com"


def test_me_unauthenticated(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_invalid_token(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer gecersiz_token"})
    assert res.status_code == 401
