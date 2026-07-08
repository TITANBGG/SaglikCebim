# ClinicalKey & UpToDate Entegrasyon Rehberi

## 1. ClinicalKey Entegrasyonu

### 1.1 Cookie Alma (Manual Adım)
```
1. Tarayıcıda https://www.clinicalkey.com adresine git
2. Kayıtlı hesapla giriş yap
3. Chrome DevTools > Network > XHR tab'ında bir istek seç
4. Request Headers > Cookie: başlığını bul
5. Cookie değerinin tamamını kopyala
```

### 1.2 Cookie'yi Sisteme Ekle
```bash
# .env dosyasında güncelle:
CLINICAL_KEY_COOKIE=paste-your-cookie-here
```

### 1.3 Backend Ajanı (Yapılması Gereken)
```python
# app/services/clinical/clinical_key_agent.py (Yeni Dosya)

import requests
from typing import List, Dict, Optional
import os

class ClinicalKeyAgent:
    def __init__(self):
        self.cookie = os.getenv("CLINICAL_KEY_COOKIE")
        self.base_url = "https://www.clinicalkey.com/api"
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        if self.cookie:
            session.headers.update({
                "Cookie": self.cookie,
                "User-Agent": "SaglikCebim/1.0"
            })
        return session

    def search_by_diagnosis(self, diagnosis: str) -> Dict:
        """
        ClinicalKey'de tanı ara ve tedavi bilgisi getir
        """
        try:
            # ClinicalKey API endpoint (gerçek endpoint'i belgelerine göre düzelteceksiniz)
            response = self.session.get(
                f"{self.base_url}/search",
                params={"q": diagnosis, "type": "clinical_summary"}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "diagnosis": diagnosis,
                    "summary": data.get("summary", ""),
                    "treatment": data.get("treatment", ""),
                    "references": data.get("references", [])
                }
        except Exception as e:
            print(f"[CLINICAL_KEY ERROR] {e}")
        
        return {"diagnosis": diagnosis, "error": "ClinicalKey bağlantısı başarısız"}

    def get_treatment_recommendations(self, diagnosis: str) -> List[str]:
        """
        Tanıya göre tedavi önerilerini getir
        """
        result = self.search_by_diagnosis(diagnosis)
        if "treatment" in result and result["treatment"]:
            # Tedavi tavsiyelerini parse et ve döndür
            return result["treatment"].split("\n")
        return []
```

### 1.4 ChatBot'ta Kullanma
```python
# app/api/v1/chatbot.py içinde

from app.services.clinical.clinical_key_agent import ClinicalKeyAgent

# ClinicalRoadmapEngine içinde
ck_agent = ClinicalKeyAgent()
treatment_guidance = ck_agent.get_treatment_recommendations(diagnosis_name)

roadmap["treatment_guidance"] = treatment_guidance
```

---

## 2. UpToDate Entegrasyonu

### 2.1 Durum
UpToDate'in resmi API'si **açık değildir**. Üç seçenek var:

#### Seçenek A: Kurumsal Lisans (Önerilir)
```
- Hastane/Klinik aracılığıyla UpToDate lisansı satın alın
- Sağlanan API anahtarını kullan
- Backend'de REST API çağrısı yap
```

#### Seçenek B: Web Scraping (Risklı)
```python
# Yasal olmayabilir, ToS ihlali riski
# Tavsiye edilmez
```

#### Seçenek C: Llama3 ile Simülasyon (Şu Anki Durum)
```python
# PharmacologyAgent zaten bunu yapıyor
# UpToDate bilgisi Llama3 training data'sından geliyor
# Çok kullanışlı ama sınırlı
```

### 2.2 Kurumsal Lisans ile Entegrasyon
```python
# app/services/clinical/uptodate_agent.py (Yeni Dosya)

import requests
from typing import Dict, List
import os

class UpToDateAgent:
    def __init__(self):
        self.api_key = os.getenv("UPTODATE_API_KEY")
        self.base_url = "https://api.uptodate.com/v1"  # Gerçek endpoint'i al
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def search_clinical_topic(self, topic: str) -> Dict:
        """UpToDate'de klinik konu ara"""
        try:
            response = requests.get(
                f"{self.base_url}/clinical-topics",
                params={"query": topic},
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[UPTODATE ERROR] {e}")
        
        return {"error": "UpToDate bağlantısı başarısız"}

    def get_drug_interactions(self, drugs: List[str]) -> Dict:
        """İlaç etkileşimlerini kontrol et"""
        try:
            response = requests.post(
                f"{self.base_url}/drug-interactions",
                json={"drugs": drugs},
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[UPTODATE DRUG INTERACTION ERROR] {e}")
        
        return {"interactions": []}

    def get_patient_education(self, diagnosis: str) -> str:
        """Hasta eğitim materyali al"""
        try:
            response = requests.get(
                f"{self.base_url}/patient-education",
                params={"topic": diagnosis},
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
        except Exception as e:
            print(f"[UPTODATE EDUCATION ERROR] {e}")
        
        return ""
```

### 2.3 .env'ye Ekle
```env
# UpToDate (Kurumsal Lisans)
UPTODATE_API_KEY=your-uptodate-api-key-here
```

---

## 3. Frontend Entegrasyonu

### 3.1 Chatbot'ta Kaynak Göster
```typescript
// frontend/src/app/components/HealthChatBot.tsx

interface ChatResponse {
  type: "clinical_roadmap" | "chat_message"
  answer: string
  sources?: {
    clinicalkey?: string
    uptodate?: string
    pubmed?: string
  }
}

// Cevabın altında kaynakları göster
{response.sources && (
  <div className="text-xs text-slate-500 mt-2">
    Kaynaklar: 
    {response.sources.clinicalkey && <a href="#">ClinicalKey</a>}
    {response.sources.uptodate && <a href="#">UpToDate</a>}
    {response.sources.pubmed && <a href="#">PubMed</a>}
  </div>
)}
```

### 3.2 Yükleme Göstergesi
```typescript
{isLoading && (
  <div className="text-sm text-slate-400">
    📚 ClinicalKey ve UpToDate aranıyor...
  </div>
)}
```

---

## 4. Implementasyon Sırası (Tavsiye Edilen)

1. **Hafta 1**: Llama3 ile simülasyon (zaten çalışıyor, geliştir)
2. **Hafta 2**: ClinicalKey cookie entegrasyonu
3. **Hafta 3**: UpToDate kurumsal lisans (mümkünse)
4. **Hafta 4**: Frontend'de kaynak gösterimi

---

## 5. Test Et

```bash
# Backend test
curl -X POST http://127.0.0.1:8000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Kan şekerim yüksek ne yapmalıyım", "conversation_history": []}'

# Yanıtta ClinicalKey/UpToDate bilgisi olmalı
```

---

## 6. Yasal Uyarılar

⚠️ **Önemli**:
- ClinicalKey ve UpToDate **telif hakkı korumalı**
- Sadece **lisanslı kullanıcılar** tarafından erişilmeli
- Kurumsal lisans almadan web scraping yapma
- Her veri çekişinde hukuki danışmanlık al

---

## 7. Alternatif Kaynaklar (Açık)

Lisans yoksa bu kaynakları kullan:

```python
# Açık Tıbbi Veritabanları
- PubMed (NCBI): https://pubmed.ncbi.nlm.nih.gov/
- OpenFDA: https://open.fda.gov/
- Wikidoc: https://wikidoc.org/
- MeSH: https://meshb.nlm.nih.gov/
```

