import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Testing Backend APIs...")
    
    # Wait for backend to be ready
    try:
        r = requests.get(f"{BASE_URL}/")
        print("Backend is up:", r.json())
    except Exception as e:
        print(f"Backend might not be running! Error: {e}")
        return

    # 1. Register/Login
    timestamp = int(time.time())
    reg_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"final_e2e_{timestamp}@example.com",
            "password": "TestPassword123",
            "full_name": "Final E2E User",
        },
    )
    print("\n--- Auth Test ---")
    print("Register:", reg_response.status_code, reg_response.text)
    token = reg_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Radiology Upload
    print("\n--- Radiology Test ---")
    files = {'file': ('test.png', b'dummy content', 'image/png')}
    r = requests.post(f"{BASE_URL}/radiology/upload", files=files, headers=headers)
    print("Radiology upload:", r.status_code, r.text)

    # 3. Chatbot Test
    print("\n--- Chatbot Test ---")
    r = requests.post(f"{BASE_URL}/api/v1/anamnesis/chat", json={
        "message": "Baş ağrım var, ne yapmalıyım?",
    }, headers=headers)
    print("Chatbot response:", r.status_code, r.text)

    # 4. Reports Test (Upload PDF)
    print("\n--- Reports Test ---")
    files = {'file': ('report.pdf', b'dummy content', 'application/pdf')}
    r = requests.post(f"{BASE_URL}/reports/upload", files=files, headers=headers)
    print("Report upload:", r.status_code, r.text)
    
if __name__ == "__main__":
    run_tests()
