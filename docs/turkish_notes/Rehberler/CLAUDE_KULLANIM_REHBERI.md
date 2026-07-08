# 🤖 CLAUDE İLE ÇALIŞMA REHBERİ

## 🎯 CLAUDE NEDİR?

Ben senin **AI kod asistanınım**. Bu projede:
- Kod yazıyorum
- Hataları çözüyorum
- Öğretiyorum
- Yol gösteriyorum

**Ama sen projeyi yapıyorsun!** Ben sadece yardımcıyım.

---

## ✅ CLAUDE'A NE ZAMAN SORULMALI?

### 🟢 KESİNLİKLE SOR (Her zaman)

1. **Yeni bir özellik başlarken:**
```
❌ Kötü: "Kod ver"
✅ İyi: "Claude, Hafta 2'deyim. JWT authentication sistemi kuracağım. 
       Nereden başlamalıyım? Hangi kütüphaneleri kullanmalıyım?"
```

2. **Hata aldığında:**
```
❌ Kötü: "Çalışmıyor"
✅ İyi: "Claude, şu komutu çalıştırdım: 'uvicorn app.main:app --reload'
       Şu hatayı aldım: 'ModuleNotFoundError: No module named fastapi'
       Nasıl çözebilirim?"
```

3. **Kod yazarken:**
```
❌ Kötü: "Register endpoint yaz"
✅ İyi: "Claude, FastAPI'de kullanıcı kayıt endpoint'i yazmalıyım.
       - Email ve password alacak
       - Password hash'lenecek (bcrypt)
       - Database'e kaydedecek
       - Token dönecek
       Kod örneği verir misin?"
```

4. **Kod anlamak isterken:**
```
✅ İyi: "Claude, bu kodu satır satır açıklar mısın?
       
       [kod buraya]
       
       Özellikle şu kısmı anlamadım: ..."
```

5. **Best practice öğrenmek isterken:**
```
✅ İyi: "Claude, FastAPI'de config dosyası nerede tutulmalı?
       Environment variables nasıl yönetilir?"
```

---

### 🟡 ÖNCE KENDIN DENE, SONRA SOR

1. **Basit syntax hataları:**
```
Önce Google'a bak: "python list append syntax"
Anlamazsan Claude'a sor
```

2. **Dokümantasyon soruları:**
```
Önce official docs'a bak
Anlamazsan Claude'a sor
```

3. **Basit CSS/styling:**
```
Önce Tailwind docs'a bak
Karışıksa Claude'a sor
```

---

### 🔴 SORMA (Zarar verir)

1. **"Tüm projeyi yaz":**
```
❌ "Claude, tüm backend'i yaz"
→ Hiçbir şey öğrenmezsin!
```

2. **Her küçük şey için:**
```
❌ "Bu satır ne yapıyor?" (her satır için ayrı)
→ Tüm kodu bir seferde açıklat
```

3. **Ödev/kopya için:**
```
❌ "Bitirme raporumu yaz"
→ Raporu sen yazmalısın!
```

---

## 📝 CLAUDE'A NASIL SORU SORULMALI?

### Şablon 1: Yeni Özellik

```
Claude, [HANGİ HAFTADAYIM] ve [NE YAPACAĞIM].

Bana şunlar için yardım et:
1. [İlk adım]
2. [İkinci adım]
3. [Üçüncü adım]

Kullandığım teknolojiler:
- Backend: FastAPI
- Frontend: React
- Database: PostgreSQL

Şu ana kadar yaptıklarım:
- [Önceki adımlar]

Nereden başlamalıyım?
```

**Örnek:**
```
Claude, Hafta 3'teyim ve PDF upload özelliğini yapacağım.

Bana şunlar için yardım et:
1. Backend'de file upload endpoint'i
2. Frontend'de upload componenti
3. Dosya validasyonu (PDF, max 10MB)

Kullandığım teknolojiler:
- Backend: FastAPI
- Frontend: React + Tailwind
- Database: PostgreSQL

Şu ana kadar yaptıklarım:
- Auth sistemi çalışıyor
- Dashboard var (boş)

Nereden başlamalıyım?
```

---

### Şablon 2: Hata Çözme

```
Claude, şu sorunu yaşıyorum:

[NE YAPMAYA ÇALIŞIYORUM]

Çalıştırdığım komut:
```
[komut buraya]
```

Aldığım hata:
```
[tam hata mesajı buraya]
```

Daha önce yaptıklarım:
- [Denediğin şeyler]

Nasıl çözebilirim?
```

**Örnek:**
```
Claude, şu sorunu yaşıyorum:

Backend'i çalıştırmaya çalışıyorum ama hata alıyorum.

Çalıştırdığım komut:
```
uvicorn app.main:app --reload
```

Aldığım hata:
```
ModuleNotFoundError: No module named 'fastapi'
```

Daha önce yaptıklarım:
- pip install fastapi yaptım
- requirements.txt var

Nasıl çözebilirim?
```

---

### Şablon 3: Kod Açıklama

```
Claude, şu kodu anlamıyorum:

```python
[kod buraya]
```

Özellikle şu kısımları açıklar mısın:
1. [Satır/fonksiyon 1]
2. [Satır/fonksiyon 2]

Basit Türkçe ile, adım adım açıklar mısın?
```

---

### Şablon 4: Kod İnceleme

```
Claude, şu kodu yazdım:

```python
[kodun buraya]
```

Şunları kontrol eder misin:
1. Best practice'lere uyuyor mu?
2. Güvenlik açığı var mı?
3. Daha iyi nasıl yazarım?
4. Comment eklemeli miyim?

Önerilerini ver.
```

---

## 🎯 CLAUDE'DAN KOD ALIRKEN

### 1. Kodu Anlayarak Yaz

```
❌ YANLIŞ:
1. Claude'a sor
2. Kodu kopyala
3. Yapıştır
4. Çalıştır
→ Hiçbir şey öğrenmezsin!

✅ DOĞRU:
1. Claude'a sor
2. Kodu OKU
3. Her satırı ANLA
4. Anlamadığın varsa Claude'a tekrar sor
5. Sonra kendin YAZ (kopyala-yapıştır değil!)
6. Test et
```

---

### 2. Adım Adım İlerle

```
❌ YANLIŞ:
"Claude, tüm auth sistemini yaz"
→ 500 satır kod gelir, anlamazsın

✅ DOĞRU:
Adım 1: "Password hashing fonksiyonu yaz"
→ Anla, test et
Adım 2: "Register endpoint yaz"
→ Anla, test et
Adım 3: "Login endpoint yaz"
→ Anla, test et
```

---

### 3. Özelleştir

```
Claude'dan gelen kod "template"dir.
Sen onu kendi projena göre değiştirmelisin!

Örnek:
- Değişken isimleri değiştir
- Error mesajlarını Türkçeleştir
- UI'ı kendi tarzına göre ayarla
```

---

## 💬 CLAUDE İLE DİYALOG ÖRNEKLERİ

### Örnek 1: Yeni Özellik (İyi)

**Sen:**
```
Claude, Hafta 2 Gün 3'teyim. Frontend'de Login sayfası yapacağım.
React + Tailwind kullanıyorum.

Basit bir login formu olsun:
- Email input
- Password input
- Login butonu
- "Kayıt ol" linki

Kod örneği verir misin?
```

**Claude:**
```javascript
// Login.jsx
import { useState } from 'react';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleLogin = async (e) => {
    e.preventDefault();
    // API çağrısı buraya
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      ...
    </div>
  );
}
```

**Sen:**
```
Teşekkürler! Şimdi API çağrısını nasıl yapmalıyım?
```

**Claude:**
```javascript
import axios from 'axios';

const handleLogin = async (e) => {
  e.preventDefault();
  try {
    const response = await axios.post('http://localhost:8000/auth/login', {
      email,
      password
    });
    ...
  }
}
```

---

### Örnek 2: Hata (İyi)

**Sen:**
```
Claude, bu hatayı alıyorum:

npm run dev çalıştırınca:
"Error: Cannot find module 'tailwindcss'"

Ne yapmalıyım?
```

**Claude:**
```
Tailwind CSS kurulu değil. Şunu çalıştır:

npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Sen:**
```
Yaptım, şimdi çalışıyor! Peki tailwind.config.js'i nasıl ayarlamalıyım?
```

**Claude:**
```javascript
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  ...
}
```

---

## 🚫 CLAUDE İLE YANLIŞ KULLANIM ÖRNEKLERİ

### ❌ Örnek 1: Çok Genel

**Kötü:**
```
"Backend yaz"
```

**Sorun:** Ne yapmalıyım? Hangi özellik? Nereden başlayım?

**İyi:**
```
"Claude, FastAPI ile kullanıcı kayıt endpoint'i yazmalıyım.
Email ve password alacak, bcrypt ile hash'leyecek.
Kod örneği ver."
```

---

### ❌ Örnek 2: Hiç Bilgi Yok

**Kötü:**
```
"Hata var, düzelt"
```

**Sorun:** Ne hatası? Hangi kod? Ne yapmaya çalışıyorsun?

**İyi:**
```
"uvicorn app.main:app --reload çalıştırınca
'ModuleNotFoundError: No module named fastapi' hatası alıyorum.
pip install fastapi yaptım ama yine aynı hata.
Ne yapmalıyım?"
```

---

### ❌ Örnek 3: Tüm Projeyi İstemek

**Kötü:**
```
"Tüm SağlıkCebim projesini yaz"
```

**Sorun:** Hiçbir şey öğrenmezsin!

**İyi:**
```
"Bu hafta PDF parsing yapacağım. 
Önce basit bir PDF okuma fonksiyonu yaz.
Sonra regex ile değer çıkarmayı öğretirim."
```

---

## 📚 CLAUDE'DAN NE İSTEYEBİLİRSİN?

### ✅ İsteyebilirsin:

1. **Kod örnekleri**
```
"FastAPI'de JWT token nasıl oluşturulur? Örnek ver."
```

2. **Açıklamalar**
```
"Bu regex pattern'i nasıl çalışıyor? Adım adım açıkla."
```

3. **Hata çözümü**
```
"Bu hatayı nasıl çözerim? [hata mesajı]"
```

4. **Best practices**
```
"React'te state management için en iyi yöntem nedir?"
```

5. **Refactoring**
```
"Bu kodu daha temiz nasıl yazarım? [kod]"
```

6. **Dokümantasyon**
```
"Bu fonksiyon için docstring yaz."
```

---

### ❌ İsteme:

1. **Bitirme raporu yazması**
2. **Tüm projeyi yazması**
3. **Ödevini yapması**
4. **Hiç çaba göstermeden "çözüm"**

---

## 🎓 ÖĞRENME STRATEJİSİ

### 70/30 Kuralı

**Claude yapacak (%70):**
- Boilerplate kod
- Karmaşık logic
- Best practice örnekleri

**Sen yapacaksın (%30):**
- Kodu anlama
- Kendi projene uyarlama
- Test etme
- UI kararları

---

### Her Kod İçin Sor:

1. **Bu ne işe yarıyor?**
2. **Neden böyle yazılmış?**
3. **Farklı nasıl yazılabilir?**
4. **Benim projemde nasıl kullanırım?**

---

## 🔄 CLAUDE İLE ÇALIŞMA DÖNGÜSÜ

```
1. PLAN: "Claude, bugün X yapacağım, nereden başlamalıyım?"
   ↓
2. KOD AL: Claude kod verir
   ↓
3. ANLA: "Claude, bu kodu açıklar mısın?"
   ↓
4. YAZ: Kodu kendin yaz (kopyala-yapıştır değil!)
   ↓
5. TEST: Çalışıyor mu?
   ↓
6a. ÇALIŞIYORSA: Commit at, sonraki adıma geç
6b. ÇALIŞMIYORSA: "Claude, şu hatayı aldım: [hata]"
   ↓
7. ÖĞREN: "Bugün ne öğrendim?" LEARNINGS.md'ye yaz
```

---

## 💡 PRO İPUÇLARI

### 1. Context Ver

```
❌ Kötü: "Login sayfası yap"

✅ İyi: "React + Tailwind ile login sayfası yapacağım.
       Backend'de /auth/login endpoint'i var.
       JWT token dönüyor.
       Token'ı localStorage'a kaydetmem lazım.
       Kod örneği ver."
```

### 2. Aşamalı İlerle

```
Büyük görev → Küçük parçalara böl → Claude'a teker teker sor

Örnek:
"Auth sistemi" →
  1. Password hashing
  2. Register endpoint
  3. Login endpoint
  4. Token verification
  5. Frontend login page
```

### 3. Geribildirim Ver

```
Claude kod verdi →
Sen test ettin →
Çalışmadı →

"Claude, kod çalıştı ama şu sorun var: [sorun]
Nasıl düzeltebilirim?"
```

---

## 🎯 ÖZETpean

**Claude = Kod asistanın**
- Yardım eder
- Öğretir
- Hataları çözer

**Sen = Proje sahibisin**
- Öğrenirsin
- Karar verirsin
- Yaparsın

**Birlikte çalışın = Başarı! 🚀**

---

## 📞 SON TAVSİYELER

1. **Her gün Claude'a danış** (en az 1 kere)
2. **Kod kopyalama, anlayarak yaz**
3. **Anlamadığın her şeyi sor**
4. **Öğrendiklerini not al**
5. **Sabırlı ol, öğrenme zaman alır**

**Sen yaparsın! Claude yardım eder! 💪**
