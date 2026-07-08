# SağlıkCebim — Sistem Mimarisi ve Teknik Rapor

> **Tarih:** 6 Mart 2026  
> **Sürüm:** 0.1.0  
> **Durum:** Tüm testler geçiyor (67/67), frontend build temiz

---

## 1. Projeye Genel Bakış

**SağlıkCebim**, kullanıcıların kan tahlili PDF'lerini yükleyip analiz ettirebildiği, sonuçlarını takip edebildiği, kişiselleştirilmiş beslenme önerileri ve PubMed makaleleri alabildiği, yapay zekâ destekli sağlık asistanı ile sohbet edebildiği bir **Progressive Web App (PWA)** platformudur.

### Temel Özellikler
- PDF tahlil yükleme ve otomatik parse etme (9 farklı lab formatı)
- Test sonuçlarının durumuna göre analiz (yüksek/düşük/normal)
- Kişiye özel beslenme ve yaşam tarzı önerileri (103 test)
- Zaman serisi trend grafikleri
- PubMed makale arama ve günlük kişisel makale önerileri
- **Multi-agent sağlık asistanı** (LLM kullanmayan, offline çalışan)
- Push notification desteği
- Zamanlanmış hatırlatıcılar (tahlil yenileme, haftalık özet)
- Analiz raporu PDF oluşturma ve indirme
- Dashboard izleme paneli (KPI'lar, göstergeler, aktivite)

---

## 2. Teknoloji Yığını

### 2.1 Backend

| Teknoloji | Sürüm | Kullanım Amacı |
|-----------|-------|----------------|
| **Python** | 3.12 | Ana dil |
| **FastAPI** | 0.109.0 | REST API framework |
| **Uvicorn** | 0.27.0 | ASGI sunucu |
| **Pydantic** | 2.5.3 | Veri validasyonu ve schema |
| **SQLAlchemy** | 2.0.25 | ORM (veritabanı) |
| **Alembic** | 1.13.1 | Veritabanı migration |
| **psycopg2** | 2.9.9 | PostgreSQL driver |
| **python-jose** | 3.5.0 | JWT token (HS256) |
| **passlib** | 1.7.4 | Şifre hashing (pbkdf2_sha256) |
| **pdfplumber** | 0.11.9 | PDF metin çıkarma |
| **reportlab** | 4.4.10 | PDF rapor oluşturma |
| **httpx** | 0.27.2 | Async HTTP client (PubMed API) |
| **APScheduler** | 3.11.2 | Zamanlanmış görevler |
| **pywebpush** | 2.3.0 | Push notification |
| **regex** | 2026.2.28 | Gelişmiş regex (PDF parse) |
| **aiofiles** | 25.1.0 | Async dosya işlemleri |
| **Pillow** | 10.1.0 | Görüntü işleme |

### 2.2 Frontend

| Teknoloji | Sürüm | Kullanım Amacı |
|-----------|-------|----------------|
| **React** | 19.2.0 | UI kütüphanesi |
| **React Router** | 7.13.1 | Sayfa yönlendirme |
| **Axios** | 1.13.6 | HTTP client |
| **Recharts** | 3.7.0 | Grafik kütüphanesi |
| **Vite** | 8.0.0-beta.13 | Build aracı + dev server |
| **Tailwind CSS** | 4.2.1 | CSS framework |
| **VitePWA** | 1.2.0 | PWA eklentisi (service worker) |
| **ESLint** | 9.39.1 | Kod kalitesi |

### 2.3 Veritabanı ve Altyapı

| Teknoloji | Sürüm | Kullanım |
|-----------|-------|----------|
| **PostgreSQL** | 15 | Production veritabanı |
| **SQLite** | - | Geliştirme/test fallback |
| **Docker** | - | Konteynerizasyon |
| **Docker Compose** | - | Multi-servis orkestrasyon |
| **Nginx** | alpine | Frontend prod sunucu + API reverse proxy |

### 2.4 Harici API'lar

| API | Kullanım |
|-----|----------|
| **PubMed E-utilities** | Tıbbi makale arama (76 önceden tanımlı arama terimi) |
| **VAPID/WebPush** | Push notification altyapısı |

---

## 3. Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│                    KULLANICI (Tarayıcı)                  │
│                    React PWA + Service Worker            │
└──────────────┬──────────────────────────┬───────────────┘
               │ HTTP/REST                │ Push
               ▼                          ▼
┌──────────────────────┐    ┌────────────────────────────┐
│   Nginx (Prod)       │    │   WebPush Notification     │
│   - SPA fallback     │    │   VAPID-based              │
│   - /api → backend   │    └────────────────────────────┘
└──────────┬───────────┘
           ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Backend (port 8000)              │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ Auth API │ │Reports   │ │ Articles    │ │Notif.   │ │
│  │ /auth    │ │ /reports │ │ /articles   │ │/notif.  │ │
│  └────┬─────┘ └────┬─────┘ └─────┬───────┘ └────┬────┘ │
│       │             │             │               │      │
│  ┌────▼─────────────▼─────────────▼───────────────▼────┐ │
│  │                 SERVIS KATMANI                       │ │
│  │  pdf_parser │ analyzer │ recommendations │ pubmed   │ │
│  │  pdf_gen    │ normalizer │ article_nlp   │ push     │ │
│  │  monitoring │ scheduler                              │ │
│  └──────┬──────────────────────┬───────────────────────┘ │
│         │                      │                         │
│  ┌──────▼──────────────────────▼───────────────────────┐ │
│  │           MULTI-AGENT SİSTEMİ                        │ │
│  │  IntentAgent → PersonalAgent → KnowledgeAgent        │ │
│  │                → AnswerAgent                          │ │
│  │  Orchestrator (pipeline yönlendirme)                 │ │
│  └──────┬──────────────────────┬───────────────────────┘ │
│         │                      │                         │
│  ┌──────▼──────┐  ┌───────────▼────────────────┐        │
│  │   SQLAlchemy│  │   Veri Dosyaları           │        │
│  │   ORM       │  │   medical_kb.json (103)    │        │
│  └──────┬──────┘  │   turkish_intents.json     │        │
│         │         │   reference_ranges.json    │        │
│         │         │   test_mapping.json (503)  │        │
│         │         └────────────────────────────┘        │
└─────────┼───────────────────────────────────────────────┘
          ▼
┌──────────────────┐
│  PostgreSQL 15   │
│  (port 5433)     │
│  5 tablo         │
└──────────────────┘
```

---

## 4. Veritabanı Şeması

### 5 Tablo, 4 Migration

```
users                    reports                test_results
┌──────────────────┐    ┌──────────────────┐   ┌──────────────────┐
│ id (PK)          │◄──┤ user_id (FK)     │   │ id (PK)          │
│ email (unique)   │    │ id (PK)          │◄──┤ report_id (FK)   │
│ hashed_password  │    │ filename         │   │ test_name        │
│ full_name        │    │ original_filename│   │ original_name    │
│ created_at       │    │ file_path        │   │ value (Float)    │
│ updated_at       │    │ status           │   │ unit             │
└──────┬───────────┘    │ created_at       │   │ ref_min          │
       │                └──────────────────┘   │ ref_max          │
       │                                       │ status           │
       │                                       │ created_at       │
       │                                       └──────────────────┘
       │
       │    notifications               push_subscriptions
       │    ┌──────────────────┐        ┌──────────────────┐
       ├───►│ user_id (FK)     │        │ user_id (FK)     │◄──┐
       │    │ id (PK)          │        │ id (PK)          │   │
       │    │ title            │        │ endpoint (unique)│   │
       │    │ body             │        │ p256dh           │   │
       │    │ type             │        │ auth             │   │
       │    │ is_read          │        │ created_at       │   │
       │    │ created_at       │        └──────────────────┘   │
       │    └──────────────────┘                               │
       └───────────────────────────────────────────────────────┘
```

---

## 5. API Endpoint'leri (26 Toplam)

### Auth — `/auth` (3 endpoint)
| Metod | Yol | Açıklama |
|-------|-----|----------|
| POST | `/auth/register` | Yeni kullanıcı kaydı |
| POST | `/auth/login` | Giriş (JWT token döner) |
| GET | `/auth/me` | Oturumdaki kullanıcı bilgisi |

### Reports — `/reports` (11 endpoint)
| Metod | Yol | Açıklama |
|-------|-----|----------|
| POST | `/reports/upload` | PDF yükleme (max 10MB) |
| GET | `/reports/` | Kullanıcının tüm raporları |
| DELETE | `/reports/{id}` | Rapor silme |
| POST | `/reports/{id}/parse` | PDF parse et, sonuçları çıkar |
| GET | `/reports/{id}/results` | Parse edilmiş test sonuçları |
| GET | `/reports/{id}/download-pdf` | Analiz raporu PDF indir |
| GET | `/reports/{id}/pubmed` | Anormal sonuçlar için PubMed makaleleri |
| GET | `/reports/{id}/recommendations` | Beslenme/yaşam tarzı önerileri |
| GET | `/reports/trends/{test_name}` | Belirli bir testin zaman serisi |
| GET | `/reports/available-tests` | Kullanıcının test listesi |
| GET | `/reports/monitoring` | Dashboard verileri (KPI, gauge, trend, aktivite) |

### Articles — `/articles` (3 endpoint)
| Metod | Yol | Açıklama |
|-------|-----|----------|
| GET | `/articles/daily` | Kişiselleştirilmiş günlük makaleler |
| POST | `/articles/search` | PubMed arama + NLP özetleme |
| POST | `/articles/chat` | Agent tabanlı sağlık asistanı |

### Notifications — `/notifications` (7 endpoint)
| Metod | Yol | Açıklama |
|-------|-----|----------|
| POST | `/notifications/subscribe` | Push abonelik |
| DELETE | `/notifications/unsubscribe` | Push abonelik iptali |
| GET | `/notifications/vapid-key` | VAPID public key |
| GET | `/notifications/` | Son 20 bildirim |
| POST | `/notifications/{id}/read` | Bildirimi okundu işaretle |
| POST | `/notifications/read-all` | Tümünü okundu işaretle |
| POST | `/notifications/test-push` | Test push bildirimi |

### Sistem (2 endpoint)
| Metod | Yol | Açıklama |
|-------|-----|----------|
| GET | `/` | API çalışıyor mesajı |
| GET | `/health` | Sağlık kontrolü |

---

## 6. Multi-Agent Sağlık Asistanı

### Mimari: 4 Agent + 1 Orchestrator (LLM yok, tamamen offline)

```
Kullanıcı Mesajı
      │
      ▼
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR (Pipeline)            │
│                                             │
│  ① IntentAgent                              │
│     ├── Intent sınıflandırma (9 intent)     │
│     ├── Test adı çıkarma (122 alias)        │
│     └── Geçmiş mesajdan test taşıma         │
│                                             │
│  greeting/help ──► AnswerAgent ──► Yanıt    │
│  search ──► PubMed fallback                 │
│                                             │
│  ② PersonalAgent                            │
│     └── DB'den kullanıcı test sonuçları     │
│                                             │
│  ③ KnowledgeAgent                           │
│     ├── medical_kb.json'dan bilgi çekme     │
│     └── 13 korelasyon pattern tespiti       │
│                                             │
│  ④ AnswerAgent                              │
│     ├── 8 intent handler                    │
│     ├── Kişiselleştirilmiş Türkçe yanıt    │
│     └── Takip sorusu önerileri             │
└─────────────────────────────────────────────┘
```

### Intent Türleri ve Yanıt Örnekleri

| Intent | Anahtar Kelimeler | Yanıt İçeriği |
|--------|-------------------|---------------|
| **explain** | ne demek, nedir, açıkla | Test açıklaması + kişisel değer + acil uyarı |
| **recommend** | ne yemeliyim, öneri, diyet | Ye/Kaçın/Yaşam tarzı önerileri |
| **compare** | özetle, genel durum, karşılaştır | Yüksek/düşük/normal özet tablosu |
| **trend** | trend, değişim, nasıl değişmiş | Zaman serisi + yön analizi |
| **correlate** | ilişki, bağlantı, birlikte | Test ilişkileri + klinik tablo tespiti |
| **danger** | tehlikeli, riskli, acil | Risk değerlendirmesi + acil uyarılar |
| **search** | makale, araştırma, çalışma | PubMed'e yönlendirme |
| **greeting** | merhaba, selam | Karşılama + başlangıç önerileri |
| **help** | yardım, ne sorabilrim | Kullanım rehberi |

### Konuşma Hafızası
- Frontend son 6 mesajı `history` olarak backend'e gönderiyor
- Takip soruları çalışıyor: "Hemoglobin ne demek?" → "Peki tehlikeli mi?" (hemoglobin otomatik taşınır)
- Yeni test adı söylenince önceki bağlam temizleniyor

### Tıbbi Bilgi Tabanı (medical_kb.json)
- **103 test** — 16 kategoride
- Her test için: açıklama (yüksek/düşük/normal), öneriler (ye/kaçın/yaşam tarzı), ilişkili testler, acil değer uyarıları
- **13 klinik korelasyon paterni**: demir eksikliği anemisi, B12 eksikliği, metabolik sendrom, hipotiroidi, hipertiroidi, böbrek yetmezliği, karaciğer hasarı, inflamasyon tablosu, kalp krizi riski, kalp yetmezliği, DIC, alerji tablosu, gut hastalığı

### Kategoriler ve Test Dağılımı

| Kategori | Test Sayısı |
|----------|:-----------:|
| Hemogram | 26 |
| Karaciğer | 13 |
| Hormon | 8 |
| Tiroid | 7 |
| Demir Paneli | 6 |
| Elektrolit | 6 |
| Lipid | 5 |
| İnflamasyon | 5 |
| Böbrek | 4 |
| Koagülasyon | 4 |
| Kardiyak | 4 |
| İmmünglobülin | 4 |
| Enfeksiyon | 4 |
| Diyabet | 3 |
| Vitamin | 3 |
| İdrar | 1 |

---

## 7. PDF Parse Sistemi

### 9 Regex Kalıbı (Türk lab raporları için optimize)

| # | Kalıp | Örnek Format |
|---|-------|--------------|
| 1 | Standart | `Hemoglobin  14.5  g/dL  12.0-17.5` |
| 2 | Parantezli | `Hemoglobin: 14.5 (g/dL) [12.0-17.5]` |
| 3 | Pipe-delimited | `Hemoglobin | 14.5 | g/dL | 12.0 | 17.5` |
| 4 | Birim sonda | `Hemoglobin  14.5  12.0-17.5  g/dL` |
| 5 | Parantezli ref | `Hemoglobin  14.5  g/dL  (12.0 - 17.5)` |
| 6 | Referanssız | `Hemoglobin  14.5  g/dL` (harici mapping) |
| 7 | Sonuc/Result | `Sonuc: 14.5` (çok satırlı format) |
| 8 | Max-only | `Hemoglobin  14.5  g/dL  < 17.5` |
| 9 | Sadece değer | `Hemoglobin  14.5` (son çare) |

### Normalizasyon
- **503 alias eşlemesi** (test_mapping.json): "hgb" → "hemoglobin", "lökosit" → "wbc", "şeker" → "glukoz"
- **103 referans aralığı** (reference_ranges.json): cinsiyet bazlı (erkek/kadın/varsayılan)
- Türkçe İ/ı, ö/ü normalizasyonu
- Binlik ayraç (nokta) temizleme
- e-Nabız PDF metadata stripleme
- Duplikasyon engelleme

---

## 8. Frontend Yapısı

### Sayfa Yönlendirme

| Yol | Sayfa | Koruma |
|-----|-------|--------|
| `/login` | Giriş | Hayır |
| `/register` | Kayıt | Hayır |
| `/dashboard` | Ana panel | Evet (JWT) |
| `/upload` | PDF yükleme | Evet |
| `/trends` | Trend grafikleri | Evet |
| `/articles` | Makaleler + Chat | Evet |

### 9 Bileşen

| Bileşen | Açıklama |
|---------|----------|
| **FileUpload** | Sürükle-bırak PDF yükleme, progress, toplu yükleme (max 20, 10MB) |
| **NotificationBell** | Bildirim dropdown, push toggle, okunmamış sayacı |
| **ProtectedRoute** | JWT auth guard |
| **PubmedArticles** | PubMed makale kartları |
| **RecommendationPanel** | Beslenme önerileri (ye/kaçın/yaşam tarzı) |
| **ReportList** | Genişleyen rapor listesi (parse, sil, indir, sonuçlar) |
| **TestResults** | Test sonuç kartları (durum chip'leri) |
| **TrendChart** | Recharts çizgi grafik (referans çizgileri, tooltip) |
| **Button** | Yeniden kullanılabilir buton |

### Chat UI Özellikleri
- Otomatik scroll (useRef + useEffect)
- Typing indicator (3 zıplayan nokta animasyonu)
- Suggestion chip'leri (tıklanabilir takip soruları)
- Intent badge (intent türü etiketi)
- Bold rendering (`**kalın**` → **kalın**)
- Konuşma geçmişi (son 6 mesaj backend'e gönderilir)
- Temizle butonu
- Zengin karşılama mesajı + başlangıç önerileri

### PWA Desteği
- Service Worker (Workbox, NetworkFirst strateji)
- Offline-first yaklaşım
- App manifest (standalone, portrait)
- Push notification desteği
- 192x192 + 512x512 ikonlar

---

## 9. Docker/Deployment

### Geliştirme
```
docker-compose up -d     # PostgreSQL (port 5433)
cd backend && uvicorn app.main:app --reload  # port 8000
cd frontend && npm run dev                    # port 5173 (proxy → 8000)
```

### Production (3 konteyner)
```yaml
services:
  db:       PostgreSQL 15
  backend:  Python 3.11-slim + uvicorn (port 8000)
  frontend: Node 22 build → nginx:alpine (port 80, /api → backend)
```

---

## 10. Test Kapsamı

### 67 Test, 5 Dosya, Tümü Geçiyor

| Dosya | Test | Kapsam |
|-------|:----:|--------|
| test_agents.py | **36** | Intent tespiti (11), test çıkarma (6), knowledge (4), answer (6), pipeline (2), konuşma hafızası (7) |
| test_reports.py | **13** | Upload, delete, download, recommendations, monitoring |
| test_parser.py | **9** | PDF parse kalıpları, normalizasyon, durum hesaplama |
| test_auth.py | **6** | Register, login, me endpoint |
| test_articles.py | **3** | Daily, search, chat |

### Test Altyapısı
- In-memory SQLite (test izolasyonu)
- Her test için temiz tablo + geçici upload dizini
- FastAPI TestClient + JWT auth fixture

---

## 11. Zamanlanmış Görevler

| Görev | Zamanlama | Açıklama |
|-------|-----------|----------|
| Tahlil Hatırlatıcı | Her gün 09:00 | Son raporu 6 aydan eski kullanıcılara bildirim |
| Haftalık Özet | Her Pazartesi 10:00 | Haftalık parse edilmiş rapor özeti |

---

## 12. Güvenlik

| Önlem | Uygulama |
|-------|----------|
| Kimlik Doğrulama | JWT (HS256, 30 dk expire) |
| Şifre Hashing | pbkdf2_sha256 (passlib) |
| CORS | Sadece localhost:3000 ve localhost:5173 |
| Dosya Validasyonu | Sadece .pdf, max 10MB |
| Token Interceptor | Frontend'de 401 → otomatik logout |
| Input Validasyonu | Pydantic model (max_length, regex pattern) |
| API Auth Guard | `get_current_user` dependency (OAuth2Bearer) |

---

## 13. Dosya İstatistikleri

| Metrik | Değer |
|--------|:-----:|
| Backend bağımlılıkları | 20 |
| Veritabanı tabloları | 5 |
| Migration'lar | 4 |
| API endpoint'leri | **26** |
| Servis modülleri | 15 (10 servis + 5 agent) |
| Veri dosyaları | 4 |
| Tıbbi KB test sayısı | **103** |
| Test kategorileri | 16 |
| Referans aralıkları | 103 |
| Test adı eşlemeleri | **503** |
| Intent türleri | 9 (128 anahtar kelime) |
| Test alias sayısı | 122 |
| PubMed arama terimleri | 76 |
| PDF parse kalıpları | 9 |
| Korelasyon paterni | 13 |
| Frontend sayfaları | 6 |
| Frontend bileşenleri | 9 |
| Toplam test sayısı | **67** |
