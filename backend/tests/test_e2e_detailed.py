import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def run_detailed_tests():
    print("=== DETAILED E2E TEST ===\n")
    
    # 1. Register a test user
    print("1. Registering test user...")
    timestamp = int(time.time())
    reg_payload = {
        "email": f"test_user_{timestamp}@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    reg_response = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    print(f"   Status: {reg_response.status_code}")
    print(f"   Response: {reg_response.text}\n")
    
    if reg_response.status_code != 200:
        print("Registration failed!")
        return
    
    token = reg_response.json().get("access_token")
    print(f"   Token: {token[:50]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload a PDF file
    print("2. Uploading PDF file...")
    files = {'file': ('test_report.pdf', b'%PDF-1.4\n%%EOF', 'application/pdf')}
    upload_response = requests.post(
        f"{BASE_URL}/reports/upload",
        files=files,
        headers=headers
    )
    print(f"   Status: {upload_response.status_code}")
    print(f"   Response: {upload_response.text}\n")
    
    if upload_response.status_code != 200:
        print("Upload failed!")
        return
    
    report_id = upload_response.json().get("report_id")
    print(f"   Report ID: {report_id}\n")
    
    # 3. List reports
    print("3. Listing reports...")
    list_response = requests.get(f"{BASE_URL}/reports/", headers=headers)
    print(f"   Status: {list_response.status_code}")
    print(f"   Response: {list_response.text}\n")
    
    # 4. Get report results
    print(f"4. Getting report results for {report_id}...")
    results_response = requests.get(f"{BASE_URL}/reports/{report_id}/results", headers=headers)
    print(f"   Status: {results_response.status_code}")
    print(f"   Response: {results_response.text}\n")
    
    # 5. Parse report
    print(f"5. Parsing report {report_id}...")
    parse_response = requests.post(f"{BASE_URL}/reports/{report_id}/parse", headers=headers)
    print(f"   Status: {parse_response.status_code}")
    print(f"   Response: {parse_response.text}\n")
    
    # 6. Get recommendations
    print(f"6. Getting recommendations for {report_id}...")
    rec_response = requests.get(f"{BASE_URL}/reports/{report_id}/recommendations", headers=headers)
    print(f"   Status: {rec_response.status_code}")
    print(f"   Response: {rec_response.text}\n")
    
    # 7. Get PubMed articles
    print(f"7. Getting PubMed articles for {report_id}...")
    pubmed_response = requests.post(f"{BASE_URL}/reports/{report_id}/pubmed", headers=headers)
    print(f"   Status: {pubmed_response.status_code}")
    print(f"   Response: {pubmed_response.text}\n")
    
    # 8. Upload radiology image
    print("8. Uploading radiology image...")
    files = {'file': ('chest_xray.png', b'dummy image data', 'image/png')}
    rad_response = requests.post(
        f"{BASE_URL}/radiology/upload",
        files=files,
        headers=headers
    )
    print(f"   Status: {rad_response.status_code}")
    print(f"   Response: {rad_response.text}\n")
    
    # 9. Chatbot test
    print("9. Testing chatbot...")
    chat_response = requests.post(
        f"{BASE_URL}/api/v1/anamnesis/chat",
        json={"message": "Baş ağrım var", "user_id": 1},
        headers=headers
    )
    print(f"   Status: {chat_response.status_code}")
    print(f"   Response: {chat_response.text}\n")
    
    # 10. Get trends
    print("10. Getting trends for 'glukoz'...")
    trends_response = requests.get(f"{BASE_URL}/reports/trends/glukoz", headers=headers)
    print(f"   Status: {trends_response.status_code}")
    print(f"   Response: {trends_response.text}\n")
    
    # 11. Get available tests
    print("11. Getting available tests...")
    tests_response = requests.get(f"{BASE_URL}/reports/available-tests", headers=headers)
    print(f"   Status: {tests_response.status_code}")
    print(f"   Response: {tests_response.text}\n")

if __name__ == "__main__":
    run_detailed_tests()
