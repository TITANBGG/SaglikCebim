**Proje Sunumu — SağlıkCebim**

Kısa Özet
- **Proje:** SağlıkCebim — Radyoloji odaklı sağlık destek ve analiz platformu.
- **Amaç:** Radyoloji görüntülerinden bilgi çıkarımı, doktor-destek araçları ve klinik entegrasyon ile prototip sunumu.
- **Bu dosya:** Projeyi sunmanız için eksiksiz bir sunum raporu ve tek-parça bir "sunum asistanı promptu" içerir. Final sunum, demo adımları, çalışma talimatları, mimari ve dağıtım rehberi kapsanır.

**Hedef Kitle**
- Teknik jüri (backend/frontend geliştiriciler, ML mühendisleri)
- Klinik paydaşlar (doktorlar, radyologlar)
- Yatırımcı/mentörler için kısa demo

**Kısa İçindekiler**
- Proje yapısı ve önemli dosyalar
- Geliştirme ortamı: çalıştırma ve test adımları
- Backend: mimari, API, veri tabanı, çalıştırma
- Frontend: mimari, çalıştırma, kritik bileşenler
- Model ve veri akışı: eğitim/çıkarım, testler
- Dağıtım: docker-compose ve prod adımları
- Sunum akışı (demo senaryosu)
- Tek-parça sunum asistanı promptu (kullanıma hazır)

**Proje Yapısı (özet)**
- Root: dokümanlar, raporlar ve geliştirme yardımcı araçları.
- `Kod (1)/saglikcebim (1)/` : uygulama kaynak kodu — backend, frontend, scriptler.
- `RAPORLAR/` : proje raporları, performans ve mimariler.
- Veritabanı örnekleri: `dev.db.*` dosyaları (lokal test verisi).
- Testler: `test_radiology_ai.py`, `_CLEANUP_TEMP_AND_EMPTY/test_gradcam_fix.py` vb.

**Geliştirme Ortamı — Gereksinimler**
- Python 3.10+ (veya proje gereksinimine uygun venv)
- Node 18+ / pnpm (frontend için)
- Docker & docker-compose (lokal prod/test kurulumları)
- Önemli paketler: backend requirements dosyasında belirtilmiştir (varsa). Eğer yoksa, `pip install -r requirements.txt` kullanın.

Çalıştırma (lokal, geliştirici)
1) Backend
   - Sanal ortam oluşturun ve etkinleştirin.
   - Gerekli paketleri yükleyin.
   - Ortam değişkenleri: `FLASK_APP` veya `DJANGO_SETTINGS_MODULE` gibi backend tipine göre ayarlayın.
   - Geliştirme sunucusunu başlatın (örnek):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r "Kod (1)/saglikcebim (1)/requirements.txt"
python "Kod (1)/saglikcebim (1)/backend/app.py"
```

2) Frontend
   - `cd "Kod (1)/saglikcebim (1)/frontend"` dizinine gidin.
   - Paketleri yükleyip dev server başlatın.

```bash
pnpm install
pnpm dev
```

3) Veritabanı
- Mevcut `dev.db.*` dosyalarını kullanın veya `migrations` varsa çalıştırın.

4) Testler
- Python testleri için:

```bash
pytest -q
```

**Backend — Özet Teknik Detaylar**
- Muhtemel stack: Python (Flask/FastAPI/Django), SQLite (dev.db), REST API endpointleri.
- Önemli noktalar:
  - API referansı ve endpointler `RAPORLAR/BACKEND_API_REFERENCE.md` dosyasında belgelenmiştir.
  - Auth & yetkilendirme: jwt/session tabanlı (varsa proje içindeki auth koduna bakın).
  - Görüntü işleme pipeline: `scripts/` ve `audit_codebase.py` içinde yardımcı araçlar.

API ve Demo Endpointleri (sunumda vurgulanacak)
- Hasta kayıt oluşturma / sorgulama
- Görüntü yükleme ve çıkarım isteği
- Grad-CAM veya heatmap üretimi endpointi
- Sonuçların dönülmesi ve ön yüz gösterimi

**Frontend — Özet Teknik Detaylar**
- Muhtemel stack: React + Vite + shadcn/ui (dosya isimlerinden ipucu).
- Kritik bileşenler:
  - Görüntü yükleme arayüzü
  - Model çıktı görüntüleme (overlay heatmap)
  - Listeleme / hasta geçmişi ekranları

Çalıştırma ve üretim derleme
- Dev: `pnpm dev`
- Build: `pnpm build`
- Serve: `pnpm preview` veya uygun statik sunucu/NGINX

**Model & Veri Akışı**
- Veri kaynağı: `uploads/radiology/` klasörü altında görüntüler.
- Model: Projede `Radyoloji_Analiz/` içeriği ve test dosyaları model ile ilgili bilgi sağlar.
- Çıkarım pipeline:
  1. Görüntü yüklenir.
  2. Ön-işleme (resize, normalize).
  3. Model çıkarımı (prediction).
  4. Post-işleme (prob eşiği, bbox/heatmap).
  5. Sonuç API üzerinden döndürülür ve frontend üzerinde gösterilir.

**Test ve Doğrulama**
- Otomatik testler: `pytest` ile çalıştırılabilen scriptler var.
- Görüntü doğrulama: `test_radiology_ai.py` gibi testlerle model davranışı kontrol edilir.

**Dağıtım**
- Docker-compose dosyaları mevcut: `Kod (1)/saglikcebim (1)/docker-compose.yml` ve `docker-compose.prod.yml`.
- Prod adımları (özet):
  1. Ortam değişkenlerini hazırlayın (.env)
  2. `docker-compose -f docker-compose.prod.yml up --build -d`
  3. Health check ve log incelemesi

**Sunum Akışı (5-10 dk demo önerisi)**
1. Kısa giriş: problem, hedef kullanıcıları ve çözümün özeti (1 dk)
2. Mimari diyagram + teknoloji stack (1 dk)
3. Kısa canlı demo: bir radyoloji görüntüsü yükleyin, çıkarımı gösterin, Grad-CAM overlay'i gösterin (3 dk)
4. API ve entegrasyon konuşması: hastane sistemlerine nasıl entegre edilir? (1 dk)
5. Performans & güvenlik notları, geliştirme planları, gelecek özellikler (1-2 dk)

**Sunumda Vurgulanacak Teknik Noktalar**
- Veri gizliliği ve hasta kimliklerinin maskelenmesi.
- Model belgelendirmesi ve klinik doğrulama gereksinimleri.
- API güvenliği ve kimlik doğrulama.
- Ölçeklenebilirlik: GPU destekli çıkarım, kuyruklama (celery/kafka) seçenekleri.

**Kullanıma Hazır Tek-Parça "Sunum Asistanı" Promptu**
Kullanım: Aşağıdaki tüm metni bir sohbet asistanına yapıştırın (veya slayt üretimi, konuşma metni ve demo adımlarını tek seferde çıkarma için kullanın).

--- BAŞLA ---

Ben bir jüri üyesiyim; şimdi bana "SağlıkCebim" projesini teknik ve iş odaklı olarak 5 dakika içinde sun. Sunum şu bölümleri içermeli:

1) Kısa özet (1-2 cümle): proje ne yapıyor, hangi problemi çözüyor, hedef kullanıcılar kim?
2) Mimari (1 paragraf): backend, frontend, veri akışı, model çıkarım pipeline, veritabanı türü ve önemli bileşenler.
3) Teknik detaylar (madde madde): kullanılan diller, kitaplıklar, docker-compose ile dağıtım, test stratejisi, CI/CD önerisi.
4) Canlı demo adımları (adım adım, kopyala-yapıştır yapılabilir komutlar dahil): nasıl lokal kurulur, hangi endpoint çağrılacak, hangi dosya upload edilecek, örnek cURL ve frontend dev server komutları.
5) Güvenlik ve gizlilik (kısa): hasta verisi nasıl korunuyor, önerilen en iyi uygulamalar.
6) Kısıtlar ve gelecek planları (kısa maddeler): bilinen sınırlamalar, klinik onay yolları, ölçeklenebilirlik planları.
7) Son olarak jüriye 2 öneri isteği: (a) hangi ek veriler/etiketlemeler klinik doğrulama için gerekli? (b) pilot kullanım için en uygun kurum/klinik türü hangisi?

Ayrıca, bana bir slayt başlık listesi ver (6 slide): Her slide için 1 cümle açıklama ve hangi görsel/ekran gösterileceğini belirt. Son olarak, 3 adet konuşma notu (her biri 1 cümle) vererek sunumu nasıl açacağımı söyle.

--- BİTİŞ ---

Kullanıcı notu: prompt'u kopyalayın ve bir üretken asistan ile çalıştırın — çıktı, sunum metni, slayt başlıkları ve demo adımlarını içerecektir.

**Kontrol Listesi (sunum öncesi)**
- Lokal ortamda backend + frontend çalışıyor mu?
- Örnek radyoloji görüntüleri hazır mı? (`uploads/radiology/`)
- Docker-compose ile prod testi geçildi mi?
- Testler (pytest) yeşil mi?

**İletişim / Notlar**
- Sunum sırasında canlı demo takılma ihtimaline karşı ekran kaydı veya önceden hazırlanmış GIF/video bulundurun.
- Eğer isterseniz, bu dosyayı slayt formatına dönüştürebilir veya İngilizce versiyonunu oluşturabilirim.

-- Dosya Sonu --
