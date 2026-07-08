import requests
import json
import time
from collections import defaultdict

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    timestamp = int(time.time())
    reg_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        },
    )
    if reg_response.status_code == 200:
        return reg_response.json().get("access_token")
    return None

def run_tests():
    print("SağlıkCebim Chatbot Test Mimarisi Başlatılıyor...\n")
    
    token = get_auth_token()
    if not token:
        print("HATA: Test kullanıcısı oluşturulamadı!")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    with open('tests/test_cases.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    results = []
    passed_count = 0
    category_stats = defaultdict(lambda: {"total": 0, "passed": 0})

    for idx, test in enumerate(test_cases):
        cat = test['category']
        category_stats[cat]["total"] += 1
        print(f"Test [{test['id']}] çalıştırılıyor: {cat}")
        
        payload = {
            "message": test["input"],
            "conversation_history": []
        }
        
        start_time = time.time()
        r = requests.post(f"{BASE_URL}/api/v1/chatbot/chat", json=payload, headers=headers)
        end_time = time.time()
        
        if r.status_code != 200:
            print(f"HATA: API {r.status_code} döndürdü")
            continue
            
        response_data = r.json()
        html_output = response_data.get("response", "")
        # Arka plandan direkt HTML geldiği için string bazlı test yapıyoruz
        
        passed = True
        errors = []
        
        # Must include checks
        for word in test["must_include"]:
            if word.lower() not in html_output.lower():
                passed = False
                errors.append(f"EKSİK: '{word}' bulunamadı.")
                
        # Must not include checks
        for word in test["must_not_include"]:
            if word.lower() in html_output.lower():
                passed = False
                errors.append(f"YASAKLI KELİME: '{word}' bulundu.")
                
        # Expected departments check
        if test.get("expected_department"):
            dept_found = any(dept.lower() in html_output.lower() for dept in test["expected_department"])
            if not dept_found:
                passed = False
                errors.append(f"DEPARTMAN HATASI: Beklenen '{test['expected_department']}' bulunamadı.")
                
        # CRITICAL OVERRIDE: If risk is critical, it MUST include emergency terms
        if test.get("risk_level") == "critical":
            emergency_terms = ["112", "acil", "acil servis", "en yakın sağlık"]
            if not any(term in html_output.lower() for term in emergency_terms):
                passed = False
                errors.append("missed_red_flag: Acil risk seviyesine rağmen 112/Acil yönlendirmesi yapılmadı!")

        if passed:
            passed_count += 1
            category_stats[cat]["passed"] += 1
            print(" -> DURUM: BASARILI")
        else:
            print(" -> DURUM: BASARISIZ")
            for e in errors:
                print("    -", e)
        print(f"    - Süre: {end_time - start_time:.2f} saniye\n")
        
        results.append({
            "test_id": test["id"],
            "category": test["category"],
            "passed": passed,
            "expected_department": test.get("expected_department", []),
            "risk_level_expected": test.get("risk_level", "unknown"),
            "errors": errors,
            "response_snippet": html_output[:200] + "...",
            "comment": test.get("expected_behavior", "")
        })
        
    print("="*40)
    print(f"GENEL TEST SONUCU: {passed_count} / {len(test_cases)} Başarılı")
    print("="*40)
    print("KATEGORİ BAZLI BAŞARI:")
    for cat, stats in category_stats.items():
        success_rate = (stats["passed"] / stats["total"]) * 100
        print(f" - {cat}: %{success_rate:.0f} ({stats['passed']}/{stats['total']})")
    
    final_report = {
        "summary": {
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "category_stats": dict(category_stats)
        },
        "details": results
    }
    
    with open('tests/test_report.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=4)
        
    print("\nDetaylı rapor 'tests/test_report.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    run_tests()
