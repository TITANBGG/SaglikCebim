# SağlıkCebim

Bu depo SağlıkCebim projesinin ana kaynak deposudur — backend API, frontend SPA, model/inference boru hattı ve deploy girdileri.

## Amaç
Klinik öykü toplama, radyoloji görüntü analizi ve raporlama otomasyonunu sağlayan bir prototip uygulama.

## Hızlı Başlangıç (Geliştirici)
Önkoşullar: Python 3.10+, Node 18+, pnpm veya npm, Docker (opsiyonel)

Backend (örnek virtualenv):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
# Çevre değişkenlerini ayarlayın (ör. .env)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:
```bash
cd frontend
pnpm install
pnpm dev
# veya
npm install
npm run dev
```

Docker ile (tüm servisler):
```bash
docker-compose up --build -d
```

## Testler
```bash
# Backend test örneği
cd backend
pytest -q
```

## Önemli Dosyalar / Dizinler
- `backend/` — API, model servisleri, requirements
- `frontend/` — React + Vite uygulaması
- `docker-compose.yml`, `docker-compose.prod.yml` — container tanımları
- `scripts/`, `setup.ps1`, `start-local.cmd` — geliştirme yardımcıları
- `RAPORLAR/BACKEND_API_REFERENCE.md` — API dökümantasyonu (link referansı)
- `final.md` — sunum raporu (oluşturuldu)

## Neyi Push'lamalıyız?
Depoya yalnızca kaynak kodu, yapılandırma şablonları ve dokümantasyon push edilmelidir. Büyük veri dosyaları, veritabanı dump'ları, hassas yerel ayarlar ve node_modules/ gibi bağımlılıklar hariç tutulmalıdır. Detaylı yönerge için [GIT_PUSH_GUIDE.md](GIT_PUSH_GUIDE.md).

## Gizli Bilgiler
- `settings.local.json`, `.env` ve benzeri dosyalar repoya eklenmemelidir. Bu dosyaları `.gitignore` dosyanıza ekleyin.

## İletişim
Proje sahibi: (sizin iletişim bilgileriniz)

