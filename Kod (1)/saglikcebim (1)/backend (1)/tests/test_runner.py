import json
import os
import sys
import unittest
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "http://127.0.0.1:8000/api/v1"

class TestClinicalAssessment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Kayıt ol veya Giriş Yap
        BASE = "http://127.0.0.1:8000"
        requests.post(f"{BASE}/auth/register", json={"email": "testrunner@test.com", "password": "SecurePass123!", "full_name": "Test Runner"})
        res = requests.post(f"{BASE}/auth/login", json={"email": "testrunner@test.com", "password": "SecurePass123!"})
        cls.token = res.json().get("access_token")
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "test_cases.json"), "r", encoding="utf-8") as f:
            self.test_cases = json.load(f)

    def test_all_cases(self):
        print("\n--- TESTLER BAŞLIYOR ---")
        for case in self.test_cases:
            print(f"\n[TEST CASE: {case['id']}] - Input: {case['input']}")
            payload = {"message": case["input"], "conversation_history": []}
            res = requests.post(f"{BASE_URL}/chatbot/chat", json=payload, headers=self.headers)
            
            self.assertEqual(res.status_code, 200, f"API 200 dönmedi: {res.text}")
            result = res.json()
            answer = result.get("answer", "").replace("İ", "i").replace("I", "ı").lower()
            
            print(f"-> Cevap Uzunluğu: {len(answer)} karakter")
            print(f"DEBUG ANSWER: {answer}")
            
            # Acil Durum Kontrolü
            if case["risk_level"] in ("high", "critical"):
                self.assertTrue(any(keyword in answer for keyword in case["must_include"]), f"Acil durum anahtar kelimeleri bulunamadı: {case['must_include']}")
                print("   [BAŞARILI] Yüksek riskli durum triyajı aktifleşti.")
            else:
                for word in case["must_not_include"]:
                    self.assertNotIn(word.lower(), answer, f"Cevapta olmaması gereken kelime bulundu: {word}")
                print("   [BAŞARILI] Düşük riskli durum normal yanıtlandı.")

if __name__ == "__main__":
    unittest.main()
