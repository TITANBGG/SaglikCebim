# 🗺️ SAĞLIKCE BİM - DETAYLI 10 HAFTALIK MASTER PLAN

## 📋 GENEL BAKIŞ

**Başlangıç:** Bugünden itibaren  
**Süre:** 10 hafta (net çalışma)  
**Toplam Saat:** ~300 saat  
**Başarı İhtimali:** %95  

---

## 🎯 CLAUDE İLE ÇALIŞMA PRENSİPLERİ

### **CLAUDE'UN YAPACAĞI (%70):**
- Boilerplate kod yazma
- Backend logic
- Database schema
- API endpoints
- Regex patterns
- Test yazma
- Bug fixing yardımı
- Dokümantasyon

### **SENİN YAPACAĞIN (%30):**
- Komutları çalıştırma
- Kod'u anlama ve öğrenme
- UI tasarım kararları
- Test etme (manuel)
- Bug raporlama
- Git commit'leme
- Öğrendiklerini not alma

### **BİRLİKTE YAPACAĞIMIZ:**
- Mimari kararlar
- Özellik önceliklendirme
- Sorun çözme
- Code review
- Refactoring

---

## 📁 PROJE KLASÖR YAPISI (İLK GÜNDEN İTİBAREN)

```
saglikcebim/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── reports.py
│   │   │       └── analysis.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── report.py
│   │   ├── services/
│   │   │   └── pdf_parser.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 🗓️ HAFTA HAFTA DETAYLI PLAN

---

# HAFTA 1: ALTYAPI KURULUMU

## 🎯 Hedef
Docker, PostgreSQL, Git kurulumu ve boilerplate proje yapısı

## 📅 Günlük Plan

### **GÜN 1 (Pazartesi) - 3 saat**

#### ☑️ Yapılacaklar:
1. Git kurulumu (eğer yoksa)
2. Docker Desktop kurulumu
3. Node.js kurulumu (v18+)
4. Python kurulumu (v3.11+)
5. VS Code kurulumu + extension'lar

#### 💬 Claude'a Soracakların:
```
"Claude, bana VS Code'da hangi extension'ları kurmalıyım?"
"Git için .gitignore dosyası hazırlar mısın?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] `docker --version` çalışıyor
- [ ] `node --version` çalışıyor
- [ ] `python --version` çalışıyor
- [ ] Git repo oluşturuldu

---

### **GÜN 2 (Salı) - 4 saat**

#### ☑️ Yapılacaklar:
1. Backend klasör yapısı oluştur
2. FastAPI boilerplate
3. requirements.txt
4. İlk API endpoint (health check)

#### 💬 Claude'a Soracakların:
```
"Claude, bana FastAPI boilerplate kodu ver"
"requirements.txt nasıl olmalı?"
"İlk basit endpoint nasıl yazarım?"
```

#### 🎯 Kod Örneği (Claude'dan alacaksın):
```python
# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

#### ✅ Gün Sonu Kontrolü:
- [ ] `uvicorn app.main:app --reload` çalışıyor
- [ ] http://localhost:8000/health açılıyor
- [ ] {"status": "ok"} görüyorsun

---

### **GÜN 3 (Çarşamba) - 4 saat**

#### ☑️ Yapılacaklar:
1. Frontend klasör yapısı
2. React + Vite kurulumu
3. İlk component
4. Tailwind CSS kurulumu

#### 💬 Claude'a Soracakların:
```
"React + Vite projesi nasıl oluştururum?"
"Tailwind CSS nasıl kurarım?"
"Basit bir Button componenti yazar mısın?"
```

#### 🎯 Komutlar (Claude'dan alacaksın):
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
```

#### ✅ Gün Sonu Kontrolü:
- [ ] `npm run dev` çalışıyor
- [ ] http://localhost:5173 açılıyor
- [ ] Tailwind çalışıyor (test butonu renkli)

---

### **GÜN 4 (Perşembe) - 4 saat**

#### ☑️ Yapılacaklar:
1. PostgreSQL Docker container
2. docker-compose.yml
3. Database bağlantısı test

#### 💬 Claude'a Soracakların:
```
"docker-compose.yml dosyası yazar mısın? (PostgreSQL + Redis)"
"Database bağlantı kodu nasıl olmalı?"
```

#### 🎯 Dosya (Claude'dan alacaksın):
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: saglikcebim
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] `docker-compose up -d` çalışıyor
- [ ] PostgreSQL container ayakta
- [ ] Backend'den DB'ye bağlanabiliyor

---

### **GÜN 5 (Cuma) - 3 saat**

#### ☑️ Yapılacaklar:
1. SQLAlchemy kurulumu
2. İlk model (User)
3. Alembic migration

#### 💬 Claude'a Soracakların:
```
"SQLAlchemy User modeli yazar mısın?"
"Alembic migration nasıl yapılır?"
"Database tabloları nasıl oluştururum?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] User tablosu DB'de var
- [ ] Migration çalıştı
- [ ] İlk commit atıldı

---

### **HAFTA SONU (Cumartesi-Pazar) - 8 saat**

#### ☑️ Yapılacaklar:
1. README.md yazma
2. Öğrendiklerini not alma
3. Eksikleri tamamlama
4. Next week preview

#### 💬 Claude'a Soracakların:
```
"README.md için template verir misin?"
"Hafta 1'de öğrendiğim şeylerin özeti nedir?"
```

#### ✅ Hafta Sonu Kontrolü:
- [ ] Backend health check çalışıyor
- [ ] Frontend ana sayfa açılıyor
- [ ] PostgreSQL bağlantısı OK
- [ ] Git'te en az 5 commit var
- [ ] README.md güncel

---

# HAFTA 2: AUTH SİSTEMİ

## 🎯 Hedef
Kullanıcı kaydı, login, JWT token sistemi

## 📅 Günlük Plan

### **GÜN 1 (Pazartesi) - 4 saat**

#### ☑️ Yapılacaklar:
1. JWT kütüphanesi kurulumu
2. Password hashing (bcrypt)
3. Security utility functions

#### 💬 Claude'a Soracakların:
```
"JWT token sistemi nasıl kurulur?"
"Password hashing kodu yazar mısın?"
"Security config dosyası ver"
```

#### 🎯 Alacağın Kod:
- `core/security.py` (hash_password, verify_password, create_token)
- `core/config.py` (SECRET_KEY, ALGORITHM)

#### ✅ Gün Sonu Kontrolü:
- [ ] Password hash'lenebiliyor
- [ ] Token oluşturabiliyor

---

### **GÜN 2 (Salı) - 4 saat**

#### ☑️ Yapılacaklar:
1. Register endpoint
2. Login endpoint
3. Pydantic schemas

#### 💬 Claude'a Soracakların:
```
"Register endpoint kodu ver"
"Login endpoint nasıl yazılır?"
"UserCreate, UserLogin schema'ları ver"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] POST /auth/register çalışıyor
- [ ] POST /auth/login çalışıyor
- [ ] Token dönüyor

---

### **GÜN 3 (Çarşamba) - 4 saat**

#### ☑️ Yapılacaklar:
1. Frontend: Login sayfası
2. Axios kurulumu
3. API çağrısı

#### 💬 Claude'a Soracakların:
```
"React'te Login formu componenti yaz"
"Axios ile API nasıl çağırılır?"
"Form validation nasıl yapılır?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] Login formu görünüyor
- [ ] API çağrısı yapabiliyor
- [ ] Token localStorage'a kaydediliyor

---

### **GÜN 4 (Perşembe) - 4 saat**

#### ☑️ Yapılacaklar:
1. Register sayfası
2. Protected routes
3. Auth context

#### 💬 Claude'a Soracakların:
```
"Register sayfası komponenti ver"
"React'te protected route nasıl yapılır?"
"Auth context/state management?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] Register çalışıyor
- [ ] Login sonrası yönlendirme OK
- [ ] Logout çalışıyor

---

### **GÜN 5 (Cuma) - 3 saat**

#### ☑️ Yapılacaklar:
1. Error handling
2. Loading states
3. Form validation

#### 💬 Claude'a Soracakların:
```
"Error handling nasıl yapmalıyım?"
"Loading spinner ekle"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] Hatalı login'de mesaj gösteriliyor
- [ ] Loading durumu var

---

### **HAFTA SONU - 8 saat**

#### ☑️ Yapılacaklar:
1. Auth sistemi test et
2. Bug fix
3. UI polish
4. Commit + push

#### ✅ Hafta Sonu Kontrolü:
- [ ] Kayıt olabiliyorsun
- [ ] Login yapabiliyorsun
- [ ] Token çalışıyor
- [ ] Protected route test edildi

---

# HAFTA 3: PDF UPLOAD UI

## 🎯 Hedef
PDF dosyası yükleme arayüzü

## 📅 Günlük Plan

### **GÜN 1 (Pazartesi) - 4 saat**

#### ☑️ Yapılacaklar:
1. Upload endpoint (backend)
2. Multipart form data handling
3. File validation

#### 💬 Claude'a Soracakların:
```
"FastAPI'de file upload endpoint'i nasıl yazılır?"
"PDF validation kodu ver"
"Dosya boyutu kontrolü nasıl yapılır?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] POST /reports/upload endpoint var
- [ ] PDF kabul ediyor
- [ ] 10MB limit çalışıyor

---

### **GÜN 2 (Salı) - 4 saat**

#### ☑️ Yapılacaklar:
1. Frontend upload component
2. Drag & drop (opsiyonel)
3. File preview

#### 💬 Claude'a Soracakların:
```
"React'te file upload komponenti yaz"
"Drag and drop nasıl yapılır?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] PDF seçebiliyor
- [ ] Upload butonu çalışıyor

---

### **GÜN 3 (Çarşamba) - 3 saat**

#### ☑️ Yapılacaklar:
1. Progress bar
2. Success/error mesajları
3. UI polish

#### ✅ Gün Sonu Kontrolü:
- [ ] Upload sırasında progress gösteriliyor
- [ ] Başarı mesajı çıkıyor

---

### **GÜN 4-5 - Hafif çalışma, hazırlık**

VİZE HAFTASINA HAZIRLIK - Kod azalt, ders çalış

---

# 🎓 VİZE HAFTASI (HAFTA 4-5 ARASI) - 0 KOD!

**TAM MOLA!**
- Sadece derslerine çalış
- Projeyi unut
- Kafanı dinlendir

---

# HAFTA 4: PDF PARSING (1) - VİZE SONRASI

## 🎯 Hedef
pdfplumber kurulumu, ilk 2 regex pattern

## 📅 Günlük Plan

### **GÜN 1 (Pazartesi) - 4 saat**

#### ☑️ Yapılacaklar:
1. pdfplumber kurulumu
2. Basit PDF okuma
3. Text extraction

#### 💬 Claude'a Soracakların:
```
"pdfplumber ile PDF nasıl okunur?"
"Text extraction kodu ver"
"Basit bir parse fonksiyonu yaz"
```

#### 🎯 Test için:
- Arkadaşlarından 2 farklı lab PDF'i iste
- Veya Google'dan örnek tahlil PDF'i bul

#### ✅ Gün Sonu Kontrolü:
- [ ] PDF açabiliyor
- [ ] Text çıkarabiliyor
- [ ] Console'da metin görünüyor

---

### **GÜN 2 (Salı) - 5 saat**

#### ☑️ Yapılacaklar:
1. İlk regex pattern
2. Basit test (Hemoglobin)
3. Value extraction

#### 💬 Claude'a Soracakların:
```
"Hemoglobin değerini çıkarmak için regex yaz"
"Pattern: 'Hemoglobin 13.5 g/dL 12.0-16.0'"
"Extract: test_name, value, unit, ref_min, ref_max"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] Hemoglobin değerini yakalayabiliyor
- [ ] Parsed data JSON olarak dönüyor

---

### **GÜN 3 (Çarşamba) - 5 saat**

#### ☑️ Yapılacaklar:
1. İkinci regex pattern
2. Farklı format desteği
3. Test expansion

#### 💬 Claude'a Soracakların:
```
"Farklı format için regex: 'HGB: 13.5 (g/dL) [12-16]'"
"Multi-pattern support nasıl eklenir?"
```

#### ✅ Gün Sonu Kontrolü:
- [ ] 2 farklı format parse ediliyor
- [ ] En az 3 test (Hemoglobin, Glukoz, WBC)

---

### **GÜN 4-5 + Hafta Sonu - 10 saat**

#### ☑️ Yapılacaklar:
1. 3. pattern
2. Test data ile deneme
3. Edge case handling

#### ✅ Hafta Sonu Kontrolü:
- [ ] 3 farklı format çalışıyor
- [ ] 5+ test değeri çıkarabiliyor
- [ ] Parse başarı oranı ~%70

---

# HAFTA 5: PDF PARSING (2) + REFERANS

## 🎯 Hedef
Normalizasyon, referans karşılaştırma

[... devam eder, her hafta için benzer detay]

---

# HAFTA 6-10: [Özet]

**HAFTA 6:** Referans DB + Analiz Logic  
**HAFTA 7:** Dashboard + Liste  
**HAFTA 8:** Trend Grafiği  
**HAFTA 9:** PubMed (basit) + BAYRAM MOLASI  
**HAFTA 10:** Test + Deployment + FİNAL HAZIRLIK  

---

## 📝 HER GÜN SONUNDA YAPILACAKLAR

```
1. ✅ Git commit at
   git add .
   git commit -m "feat: bugünkü özellik açıklaması"

2. ✅ Çalışan kısmı test et
   - Backend: API test (Postman/curl)
   - Frontend: Tarayıcıda kontrol

3. ✅ Yarına not bırak
   - TODO.md dosyasına yaz
   - "Yarın şunu yapacağım"

4. ✅ Öğrendiklerini not al
   - LEARNINGS.md dosyası tut
   - "Bugün JWT öğrendim" gibi
```

---

## 🆘 SIKIŞIRSAN NE YAP?

### Kod çalışmıyorsa:
```
1. Claude'a hata mesajını göster tam olarak
2. "Bu hatayı nasıl çözerim?" diye sor
3. Stack Overflow'a bakma, önce Claude'a sor
```

### Anlayamadığın kod varsa:
```
1. Claude'a "Bu kodu satır satır açıklar mısın?" de
2. Her satırı öğren
3. Ezberleme, mantığını anla
```

### Zaman yetersizse:
```
1. Claude'a "Bu özelliği basitleştirebilir miyiz?" sor
2. Bonus özellikleri atla
3. Core'a odaklan
```

---

## 🎯 CHECKPOINT'LER (Mutlaka Kontrol Et)

**Hafta 2 Sonu:**
- [ ] Login çalışıyor mu?

**Hafta 5 Sonu (En kritik!):**
- [ ] PDF parse ediliyor mu?
- [ ] En az 3 format destekleniyor mu?

**Hafta 8 Sonu:**
- [ ] Dashboard güzel görünüyor mu?
- [ ] Grafik var mı?

**Hafta 10 Sonu:**
- [ ] Tüm özellikler çalışıyor mu?
- [ ] Demo yapabilir misin?

---

## 📞 CLAUDE'A NE ZAMAN SORMALIYIM?

### ✅ Kesinlikle sor:
- Yeni bir özellik başlayacaksan
- Hata aldığında
- Kod örneği istediğinde
- "Best practice" merak ettiğinde
- Refactor gerektiğinde

### ❌ Sorma (önce kendin dene):
- Basit syntax hataları (Google)
- Komut nasıl çalıştırılır (dokümantasyon)
- Çok basit CSS değişiklikleri

---

## 🎓 ÖĞRENME STRATEJİSİ

1. **Kodu kopyala-yapıştır yapma!**
   - Claude'dan aldığın kodu oku
   - Anla
   - Sonra yaz

2. **Her gün bir şey öğren**
   - LEARNINGS.md tut
   - "Bugün ne öğrendim?"

3. **Hata yapmaktan korkma**
   - Broken kod OK
   - Git var, geri dönebilirsin

---

## 💾 YEDEKLENacceptME

```bash
# Her gün
git push origin main

# Her hafta sonu
git tag -a v0.1 -m "Hafta 1 tamamlandı"
git push --tags
```

---

## 🎉 BAŞARI KRİTERLERİ

**Hafta 5'te (MVP):**
- PDF yüklenebiliyor
- Parse ediliyor
- Sonuç gösteriliyor
→ **Bu kadar olsa geçersin!**

**Hafta 10'da (Full):**
- Login var
- Dashboard var
- Grafik var
- PubMed var
→ **80+ not alırsın!**

---

## 📞 ACİL DURUM PLANI

**Eğer çok sıkışırsan:**

1. Hafta 9 → PubMed'i atla
2. Hafta 8 → Grafik basitleştir
3. Hafta 7 → Dashboard basit liste yap

**Minimum yapılacaklar:**
- Login
- PDF parse
- Basit sonuç gösterimi

**Bu 3'ü yap, 70 puan kesin!**

---

## ✅ GÜNLÜK RUTİN

```
SABAH (9:00)
├─ TODO listesine bak
├─ "Bugün ne yapacağım?"
└─ Claude'a sor: "Bugün X özelliğini yapacağım, nereden başlamalıyım?"

ÖĞLE (12:00)
├─ Checkpoint: Çalışıyor mu?
└─ Git commit

AKŞAM (18:00)
├─ Test et
├─ Git commit
├─ Yarına not bırak
└─ LEARNINGS.md güncelle
```

---

## 🚀 BAŞLIYOR!

**Yarın ilk günün:**

1. Docker kur
2. Git repo oluştur
3. Claude'a sor: "Hafta 1 Gün 1'deyim, FastAPI boilerplate ver"

**Başarılar! Sen yaparsın! 💪**
