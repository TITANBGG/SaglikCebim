# 📊 SaglikCebim Plan Duzenlemeleri - 31 Mart 2026

**Tarih:** 31 Mart 2026
**Durum:** Faz 0 implementasyon basladi
**Odak:** Stabilizasyon, bug kapatma, entegrasyon onceliklendirmesi

---

## 1) Amac ve Kapsam

Bu rapor, onceki yol haritasi metnindeki tekrarli/eskimis maddeleri temizleyip kod tabaniyla dogrulanmis bir uygulama sirasi tanimlar. Hedef, Faz 0 tamamlanmadan Faz 1-2'ye gecisi engellemektir.

---

## 2) Kod Tabanina Gore Dogrulanan Durum

### Dogru olanlar

1. Pre-radyoloji formunda API cagri kirigi bulundu.
2. Anamnez profil duzenleme yonlendirmesinde route parametre tutarsizligi bulundu.
3. Backend `main.py` icinde cift `/health` endpoint tanimi bulundu.

### Guncel kodda artik gecersiz olan iddialar

1. Radyoloji route kapali iddiasi guncel kodda gecerli degil.
2. Anamnez cift-prefix iddiasi guncel kodda gecerli degil.
3. Vite anamnez proxy eksik iddiasi guncel kodda gecerli degil.

---

## 3) Bugun Baslatilan Implementasyon (Faz 0 / Tur 1)

### Tamamlananlar

1. **PreRadiologyForm API cagrisi duzeltildi**
   - `apiCall(...)` yerine ortak istemci `api.post(...)` kullanildi.
   - Snapshot id cevabi `response.data.snapshot_id` olarak alinacak sekilde normalize edildi.

2. **AnamnesisProfile edit route duzeltildi**
   - `"/anamnesis/edit"` yerine parametreli route kullanildi:
   - `"/anamnesis/edit/profile/0"`

3. **Backend health endpoint tekillestirildi**
   - Cift tanim kaldirildi, tek `/health` endpoint birakildi.

### Beklenen etkiler

1. Pre-radyoloji semptom snapshot kaydi artik runtime'da patlamadan calisir.
2. Profil duzenleme/olusturma tuslari route mismatch sebebiyle bos sayfaya dusmez.
3. Monitoring ve health-check davranisi tutarli hale gelir.

---

## 4) Faz 0 Kalan Isler (Oncelikli Sira)

1. **Radyoloji sayfasi smoke testi**
   - Upload -> Analyze -> Findings -> Report zinciri
   - 200/401/500 hata formatlari UI'da adim bazli gosterim

2. **Anamnez ekranlari smoke testi**
   - Profile, conditions, medications, allergies, family-history CRUD
   - Edit ekranlarinin tum tiplerde route uyumu

3. **Port ve process standardizasyonu**
   - Backend 8000
   - Frontend 5173
   - Tek backend prosesi, tek frontend prosesi

4. **Lint kapisi**
   - `npm run lint` kritik hatalarin sifirlanmasi

5. **Hata mesaji standardizasyonu**
   - Backend `detail` yapisinin tum endpointlerde benzerlenmesi
   - Frontend parse fonksiyonunun tek merkezde toplanmasi

---

## 5) Faz 1'e Gecis Kriterleri

Faz 1'e gecis icin asagidaki kosullar ayni anda saglanmali:

1. Frontend route'lari kiriksiz aciliyor.
2. Auth + anamnez + radyoloji ana akislari 200/4xx beklenen sekilde calisiyor.
3. Upload/Analyze/Findings zinciri en az 3 farkli test senaryosunda geciyor.
4. Lint kritik seviye hata vermiyor.

---

## 6) Faz 1 Ozet Plan (Entegrasyon)

1. Hasta bazli ozet endpoint:
   - `GET /patient/summary/basic`

2. Modaliteler arasi baglam birlestirme:
   - Anamnez + lab + radyoloji varlik bayraklari

3. Frontend akis kontrolu:
   - Eksik modaliteye gore rehberli yonlendirme

---

## 7) Faz 2 Ozet Plan (Klinik Deger)

1. Rule-based korelasyon motoru
2. Adaptif anamnez soru uretimi
3. Birlesik risk skoru ve aciklanabilirlik katmani

---

## 8) Riskler ve Onlemler

1. **Coklu terminal/proses riski**
   - Onlem: Baslangic scriptleri tek oturum standardina cekilmeli.

2. **Model/threshold karisimi riski**
   - Onlem: Model dosyasi + threshold dosyasi startup logunda birlikte yazdirilmali.

3. **UI'da genel hata metni riski**
   - Onlem: Adim bazli hata kodu + backend detail zorunlu gosterim.

---

## 9) Sonuc

31.03.2026 itibariyla plan revizyonu uygulamaya alinmistir. Faz 0 icin ilk uc kritik bug kapatildi. Sonraki adim, smoke test ve lint kapisini gecerek Faz 1 entegrasyonuna gecmektir.

---

**Durum:** ✅ In Progress (Faz 0 / Tur 1 tamamlandi)
