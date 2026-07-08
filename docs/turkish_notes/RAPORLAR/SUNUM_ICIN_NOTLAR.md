# 🎤 Sunum Icin Notlar - SaglikCebim

**Tarih:** 01 Nisan 2026  
**Amac:** Yarin yapilacak sunumda teknik, urun ve klinik degeri net anlatmak  
**Sure Onerisi:** 12-15 dakika + 5 dakika soru-cevap

---

## 1) 30 Saniyelik Acilis Konusmasi

SaglikCebim, kan tahlili raporlari ve radyoloji goruntulerini tek platformda analiz ederek kullaniciya anlasilir bir saglik ozeti sunan yapay zeka destekli bir karar-destek uygulamasidir. Projede hedefimiz, tek bir model gostermek degil; laboratuvar, anamnez ve goruntu bulgularini bir araya getirerek anlamli klinik baglam olusturmaktir.

---

## 2) Problem ve Cozum

### Problem
1. Kullanici raporlari farkli formatlarda geliyor ve manuel yorum zor.
2. Sonuclar tarihsel olarak takip edilmiyor.
3. Radyoloji ciktilari teknik ama kullaniciya aciklamasi zor.

### Cozum
1. PDF yukleme ile otomatik test sonucu cikarma.
2. Trend ekrani ile zaman bazli degisim analizi.
3. Radyoloji AI sonucu + isi haritasi + rapor indirme.
4. Anamnez modulu ile klinik baglam guclendirme.

---

## 3) Kullanilan Teknolojiler (Detayli)

### Frontend
1. React 19
2. Vite 8
3. Tailwind CSS 4
4. React Router DOM 7
5. Axios
6. Recharts
7. Lucide React
8. PWA (vite-plugin-pwa)
9. Spline entegrasyonu (gorsel/animasyon)

### Backend
1. FastAPI 0.109
2. Uvicorn
3. Pydantic 2
4. SQLAlchemy 2
5. Alembic
6. JWT (python-jose) + Passlib
7. PDF isleme: pdfplumber
8. PDF rapor: reportlab
9. HTTP istemci: httpx
10. Zamanlanmis gorevler: APScheduler

### AI ve Goruntu Isleme
1. PyTorch
2. Torchvision
3. NumPy
4. Matplotlib
5. Pydicom
6. DenseNet-121 tabanli radyoloji siniflandirma
7. Grad-CAM benzeri aciklanabilirlik haritalari

### DevOps
1. Docker Compose
2. PostgreSQL 15
3. Uretim kaynak limitleri (CPU/RAM) ile daha stabil calisma

---

## 4) Mimari Ozeti (Sunum Slayti Icin Hazir)

1. Frontend (React) kullanicidan veri alir.
2. Backend (FastAPI) kimlik dogrular, analiz servislerini cagirir.
3. Veritabani (PostgreSQL) kullanici, rapor ve bulgu verilerini saklar.
4. AI servisleri radyoloji goruntusunu isler ve olasilik ciktilari uretir.
5. Sonuclar UI'da risk, bulgu listesi, isi haritasi ve rapor olarak sunulur.

---

## 5) Demo Akisi (Canli Gosterim Sirasi)

### A) Giris ve Dashboard (2 dk)
1. Login ekrani
2. Dashboard genel gorunum
3. Moduller arasi gecis

### B) Kan Tahlili Akisi (4 dk)
1. PDF yukle
2. Otomatik ayrisma ve test sonuclari
3. Trend grafikleri
4. PDF rapor indir

### C) Radyoloji Akisi (4 dk)
1. X-ray yukleme
2. Sonuclar ekrani
3. Ana bulgu + alternatif bulgular
4. Orijinal / Islenmis / Isi Haritasi / Bolunmus gorunum
5. Rapor indir

### D) Anamnez Akisi (2 dk)
1. Anamnez baslangic ekrani
2. Akilli giris adimlari
3. Standart terim secimi ile veri kalitesi (dedup mantigi)

---

## 6) Teknik Olgunluk ve Guvenilirlik Notlari

1. Kimlik dogrulama JWT tabanli.
2. API katmani dokumante (Swagger).
3. Veritabani migration yapisi mevcut.
4. Frontend lint/build kapisi kullaniliyor.
5. Radyoloji tarafinda aciklanabilirlik goruntuleme eklendi.

### Sinirlar (Dogrudan soylenecek)
1. Bu bir karar-destek sistemi; tek basina tibbi taninin yerine gecmez.
2. Isi haritasi tani kaniti degil, model dikkat haritasidir.
3. Klinik kalibrasyon ve multimodal birlestirme calismalari devam ediyor.

---

## 7) Basari Gostergeleri (Sunumda Verilebilecek)

1. Uctan uca akista kullanici girisinden rapor indirmeye kadar tam zincir calisiyor.
2. Frontend ve backend ayrik ama uyumlu mimari ile ilerliyor.
3. Radyoloji ekraninda aciklanabilirlik ve detay goruntuleme modlari aktif.
4. Anamnezde standart secim yapisi ile veri tutarliligi artirildi.

---

## 8) Soru-Cevap Icin Hazir Kisa Yanitlar

### Soru: Model yuzde kac dogru?
Yanit: Gorev bazli metrikler ve sinif bazli performans raporlari uretiyoruz. Klinikte dogrudan tani iddiasi degil, karar-destek odakli yaklasim benimsiyoruz.

### Soru: Neden birden fazla bulgu yuksek cikiyor?
Yanit: Problem multi-label yapida. Bu nedenle birden fazla bulgu ayni anda yuksek olabilir. UI tarafinda ana bulgu ve alternatif bulgular ayrimi ile bunu daha anlasilir hale getirdik.

### Soru: Isi haritasi neyi gosteriyor?
Yanit: Modelin hangi bolgelere dikkat ettigini gosterir. Bu alanlar klinik yorum icin yardimci gorusel veri sunar ancak tek basina tani yerine gecmez.

### Soru: Sistem hastane entegrasyonuna uygun mu?
Yanit: Mimari bu yonde tasarlandi. Sonraki asamada FHIR/standart kod sistemleri ile entegrasyon planlaniyor.

---

## 9) Yarin Icin Kontrol Listesi

1. Backend calisiyor mu: `http://localhost:8000/health`
2. Frontend acik mi: `http://localhost:5173`
3. Login test hesabi hazir mi
4. Demo PDF ve demo X-ray dosyalari masaustunde hazir mi
5. Internet olmasa da gosterilecek akisin yerel calisma plani hazir mi
6. Rapor indir butonlari test edildi mi
7. Kritik ekranlar icin yedek ekran goruntuleri hazir mi

---

## 10) Kapanis Cumlesi (Hazir Metin)

SaglikCebim ile hedefimiz, daigik ve zor yorumlanan saglik verilerini tek bir akista toplayip kullaniciya ve hekime daha hizli, daha anlasilir ve daha baglamli bir karar-destek deneyimi sunmak. Sunulan sistem, bugunden calisan bir temel ve yarinin multimodal klinik zekasi icin guclu bir altyapi olusturuyor.

---

## 11) Plan B (Canli Demo Sorunu Olursa)

### Senaryo 1: Frontend acilmaz
1. Ekran goruntuleri ile akisi anlat:
	- Login
	- Dashboard
	- Kan tahlili sonucu
	- Radyoloji isi haritasi
	- Anamnez wizard
2. API'nin ayakta oldugunu `http://localhost:8000/docs` ile goster.

### Senaryo 2: Backend gec acilir
1. Once UI akisini statik anlatimla goster.
2. Bu sirada backend komutlarini calistir.
3. Canli kisma sadece tek akista gec: Radiology Sonuclar + Rapor indir.

### Senaryo 3: Model cikti vermez
1. Onceki kaydedilmis analiz kaydini ac.
2. Isi haritasi ve Ana Bulgu/Alternatif Bulgu ekranini goster.
3. "Karar-destek" kapsamini tekrar vurgula.

---

## 12) Net Baslatma ve Kapatma Komutlari

### Docker servisleri
1. Baslat:
	- `cd Kod/saglikcebim`
	- `docker-compose -f docker-compose.prod.yml up -d`
2. Durum:
	- `docker-compose -f docker-compose.prod.yml ps`
3. Kapat:
	- `docker-compose -f docker-compose.prod.yml down`

### Backend (FastAPI)
1. `cd Kod/saglikcebim/backend`
2. `./venv/Scripts/activate.ps1`
3. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend (Vite)
1. `cd Kod/saglikcebim/frontend`
2. `npm install`
3. `npm run dev -- --host 127.0.0.1 --port 5173`

### Hizli saglik kontrolu
1. Backend: `http://localhost:8000/health`
2. Swagger: `http://localhost:8000/docs`
3. Frontend: `http://127.0.0.1:5173`

---

## 13) Klinik ve Urun Beyani (Sunumda Acik Soylenecek)

1. Bu platform tani koyan bir sistem degil, karar-destek sistemidir.
2. Model olasilik skorlarini ve dikkat haritalarini sunar.
3. Nihai klinik karar hekim degerlendirmesi ile verilmelidir.
4. Isi haritasi, modelin dikkat bolgesini gosterir; tek basina tani kaniti degildir.
5. Ciktilar, anamnez ve laboratuvar baglami ile birlikte yorumlanmalidir.

---

## 14) 2 Dakikalik Kapanis Metni

Bugun gosterdigimiz sistemle, saglik verisini parcali degil butunsel ele almayi hedefliyoruz. Kan tahlili, radyoloji ve anamnez akislari tek bir platformda birlestiginde, kullaniciya sadece veri degil anlamli baglam sunabiliyoruz. Teknik olarak calisan bir temelimiz var; urun olarak da aciklanabilirlik, risk semantigi ve kullanici deneyimi tarafini guclendiriyoruz. Klinik tarafta ise sinirlari net ciziyoruz: bu bir karar-destek araci, tani yerine gecen bir sistem degil. Sonraki adimda multimodal birlestirme ile daha tutarli, daha guvenilir ve daha eyleme donuk ciktilar ureterek gercek dunya etkisini artirmayi planliyoruz.

---

## 15) Olculebilir Etki Basliklari (Sunum Slaydi Icin)

1. Uctan uca canli akista 3 ana mod ulasilabilir:
	- Kan Tahlili
	- Radyoloji
	- Anamnez
2. Radyoloji ekraninda 4 goruntuleme modu:
	- Orijinal
	- Islenmis Harita
	- Isi Haritasi
	- Bolunmus Gorunum
3. Raporlama akisi mevcut:
	- Sonuc ekrani
	- PDF rapor indirme
4. Gelistirme olgunlugu gostergeleri:
	- Frontend build kapisi
	- API dokumantasyonu (Swagger)
	- Veritabani migration altyapisi

---

**Hazirlayan:** Copilot ile teknik sunum notu hazirligi  
**Durum:** ✅ Sunuma Hazir
