import requests
import json

BASE = "http://127.0.0.1:8000"

# 1. Login
login_resp = requests.post(f"{BASE}/auth/login", json={"email": "test@test.com", "password": "test123"})
print("Login status:", login_resp.status_code)
if login_resp.status_code != 200:
    # Try register
    reg = requests.post(f"{BASE}/auth/register", json={
        "email": "devtest@test.com",
        "password": "test123",
        "full_name": "Dev Test"
    })
    print("Register:", reg.status_code, reg.text[:200])
    login_resp = requests.post(f"{BASE}/auth/login", json={"email": "devtest@test.com", "password": "test123"})
    print("Login2:", login_resp.status_code)

token = login_resp.json().get("access_token") if login_resp.status_code == 200 else None
print("Token:", token[:40] if token else "NO TOKEN")

if not token:
    print("ERROR: Cannot get token")
    exit(1)

# 2. Upload a fake PNG (1x1 pixel PNG bytes)
import io
# Minimal valid PNG bytes (1x1 red pixel)
PNG_1X1 = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
    0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82
])

files = {"file": ("test_chest.png", io.BytesIO(PNG_1X1), "image/png")}
headers = {"Authorization": f"Bearer {token}"}

upload_resp = requests.post(f"{BASE}/radiology/upload", files=files, headers=headers)
print("\nUpload status:", upload_resp.status_code)
print("Upload response:", json.dumps(upload_resp.json(), indent=2, ensure_ascii=False))
