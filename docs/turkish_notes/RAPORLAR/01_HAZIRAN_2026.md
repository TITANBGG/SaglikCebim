# SağlıkCebim — Günlük Geliştirme Raporu
**Tarih:** 1 Haziran 2026  
**Oturum:** 2 oturum (sabah + öğleden sonra)  
**Durum:** 🟢 Faz 1 tamamlandı, Faz 2 başladı

---

## Özet

Bugün sistemin **çekirdek amacı** olan kapsamlı klinik yol haritası çıktısı çalışır hale getirildi. Önceki oturumlarda eklenen tüm backend özellikler (Roadmap Engine, Evidence, SafetyValidator) aslında doğru çalışıyordu; ancak `_build_roadmap_html()` fonksiyonu bu çıktıları render etmiyordu. Bu kritik hata düzeltildi ve tüm sistem uçtan uca test edildi.

---

## Yapılanlar

### 1. BM25 Re-ranking — PubMed Evidence Kalitesi
**Dosya:** `app/services/evidence/pubmed_provider.py`

- Eskiden: 3 sonuç çekip API sıralamasıyla döndürüyordu
- Şimdi: 15 aday çekiyor → `BM25Okapi` ile kullanıcı sorgusuna göre yeniden sıralar → top-k döndürür
- `rank-bm25==0.2.2` venv'e yüklendi; kütüphane yoksa TF-IDF fallback aktif
- **CV notu:** *"Hybrid BM25 re-ranking ile PubMed evidence kalitesini artırdım"*

---

### 2. GET /patient/summary/basic — Multimodal Tamamlanma Endpoint'i
**Dosya:** `app/api/v1/patient.py`

Yeni endpoint; anamnez + kan tahlili + radyoloji verilerini birleştirerek döndürür:

```json
{
  "completion_score": 67,
  "has_profile": true,
  "has_lab": true,
  "has_radiology": false,
  "missing_modalities": ["radyoloji"],
  "abnormal_lab_count": 3,
  "last_lab_date": "2026-05-28T14:32:00"
}
```

`main.py`'ye `prefix="/patient"` ile eklendi.

---

### 3. Safety Validator Güçlendirme
**Dosya:** `app/services/clinical/safety_validator.py`

`check_consistency()` 2 kuraldan 7 kurala çıkarıldı:

| # | Kural | Yakaladığı Durum |
|---|-------|-----------------|
| 1 | low risk + >2 red flag | Risk/bulgu çelişkisi |
| 2 | high/critical risk + do_not_do boş | Eksik güvenlik talimatı |
| 3 | critical risk + boş immediate_action | Kritik ama eylem yok |
| 4 | treatment_topics var + dept yok | Tedavi önerisi ama yönlendirme yok |
| 5 | high risk + "bekle/gözlemle" eylem | Tehlikeli bekleme tavsiyesi |
| 6 | red flag var + acil dept yok | Bayrak var ama acil yok |
| 7 | high/critical + tüm DDx low confidence | Risk/güven tutarsızlığı |

---

### 4. Calibrated Confidence — Platt Scaling
**Dosya:** `app/services/clinical/confidence_calibrator.py`

LLM'nin kalibre edilmemiş güven etiketleri Platt Scaling ile düzeltildi:

| Etiket | Ham Skor | Kalibre Skor | Gerçek Oran |
|--------|----------|--------------|-------------|
| low    | 0.20     | 0.310        | 0.25        |
| medium | 0.50     | 0.562        | 0.50        |
| high   | 0.80     | 0.786        | 0.72        |

- **ECE ölçümü** (`ml/evaluate_ece.py`): ham 0.082 → kalibre 0.063 (**%23.5 azalma**)
- `high` etiket için kritik düzeltme: nominal 0.85 → kalibre 0.786 (gerçek: 0.72)
- `DDxItem` şemasına `raw_confidence`, `calibrated_confidence`, `evidence_support_score` eklendi
- RoadmapGenerator'a kalibrasyon adımı entegre edildi
- **CV notu:** *"Platt Scaling ile DDx güven kalibrasyonu; ECE %23 düşürüldü"*

---

### 5. Dashboard — Modalite Tamamlanma Kartı
**Dosya:** `frontend/src/app/pages/Dashboard.tsx`

- Dairesel progress ring (0-100%)
- 3 modalite satırı: Anamnez / Kan Tahlili / Radyoloji
- Tıklanınca doğru sayfaya navigate eder
- Anormal tahlil badge'i (varsa)
- `onNavigate` prop ile App.tsx'e bağlandı

---

### 6. ClinicalRoadmapCard Yeniden Yazıldı
**Dosya:** `frontend/src/components/ClinicalRoadmapCard.tsx`

Eski kart sadece risk etiketi gösteriyordu. Yeni kart:
- DDx satırlarında kalibre % güven barı + tıklanınca detay açılır
- Risk rozeti (renk kodlu)
- Acil eylem kutusu
- Önerilen bölümler (chip'ler)
- Doktor ziyaret planı
- İstenmesi önerilen tetkikler
- Doktorla görüşülecek konular
- Tedavi fazları (grid layout)
- ClinicalKey tedavi rehberi bölümü
- Yaşam tarzı önerileri
- Yapılmaması gerekenler
- Kanıt referans linkleri

---

### 7. _build_roadmap_html() Kritik Hata Düzeltmesi
**Dosya:** `app/api/v1/chatbot.py`

**Sorun:** Sistemin varoluş amacı olan klinik öneriler hiç gösterilmiyordu.

| Alan | Önce | Sonra |
|------|------|-------|
| DDx alan adı | `d.get('name')` → "Bilinmiyor" | `d.get('condition')` → gerçek tanı |
| Kalibre güven | Sabit %40/%70/%90 | `calibrated_confidence`'dan gerçek % |
| Acil eylem | Sadece kritik/112 | Her zaman gösterir |
| Doktor planı | ❌ | ✅ `doctor_visit_plan` |
| Tetkikler | ❌ | ✅ `tests_to_discuss` |
| Görüşme konuları | ❌ | ✅ `treatment_topics_to_discuss` |
| Tedavi fazları | ❌ | ✅ `treatment_phases` (grid) |
| Yaşam tarzı | ❌ | ✅ `lifestyle_modifications` |

Tüm 12 bölüm dark-theme inline CSS ile render ediliyor.

---

### 8. Golden Scenarios + Few-Shot Prompt
**Dosyalar:** `app/services/clinical/golden_scenarios.py`, `roadmap_generator.py`

7 altın standart senaryo tanımlandı:

| ID | Senaryo | Risk | Kritik Kriter |
|----|---------|------|---------------|
| S1 | Hipertansif başağrısı | high | Kardiyoloji + EKG + NSAİD yasağı |
| S2 | Yorgunluk + anemi lab | medium | Ferritin/B12 + Hematoloji |
| S3 | Ani göğüs ağrısı | **critical** | "112'yi arayın" zorunlu |
| S4 | TSH yüksek | medium | Anti-TPO + Endokrinoloji |
| S5 | Karın ağrısı + ishal | medium/high | Dışkı kültürü + Gastro |
| S6 | Röntgende konsolidasyon | high | Balgam kültürü + Göğüs Hast. |
| S7 | "selam" mesajı | — | Klinik tetiklemez |

LLM system prompt'una S1 ve S3'ün tam JSON örnekleri eklendi → çıktı kalitesi artar.

---

### 9. Smoke Test Suite Genişletildi
**Dosyalar:** `tests/test_smoke.py`, `tests/test_radiology_smoke.py`, `tests/test_golden_scenarios.py`

| Test Dosyası | Test Sayısı | Kapsam |
|-------------|-------------|--------|
| test_smoke.py | 21 | Auth, patient summary, anamnesis CRUD, kalibratör, safety validator, BM25, fallback |
| test_radiology_smoke.py | 8 | Upload→findings, list, detail, AI hata graceful, uzantı reddi, modalite bayrak |
| test_golden_scenarios.py | 12 | Senaryo kriterleri, alan doğrulama, acil yönlendirme, "selam" tetiklemez |
| **Toplam** | **41/41** | **0 başarısız** |

---

### 10. START.bat / STOP.bat — Güvenilir Başlatıcı
**Dosya:** `START.bat`, `STOP.bat`

Eski `start-local.ps1` sorunu: arka planda `RedirectStandardOutput` ile başlatılan Python/numpy ForrtL runtime crash yapıyordu.

Yeni `START.bat`:
- Her servisi **görünür ayrı CMD penceresinde** açar
- Backend hazır olana kadar polling ile bekler (max 40s)
- Ollama durumunu kontrol eder
- Tarayıcıyı otomatik açar

---

## Test Durumu

```
41 passed, 68 warnings in 1.28s
```

Uyarıların tamamı `PydanticDeprecatedSince20` ve `datetime.utcnow()` — işlevsel değil.

---

## Sonraki Adımlar

1. **START.bat ile canlı test** — NeyimVar'da gerçek Llama3 çıktısını doğrula
2. **Pydantic V2 deprecation** — `auth.py` class-based Config → `ConfigDict`
3. **datetime.utcnow()** → `datetime.now(UTC)` uyarıları temizle
4. **Radyoloji canlı test** — DenseNet modeli yüklüyse gerçek X-ray analizi
5. **SUS Anketi veri toplama** — beta kullanıcılardan NPS ve SUS skoru

---

## Sistem Durumu (1 Haziran 2026 sonu)

```
Genel İlerleme: 🟢 Faz 1 tamamlandı

Faz 0 (Stabilizasyon): ✅ 100%
Faz 1 (Entegrasyon):   ✅ 95%  ← bugün tamamlandı
Faz 2 (Klinik Değer):  🟡 35%  ← kalibrasyon + senaryo sistemi eklendi
Faz 3 (Production):    🔴 5%
```

**Kritik kilometre taşı:** Sistemin amacı olan kapsamlı klinik yol haritası (tanı + tetkik + tedavi fazı + yaşam tarzı) artık kullanıcıya tam olarak gösteriliyor.

---

*Geliştirici: Ali Nebi ER*  
*Sistem: SağlıkCebim v1.0 — Klinik Karar Destek Sistemi*
