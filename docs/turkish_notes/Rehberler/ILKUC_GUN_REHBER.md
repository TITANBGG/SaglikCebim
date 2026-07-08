# 🚀 HIZLI BAŞLANGIÇ REHBERİ - İLK 3 GÜN

## 📅 GÜN 1: KURULUM GÜNÜ (3 saat)

### ⏰ ZAMAN PLANI
- 09:00 - 10:00: Araçları indir
- 10:00 - 11:30: Git + VS Code kurulum
- 11:30 - 12:00: İlk repo oluştur

---

### 📝 ADIM ADIM TALİMATLAR

#### ADIM 1: DOCKER KURULUMU (20 dk)

**Windows:**
```
1. https://www.docker.com/products/docker-desktop/ aç
2. "Download for Windows" tıkla
3. İndirilen .exe dosyasını çalıştır
4. "Install" tıkla, bekle
5. Bilgisayarı yeniden başlat
6. Docker Desktop'ı aç
7. Terminal aç, yaz: docker --version
8. Versiyon görüyorsan ✅ TAMAM
```

**Mac:**
```
1. https://www.docker.com/products/docker-desktop/ aç
2. "Download for Mac" tıkla
3. .dmg dosyasını aç
4. Docker'ı Applications'a sürükle
5. Docker Desktop'ı aç
6. Terminal aç, yaz: docker --version
7. Versiyon görüyorsan ✅ TAMAM
```

**❌ Sorun varsa Claude'a sor:**
```
"Claude, Docker kurulumunda şu hatayı aldım: [hata mesajı]"
```

---

#### ADIM 2: NODE.JS KURULUMU (10 dk)

**Tüm işletim sistemleri:**
```
1. https://nodejs.org aç
2. LTS versiyonunu indir (v20.x)
3. Kurulumu çalıştır, hep "Next" tıkla
4. Terminal aç, yaz: node --version
5. Versiyon görüyorsan ✅ TAMAM
```

---

#### ADIM 3: PYTHON KURULUMU (10 dk)

**Windows:**
```
1. https://www.python.org/downloads/ aç
2. "Download Python 3.11.x" tıkla
3. Kurulumu çalıştır
4. ⚠️ ÖNEMLİ: "Add Python to PATH" kutusunu işaretle!
5. "Install Now" tıkla
6. Terminal aç, yaz: python --version
7. Versiyon görüyorsan ✅ TAMAM
```

**Mac:**
```
1. Terminal aç
2. Yaz: brew install python@3.11
   (Homebrew yoksa önce: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
3. Yaz: python3 --version
4. Versiyon görüyorsan ✅ TAMAM
```

---

#### ADIM 4: VS CODE KURULUMU (10 dk)

```
1. https://code.visualstudio.com/ aç
2. İşletim sistemine göre indir
3. Kurulumu çalıştır
4. VS Code'u aç
5. Sol taraftan Extensions'a git (kare içinde 4 kare ikonu)
6. Şu extension'ları ara ve kur:
   - Python
   - Prettier
   - ES7+ React/Redux/React-Native snippets
   - Tailwind CSS IntelliSense
7. ✅ TAMAM
```

---

#### ADIM 5: GİT KURULUMU (10 dk)

**Windows:**
```
1. https://git-scm.com/download/win aç
2. İndir, çalıştır
3. Hep "Next" tıkla (default ayarlar OK)
4. Terminal aç, yaz: git --version
5. Versiyon görüyorsan ✅ TAMAM
```

**Mac:**
```
1. Terminal aç
2. Yaz: git --version
3. Zaten varsa ✅ TAMAM
4. Yoksa: xcode-select --install
```

**Git config:**
```bash
git config --global user.name "Senin Adın"
git config --global user.email "email@example.com"
```

---

#### ADIM 6: İLK REPO OLUŞTUR (20 dk)

**Terminal'de yaz (SATIR SATIR):**

```bash
# 1. Klasör oluştur
mkdir saglikcebim
cd saglikcebim

# 2. Git başlat
git init

# 3. README oluştur
echo "# SağlıkCebim - Tıbbi Tahlil Analiz Platformu" > README.md
echo "" >> README.md
echo "Başlangıç tarihi: $(date)" >> README.md

# 4. .gitignore oluştur
```

**Şimdi Claude'a sor:**
```
"Claude, Python + React projesi için .gitignore dosyası verir misin?"
```

**Claude'dan geleni kopyala, yapıştır:**
```bash
# Terminal'de
cat > .gitignore
# (Claude'dan aldığın metni yapıştır)
# Ctrl+D (Mac: Cmd+D) ile kaydet
```

**İlk commit:**
```bash
git add .
git commit -m "🚀 İlk commit - Proje başlangıcı"
```

---

### ✅ GÜN 1 SONU KONTROLÜ

Hepsini yap, işaretle:

- [ ] Docker çalışıyor: `docker --version`
- [ ] Node.js çalışıyor: `node --version`
- [ ] Python çalışıyor: `python --version`
- [ ] Git çalışıyor: `git --version`
- [ ] VS Code kurulu
- [ ] Git repo oluşturuldu
- [ ] İlk commit atıldı

**Hepsi ✅ ise → Mükemmel! Yarın GÜN 2'ye geç!**

---

## 📅 GÜN 2: BACKEND BAŞLANGIÇ (4 saat)

### ADIM 1: Klasör Yapısı (5 dk)

**Terminal'de (saglikcebim/ klasöründe):**

```bash
# Backend klasörü
mkdir backend
cd backend
mkdir app
mkdir tests
cd app
mkdir api core models services
cd api
mkdir v1
cd ../../..
# Şimdi saglikcebim/ klasöründesin
```

**Kontrol et:**
```bash
tree backend
# Veya Windows: dir backend /s
```

**Görmeni gereken:**
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── models/
│   └── services/
└── tests/
```

---

### ADIM 2: FastAPI Kurulumu (10 dk)

**Terminal'de (saglikcebim/backend klasöründe):**

```bash
cd backend

# Python sanal ortam oluştur
python -m venv venv

# Aktif et
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# (venv) görmelisin terminalin başında
```

**Şimdi Claude'a sor:**
```
"Claude, bana FastAPI projesi için requirements.txt ver"
```

**Claude'dan geleni kaydet:**
```bash
# Terminal'de
cat > requirements.txt
# (Claude'dan aldığın listeyi yapıştır)
# Ctrl+D ile kaydet
```

**Kur:**
```bash
pip install -r requirements.txt
```

---

### ADIM 3: İlk FastAPI Kodu (15 dk)

**Claude'a sor:**
```
"Claude, bana basit bir FastAPI main.py dosyası ver. 
Sadece health check endpoint'i olsun."
```

**Claude'dan geleni kaydet:**

```bash
cd app
# VS Code'da aç
code main.py
```

**Claude'dan gelen kodu yapıştır, kaydet (Ctrl+S)**

---

### ADIM 4: İlk Test (5 dk)

**Terminal'de (backend/ klasöründe, venv aktif):**

```bash
uvicorn app.main:app --reload
```

**Görmeni gereken:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Tarayıcıda aç:**
```
http://localhost:8000/health
```

**Görmeni gereken:**
```json
{"status": "ok"}
```

**✅ Görüyorsan → BAŞARILI!**

---

### ADIM 5: Swagger Dokümantasyonu (2 dk)

**Tarayıcıda aç:**
```
http://localhost:8000/docs
```

**Swagger UI görmelisin!**

**Screenshot al → Daha sonra rapora koyarsın**

---

### ADIM 6: Git Commit (5 dk)

**Terminal'de (CTRL+C ile uvicorn'u durdur):**

```bash
cd ..
# saglikcebim/ klasöründesin

git add .
git commit -m "feat: FastAPI backend kuruldu, health check endpoint eklendi"
```

---

### ✅ GÜN 2 SONU KONTROLÜ

- [ ] Backend klasör yapısı doğru
- [ ] requirements.txt var
- [ ] main.py var
- [ ] `uvicorn` çalışıyor
- [ ] http://localhost:8000/health açılıyor
- [ ] http://localhost:8000/docs açılıyor
- [ ] Git commit atıldı

**Hepsi ✅ ise → Süper! Yarın frontend!**

---

## 📅 GÜN 3: FRONTEND BAŞLANGIÇ (4 saat)

### ADIM 1: React Projesi Oluştur (10 dk)

**Terminal'de (saglikcebim/ klasöründe):**

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

**Bekle... (2-3 dakika sürebilir)**

---

### ADIM 2: İlk Test (2 dk)

```bash
npm run dev
```

**Tarayıcıda otomatik açılacak:**
```
http://localhost:5173
```

**Vite + React logosu görmelisin!**

**✅ Görüyorsan → BAŞARILI!**

**CTRL+C ile durdur**

---

### ADIM 3: Tailwind CSS Kurulumu (15 dk)

**Claude'a sor:**
```
"Claude, React + Vite projesine Tailwind CSS nasıl kurulur? 
Adım adım komutları ver."
```

**Claude'dan gelen komutları SATIR SATIR çalıştır**

**Örnek olacak komutlar (Claude'dan al):**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Claude'a tekrar sor:**
```
"Claude, tailwind.config.js dosyasını düzenle (content paths)"
"Claude, index.css'e Tailwind direktiflerini ekle"
```

---

### ADIM 4: İlk Component (20 dk)

**Claude'a sor:**
```
"Claude, bana basit bir Button componenti yaz (Tailwind ile)"
```

**VS Code'da:**

```bash
# frontend/src klasöründe
mkdir components
cd components
code Button.jsx
```

**Claude'dan gelen kodu yapıştır**

---

### ADIM 5: Test Et (5 dk)

**Claude'a sor:**
```
"Claude, App.jsx'i düzenle, Button componentini kullan"
```

**App.jsx'i değiştir (Claude'dan gelen kodla)**

**Terminal'de:**
```bash
npm run dev
```

**Tarayıcıda:**
```
http://localhost:5173
```

**Tailwind'li butonu görmelisin!**

---

### ADIM 6: Git Commit (5 dk)

```bash
cd ..
# saglikcebim/ klasöründesin

git add .
git commit -m "feat: React frontend kuruldu, Tailwind eklendi"
```

---

### ✅ GÜN 3 SONU KONTROLÜ

- [ ] Frontend klasörü var
- [ ] `npm run dev` çalışıyor
- [ ] Tailwind CSS çalışıyor (test butonu renkli)
- [ ] Button componenti çalışıyor
- [ ] Git commit atıldı

---

## 🎉 İLK 3 GÜN TAMAMLANDI!

### ✅ Şu an elimizde ne var?

```
saglikcebim/
├── backend/
│   ├── app/
│   │   └── main.py (FastAPI health check)
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Button.jsx
│   │   └── App.jsx
│   └── package.json
├── README.md
└── .gitignore
```

### ✅ Ne çalışıyor?

- Backend: http://localhost:8000/health ✅
- Frontend: http://localhost:5173 ✅
- Git: En az 3 commit ✅

---

## 📞 SONRAKI ADIM

**Hafta 1 Gün 4'e geç:**
- Docker Compose kurulumu
- PostgreSQL

**Claude'a sor:**
```
"Claude, Hafta 1 Gün 4'teyim. Docker Compose ile PostgreSQL nasıl kurarım?"
```

---

## 🆘 SIKIŞIRSAN

### Backend çalışmıyor:
```
1. venv aktif mi? (terminal başında (venv) var mı?)
2. requirements.txt kuruldu mu? (pip list | grep fastapi)
3. Port 8000 dolu mu? (başka uygulama kullanıyor olabilir)
```

### Frontend çalışmıyor:
```
1. node_modules var mı? (npm install yaptın mı?)
2. Port 5173 dolu mu?
```

### Her şey çalışıyor ama anlamıyorum:
```
Claude'a sor: "Bu kodları satır satır açıklar mısın?"
```

---

## 💪 MOTİVASYON

**3 günde şunları yaptın:**

✅ 5 araç kurdun (Docker, Node, Python, Git, VS Code)  
✅ Backend kurdun (FastAPI)  
✅ Frontend kurdun (React + Tailwind)  
✅ İlk commit'lerini attın  

**→ İLK ADIMI ATTIN! 🎉**

**Devam et, sen yaparsın! 💪**
