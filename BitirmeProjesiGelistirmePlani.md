# SağlıkCebim — Bitirme Projesi Geliştirme Planı
**Hedef:** 6/10 → 8-9/10  
**Tarih:** 31.05.2026  
**Toplam Süre:** ~6-8 hafta  

---

## GENEL BAKIŞ

```
FAZA 1 (Hafta 1)     → Kritik altyapı düzeltmeleri
FAZA 2 (Hafta 2)     → LLM yükseltme (GPT-4o)
FAZA 3 (Hafta 3-4)   → Güvenlik + Test suite
FAZA 4 (Hafta 4-5)   → Radyoloji AI tamamlama
FAZA 5 (Hafta 5-6)   → Evidence engine (PubMed gerçek)
FAZA 6 (Hafta 6-7)   → Kullanıcı testi + Performans
FAZA 7 (Hafta 7-8)   → Dokümantasyon + Akademik rapor
```

---

## FAZA 1 — Kritik Altyapı (Hafta 1)
**Kazanç:** 6 → 6.5 | **Süre:** 3-5 gün

### 1.1 Güvenlik: Hardcoded Credentials
**Sorun:** SECRET_KEY, DB şifresi repoda açık.  
**Yapılacak:**
- `docker-compose.yml`'de tüm secret'ları `${ENV_VAR}` formatına çek
- `.env.example` oluştur (gerçek değerler olmadan)
- `.env`'i `.gitignore`'a ekle (şu an var mı kontrol et)
- SECRET_KEY için `python -c "import secrets; print(secrets.token_urlsafe(64))"` ile güçlü key üret
- Dosyalar: `docker-compose.yml`, `.env`, `.gitignore`

**Test:** `git log --all --full-history -- .env` → commit geçmişinde credential kalmamalı

---

### 1.2 Rate Limiting: Chatbot Flood Koruması
**Sorun:** `/api/v1/chatbot/chat` saniyede yüzlerce istek alabiliyor.  
**Yapılacak:**
- `pip install slowapi` → `requirements.txt`'e ekle
- `app/main.py`'e rate limiter ekle:
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  limiter = Limiter(key_func=get_remote_address)
  
  @router.post("/chat")
  @limiter.limit("10/minute")  # Kullanıcı başına dakikada 10
  async def chatbot_chat(...):
  ```
- Dosyalar: `backend/app/main.py`, `backend/app/api/v1/chatbot.py`

**Test:** `ab -n 20 -c 5 http://localhost:8000/api/v1/chatbot/chat` → 429 Too Many Requests gelsin

---

### 1.3 XSS: DOMPurify Entegrasyonu
**Sorun:** `dangerouslySetInnerHTML` XSS açığı.  
**Yapılacak:**
```bash
cd frontend && npm install dompurify && npm install -D @types/dompurify
```
- `HealthChatBot.tsx` ve `NeyimVar.tsx`'te:
  ```typescript
  import DOMPurify from 'dompurify';
  // Tüm dangerouslySetInnerHTML'lerde:
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(msg.content) }} />
  ```
- Dosyalar: `frontend/src/app/components/HealthChatBot.tsx`, `frontend/src/app/pages/NeyimVar.tsx`

---

### 1.4 Structured Logging
**Sorun:** Hatalar sadece `print()` ile konsola yazılıyor.  
**Yapılacak:**
- `backend/app/core/logging.py` oluştur:
  ```python
  import logging, json
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
  logger = logging.getLogger("saglikcebim")
  ```
- `chatbot.py`, `clinical_roadmap_engine.py`, `roadmap_generator.py`'deki tüm `print()`'leri `logger.error()`, `logger.info()` ile değiştir

**Faza 1 tamamlandığında:** Güvenlik açıkları kapalı, loglar düzgün.

---

## FAZA 2 — LLM Yükseltme (Hafta 2)
**Kazanç:** 6.5 → 7.5 | **Süre:** 3-4 gün

### 2.1 GPT-4o API Entegrasyonu
**Neden:** Llama3 8B Türkçe tutmuyor, medikal reasoning zayıf, 15-30 sn latency.  
**GPT-4o ile:** Tutarlı Türkçe, güçlü medikal reasoning, ~2-3 sn yanıt.

**Yapılacak:**
1. `requirements.txt`'e `openai>=1.0.0` ekle
2. `docker-compose.yml`'e `OPENAI_API_KEY: ${OPENAI_API_KEY}` ekle
3. `backend/app/services/llm_client.py` oluştur (LLM provider abstraction):
   ```python
   import os
   
   def get_llm_client():
       provider = os.getenv("LLM_PROVIDER", "ollama")  # "openai" veya "ollama"
       if provider == "openai":
           from openai import OpenAI
           return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
       else:
           # Mevcut Ollama client
           from langchain_ollama import OllamaLLM
           return OllamaLLM(model="llama3", base_url=os.getenv("OLLAMA_BASE_URL"))
   ```
4. `ollama_agent.py`'deki `chat_conversational()` → GPT-4o chat completion formatına taşı:
   ```python
   # OpenAI formatı:
   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_message}
       ],
       temperature=0.3,
       max_tokens=1000
   )
   ```
5. `roadmap_generator.py`'deki JSON üretimi → GPT-4o ile JSON mode kullan:
   ```python
   response = client.chat.completions.create(
       model="gpt-4o",
       response_format={"type": "json_object"},
       messages=[...]
   )
   ```
6. `.env`'e `LLM_PROVIDER=openai` ve `OPENAI_API_KEY=sk-...` ekle

**Dosyalar:**
- `backend/app/services/llm_client.py` (yeni)
- `backend/app/services/ollama_agent.py`
- `backend/app/services/clinical/roadmap_generator.py`
- `backend/requirements.txt`
- `docker-compose.yml`

**Maliyet tahmini:** 1000 chatbot konuşması ≈ $2-5 (GPT-4o fiyatıyla)

**Test:** "başım dönüyor" → Türkçe yanıt, < 5 sn

---

### 2.2 Prompt Caching (Maliyet Optimizasyonu)
- Hasta bağlamı (anamnez, lab) her sorguda aynı → cache edilebilir
- OpenAI prompt caching ile tekrarlanan sistem prompt'ları %50 indirimli

---

## FAZA 3 — Güvenlik + Test Suite (Hafta 3-4)
**Kazanç:** 7.5 → 8 | **Süre:** 1-1.5 hafta

### 3.1 Test Suite — Sıfırdan Yaz
**Sorun:** `test_agents.py` çalışmıyor, coverage ~%0.

**Yapılacak:**
```
backend/tests/
├── conftest.py              # Fixtures: test DB, mock LLM, test user
├── test_auth.py             # Register, login, token
├── test_chatbot.py          # Chat endpoint I/O (LLM mock ile)
├── test_clinical_engine.py  # Roadmap üretimi, safety validator
├── test_anamnesis.py        # İlaç, alerji, pharmacy check
├── test_reports.py          # PDF upload, parse
└── test_radiology.py        # Radyoloji upload, analiz
```

**Kritik: LLM'i mock'la:**
```python
# conftest.py
@pytest.fixture
def mock_llm(monkeypatch):
    def fake_invoke(prompt):
        return '{"risk_level":"medium","differential_diagnosis":[],...}'
    monkeypatch.setattr("app.services.ollama_agent.OllamaDiagnosisAgent.llm.invoke", fake_invoke)
```

**Hedef:** `pytest --cov=app --cov-report=term` → %70+ coverage

---

### 3.2 CI/CD Pipeline
**Yapılacak:**
- `.github/workflows/test.yml` oluştur:
  ```yaml
  name: Tests
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Run tests
          run: docker-compose run backend pytest tests/ -v
  ```
- Her commit'te testler otomatik çalışsın

---

### 3.3 Input Validation & Prompt Injection Koruması
**Yapılacak:**
- `ChatRequest`'e max_length ekle:
  ```python
  class ChatRequest(BaseModel):
      message: str = Field(..., max_length=1000, min_length=1)
  ```
- Prompt'a inject deneme tespiti:
  ```python
  INJECTION_PATTERNS = ["ignore previous", "disregard", "jailbreak", "system:"]
  if any(p in message.lower() for p in INJECTION_PATTERNS):
      return {"answer": "Geçersiz istek.", ...}
  ```

---

## FAZA 4 — Radyoloji AI Tamamlama (Hafta 4-5)
**Kazanç:** 8 → 8.5 | **Süre:** 1.5 hafta

### 4.1 Model Accuracy Metrikleri
**Sorun:** Model var ama hiç ölçüm yapılmamış.  
**Yapılacak:**
- NIH ChestX-ray14 validation set'inde model'i değerlendir:
  ```python
  # ml/evaluate.py'i çalıştır:
  python ml/evaluate.py --model_path ml/models/best_model.pt --data_dir data/val/
  ```
- Rapor: Accuracy, AUC-ROC, F1, Sensitivity, Specificity — her sınıf için
- Bu metrikleri frontend'de "Model Performansı" sayfasında göster

### 4.2 GradCAM Görselleştirme — UI'a Ekle
**Sorun:** `ml/gradcam.py` var ama arayüzde gösterilmiyor.  
**Yapılacak:**
- Radyoloji analiz sonucunda GradCAM ısı haritasını overlay olarak göster
- "Modelin nereye baktığını" kullanıcıya açıkla
- Bu jüriyi en çok etkileyen özellik olacak

### 4.3 Daha Fazla Patoloji Sınıfı
**Şu an:** Sadece infiltrasyon  
**Hedef:** Effüzyon, pnömotoraks, kosta kırığı, kardiyomegali

### 4.4 DICOM Dosya Desteği
- Gerçek hastane sistemleri DICOM kullanıyor
- `pydicom` kütüphanesi ekle
- `.dcm` dosyaları upload edilebilsin

---

## FAZA 5 — Evidence Engine Gerçek Entegrasyon (Hafta 5-6)
**Kazanç:** 8.5 → 9 | **Süre:** 4-5 gün

### 5.1 PubMed Tam Entegrasyonu
**Sorun:** Email var ama gerçek API sorgusu test edilmemiş.  
**Yapılacak:**
- Entrez API ile gerçek sorgular:
  ```python
  from Bio import Entrez
  Entrez.email = os.getenv("PUBMED_EMAIL")
  handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
  ```
- Abstract'ları çek, GPT-4o ile Türkçe özetle
- Chatbot yanıtına "İlgili Yayınlar" bölümü ekle
- Referans listesi PDF olarak indirilebilsin

### 5.2 Evidence-Based Roadmap
- LLM'e PubMed abstract'larını bağlam olarak ver
- "Bu öneri X ve Y çalışmalarına dayanmaktadır" formatında cite et
- Evidence level (IA, IB, IIA...) otomatik ata

### 5.3 ClinicalKey (Opsiyonel)
- Gerçek ClinicalKey erişimi varsa demo moddan çık
- Yoksa "ClinicalKey içeriği lisanslı, kurumsal erişim gerektirir" notu ekle

---

## FAZA 6 — Kullanıcı Testi + Performans (Hafta 6-7)
**Kazanç:** 9 → 9.5 | **Süre:** 1-1.5 hafta

### 6.1 Kullanıcı Testi (Zorunlu!)
**Yapılacak:**
- En az 10 kullanıcı (5 sağlık profesyoneli, 5 normal kullanıcı)
- **SUS (System Usability Scale)** anketi uygula — 10 soru, 0-100 arası skor
- Test senaryoları:
  - Tahlil yükle → yorumla → önerileri oku
  - Şikayet anlat → klinik yol haritasını değerlendir
  - İlaç ekle → etkileşim kontrol et
- Sonuçları tabloya dök → Akademik raporda kullan
- Bir doktor veya sağlık profesyoneli klinik doğruluğu değerlendirsin

### 6.2 Performans Optimizasyonu
**Sorun:** Chatbot 15-30 saniye yanıt veriyor (Ollama ile).

**GPT-4o ile bu sorun büyük ölçüde çözülür ama ek optimizasyonlar:**
- **Streaming response ekle:** Yanıt kelime kelime gelsin, bekleme hissi azalsın
  ```python
  # Zaten /api/v1/roadmap/stream endpoint'i var — chatbot'a da ekle
  ```
- **DB query optimizasyonu:** N+1 query var mı kontrol et, index ekle
- **Response caching:** Aynı hasta verisiyle aynı soru → cache'den dön

### 6.3 Load Testing
```bash
pip install locust
# locustfile.py oluştur:
class ChatUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/api/v1/chatbot/chat", json={"message":"baş ağrım var"})
```
- 10 eşzamanlı kullanıcı → sistem stabil mi?
- Sonuçları raporla

---

## FAZA 7 — Dokümantasyon + Akademik Rapor (Hafta 7-8)
**Kazanım:** 9.5 → 10 | **Süre:** 1 hafta

### 7.1 Sistem Mimarisi Diyagramı
- **C4 diyagramı** (Context, Container, Component, Code)
- `draw.io` veya `Mermaid.js` kullan
- Jüri sunum slaytlarına ekle

### 7.2 Veritabanı ER Diyagramı
- `pgAdmin` ile otomatik oluştur veya `dbdiagram.io`
- Tüm tablolar ve ilişkiler görünmeli

### 7.3 API Dokümantasyonu
- FastAPI'nin `/docs` (Swagger) sayfasını zenginleştir:
  ```python
  @router.post("/chat", summary="Klinik chatbot", 
               description="Kullanıcı şikayetini alır, klinik roadmap veya sohbet yanıtı döner")
  ```
- Her endpoint için örnek request/response ekle

### 7.4 Akademik Rapor Bölümleri
Jürinin görmek istediği rapor yapısı:

```
1. Özet (Abstract)
2. Giriş
   - Motivasyon: Türkiye'de sağlık bilgi erişimi sorunu
   - Katkı: Ne yeni getiriyorsunuz?
3. İlgili Çalışmalar
   - Medikal NLP sistemleri
   - Klinik karar destek sistemleri
   - LLM tabanlı sağlık asistanları
4. Sistem Mimarisi
   - Bileşenler diyagramı
   - Veri akışı
5. Yöntem
   - LLM entegrasyon yöntemi
   - Radyoloji AI modeli
   - Evidence entegrasyonu
6. Deneyler ve Sonuçlar
   - Radyoloji model accuracy metrikleri
   - Chatbot yanıt kalitesi değerlendirmesi
   - Kullanıcı testi (SUS skoru)
   - Performans ölçümleri
7. Tartışma
   - Güçlü yanlar, sınırlılıklar
   - Etik ve yasal değerlendirme (KVKK)
8. Sonuç ve Gelecek Çalışmalar
9. Kaynaklar
```

### 7.5 KVKK Uyumluluk Notu
- Hasta verilerinin nasıl saklandığını belgele
- Veri silme endpoint'i ekle (GDPR/KVKK "unutulma hakkı")
- Privacy policy sayfası (basit olsa da olur)

---

## ÖZET TABLO

| Faz | İçerik | Süre | Puan Katkısı |
|-----|--------|------|--------------|
| 1 | Güvenlik, rate limit, XSS, logging | 3-5 gün | +0.5 |
| 2 | GPT-4o entegrasyonu | 3-4 gün | +1.0 |
| 3 | Test suite + CI/CD | 1-1.5 hafta | +0.5 |
| 4 | Radyoloji AI tamamlama | 1.5 hafta | +0.5 |
| 5 | PubMed gerçek entegrasyon | 4-5 gün | +0.5 |
| 6 | Kullanıcı testi + performans | 1-1.5 hafta | +0.5 |
| 7 | Dokümantasyon + akademik rapor | 1 hafta | +0.5 |
| **TOPLAM** | | **~7-8 hafta** | **+4.0 → 10/10** |

---

## EN YÜKSEk ETKİLİ 3 ADIM (Zaman kısıtlıysa)

**Bu 3 şeyi yapın, 6 → 8.5 olur:**

### 1. GPT-4o'ya Geç (3-4 gün)
Türkçe dil sorunu biter, yanıt süresi düşer, reasoning kalitesi artar.  
Jüriye demoyu gösterdiğinizde gece yarısı çalışmak zorunda kalmazsınız.

### 2. Kullanıcı Testi Yap (1 hafta)
10 kişiyle test, SUS anketi, 1 doktordan onay al.  
"Gerçek kullanıcılarla test ettik, SUS skorumuz X'tir" cümlesi jüriyi etkiler.

### 3. Radyoloji Metriklerini Çıkar (2-3 gün)
`ml/evaluate.py` zaten var. Çalıştır, sayıları al, slayta koy.  
"Accuracy %87, AUC 0.91" → jüri etkilenir.

---

## CLAUDE'UN NELER YAPABİLECEĞİ

Bir sonraki oturumda şunu söyle:
> "BitirmeProjesiGelistirmePlani.md'yi oku, Faza X'i yap."

Claude otomatik olarak:
- Doğru dosyaları bulur
- Kodu yazar
- Docker rebuild yapar
- Test eder
- Sonucu raporlar
