# 🚀 SağlıkCebim - Gelecek Hedefler

**Hazırlanma Tarihi:** 28 Mart 2026  
**Dayanak Belgeler:**  
- `Klinik Tanı ve Tedavi Algoritmizasyonu İçin Şablon ve Altyapı Raporu.pdf`
- `Tıbbi Yapay Zeka Projesi Altyapı Raporu.pdf`
- 28 Mart 2026 tarihli güncel sistem incelemesi

---

## 🎯 Bu Dokümanın Amacı

Bu doküman, SağlıkCebim’in mevcut laboratuvar odaklı ürün yapısından:

- klinik bilgi tabanı güçlü,
- algoritmalaştırılmış tanı/tedavi mantığı olan,
- hasta takibi yapabilen,
- standartlarla uyumlu,
- denetlenebilir ve genişleyebilir

bir tıbbi yapay zeka platformuna dönüşmesi için hedefleri tanımlar.

Bu planın ana prensibi şudur:

**Önce çalışan çekirdek ürünü stabilize et, sonra klinik bilgi modelini standartlaştır, en son ileri seviye AI ve entegrasyon katmanlarını ekle.**

---

## 📌 Mevcut Durumun Kısa Özeti

### Güçlü alanlar
- Auth akışı çalışıyor
- PDF upload / parse / sonuç üretimi sağlam
- Trend ve monitoring mantığı oluşmuş durumda
- PubMed entegrasyonu ve makale/chat akışı mevcut
- Bilgi tabanı için başlangıç veri dosyaları var
- Backend testleri güçlü bir temel sunuyor

### Zayıf alanlar
- Anamnez modülü full-stack entegrasyon olarak kırık
- Radyoloji modülü entegrasyon seviyesinde tamamlanmamış
- Standart terminoloji katmanı yok
- FHIR / SMART on FHIR / CDS Hooks sınırı henüz yok
- Kural motoru ile AI katmanı ayrışmış değil
- Klinik bilgi nesneleri hastalık bazında standartlaştırılmamış
- Uyum / yönetişim / audit / drift izleme katmanı başlangıç seviyesinde

---

## 🧭 Stratejik Hedefler

## 1. Çekirdek Ürünü Stabil Hale Getirmek

İlk hedef yeni vizyon eklemek değil, mevcut sistemi güvenilir hale getirmektir.

### Bu hedefin çıktıları
- Anamnez route ve frontend entegrasyonu düzelmiş olacak
- Radyoloji modülü teknik olarak açılabilir hale gelecek
- Frontend lint hataları temizlenecek
- Port, baseURL ve proxy mantığı tek standarda inecek
- Çalışan modüller için “production-safe” temel seviye oluşacak

---

## 2. Hastalık Bazlı Klinik Bilgi Şablonu Oluşturmak

İlk PDF’nin önerdiği en değerli şey, her koşul/hastalık için tek biçimli bir bilgi nesnesi üretme fikridir.

### Hedeflenen bilgi nesnesi alanları
- `condition_name_tr`
- `condition_name_en`
- `synonyms`
- `population_scope`
- `care_setting`
- `icd10`
- `snomed_ct`
- epidemiyoloji
- risk faktörleri
- red flags
- tanı kriterleri
- ayırıcı tanı
- laboratuvar / görüntüleme eşikleri
- izlem sıklığı
- tedavi seçenekleri
- ilaç dozları
- kontrendikasyonlar
- hasta eğitimi
- follow-up kuralları
- kanıt düzeyi
- kaynak referansları

### Neden önemli
- Yeni hastalık eklemek yazılım projesi olmaktan çıkar
- Rule engine için tek tip veri sağlanır
- İzlenebilir klinik içerik oluşur
- AI öneri katmanının halüsinasyon riski azalır

---

## 3. Terminoloji ve Kodlama Katmanı Kurmak

Her klinik nesne ileride birlikte çalışabilirlik için standart kod sistemlerine bağlanmalıdır.

### Hedef standartlar
- ICD-10
- SNOMED CT
- LOINC
- UCUM
- Gerekirse ilaç tarafında ATC / RxNorm eşleme

### Beklenen sonuç
- Test, tanı, semptom ve tedavi verileri normalize olur
- FHIR geçişi kolaylaşır
- Klinik karar motoru daha güvenilir çalışır
- Rapordan gelen serbest metin ile klinik kural tabanı arasında köprü kurulur

---

## 4. FHIR Tabanlı Entegrasyon Sınırı Tasarlamak

İkinci PDF’nin ana katkısı, sistemin dış dünya ile nasıl konuşacağını netleştirmesidir.

### Hedeflenen FHIR kaynakları
- `Patient`
- `Condition`
- `Observation`
- `Medication`
- `MedicationRequest`
- `Encounter`
- `DiagnosticReport`
- `CarePlan`
- `ServiceRequest`

### Orta vadeli amaç
- SağlıkCebim kendi iç verisini FHIR benzeri bir kanonik modele taşımalı
- Dış sistem entegrasyonu daha sonra gelse bile içerideki veri modeli buna hazırlanmalı

### Uzun vadeli amaç
- SMART on FHIR ile embeddable klinik uygulama
- CDS Hooks ile bağlama duyarlı karar destek kartları

---

## 5. Rule Engine ve AI Katmanını Ayrıştırmak

Bugünkü sistemde öneri, açıklama ve bilgi sunumu büyük ölçüde aynı katman içinde çalışıyor. Hedef bunları ayrıştırmak.

### Kurulacak mantık
- **Rule Engine:** deterministik kurallar, eşikler, red flag, follow-up
- **ML / AI Layer:** risk skoru, tahmin, sıralama, ilişki keşfi
- **Orchestrator:** rule engine + AI çıktılarını birleştiren karar katmanı

### Prensip
- Kritik klinik uyarılar yalnızca LLM veya serbest metin üretimiyle verilmemeli
- Acil / kontrendikasyon / sevk kararları kural tabanlı olmalı
- AI katmanı destekleyici ve açıklayıcı rolde kalmalı

---

## 6. Dinamik Hasta Takip Sistemi Kurmak

SağlıkCebim’in en büyük sıçrama noktası yalnızca “rapor analiz eden uygulama” olmaktan çıkıp “takip eden sistem” haline gelmesidir.

### Takip bileşenleri
- Zaman serili laboratuvar izleme
- Hastalık bazlı izlem protokolleri
- İlaç ve kontrol hatırlatmaları
- Alarm eşikleri
- Semptom snapshot akışı
- Radyoloji + laboratuvar + anamnez birleşik görünüm

### Hedef sonuç
- Tek seferlik rapor yorumundan sürekli bakım mantığına geçiş
- Kullanıcı için daha yüksek ürün değeri
- Hekim destekli kullanım senaryolarına daha yakın yapı

---

## 7. GraphRAG ve Gelişmiş Klinik Bilgi Katmanı

Bu alan erken değil, ancak doğru zamanda önemli olacaktır.

### GraphRAG ne zaman düşünülmeli
- Klinik bilgi nesneleri oturmuşsa
- Terminoloji katmanı kurulmuşsa
- Kural motoru çalışıyorsa
- Kaynak yönetimi ve referans sistemi standardize edilmişse

### GraphRAG’den beklenenler
- Semptom-test-tanı-tedavi ilişkilerini grafik olarak modellemek
- Kaynaklı açıklamalar üretmek
- PubMed / kılavuz / KB verisini bağlamsal hale getirmek
- “Neden bu öneri verildi?” sorusuna daha güçlü cevap vermek

### Şu anki not
GraphRAG, ilk adım değil; iyi kurulmuş veri modeli ve knowledge graph sonrasında gelmeli.

---

## 🗓️ Faz Bazlı Yol Haritası

## FAZ 0 - Stabilizasyon
**Süre:** 1-2 hafta

### Hedef
Mevcut kırıkları kapatmak ve sistemi tekrar tutarlı hale getirmek

### Yapılacaklar
- Anamnez route prefix düzeltmesi
- Frontend anamnez endpoint standardizasyonu
- Vite proxy güncellemesi
- Radyoloji `RadiologyContextLink` uyumsuzluğunu düzeltme
- `PreRadiologyForm` import düzeltmesi
- `Radiology.jsx` parse hatası temizliği
- Anamnez profile route ve handler temizlikleri
- Lint temizliği

### Faz çıkışı
- Anamnez çalışır
- Radyoloji UI tekrar açılabilir
- Frontend temiz build + temiz lint verir

---

## FAZ 1 - Klinik Bilgi Modeli
**Süre:** 2-4 hafta

### Hedef
Hastalık/koşul bazlı standart şablon veri modelini kurmak

### Yapılacaklar
- `conditions` için JSON schema tasarımı
- Hastalık modülü veri alanlarını netleştirme
- Kaynak referans formatı tanımlama
- Kanıt düzeyi ve guideline versiyon alanı ekleme
- İlk 5-10 hastalık için pilot bilgi nesneleri hazırlama

### Faz çıkışı
- Klinik bilgi tabanı kurumsal hale gelir
- Hastalık ekleme standardı oluşur

---

## FAZ 2 - Terminoloji ve Uyum Katmanı
**Süre:** 3-5 hafta

### Hedef
Klinik nesneleri kod sistemleri ve güvenlik/uyum çerçevesiyle hizalamak

### Yapılacaklar
- ICD-10 / SNOMED / LOINC / UCUM eşleme tablosu
- Veri sözlüğü hazırlama
- Audit log kapsamını genişletme
- KVKK veri sınıflandırması
- Yetki, rol ve veri erişim sınırlarını netleştirme

### Faz çıkışı
- Daha güvenilir veri katmanı
- FHIR geçişine hazır temel model

---

## FAZ 3 - FHIR ve Karar Motoru Hazırlığı
**Süre:** 4-6 hafta

### Hedef
İç veri modeli ile FHIR-benzeri klinik kaynaklar arasında köprü kurmak

### Yapılacaklar
- `Patient`, `Observation`, `Condition`, `DiagnosticReport` iç eşlemeleri
- Kural motoru DSL veya yapılandırılmış kural formatı
- Kritik eşik / red flag / sevk kuralları
- Klinik karar açıklama formatı

### Faz çıkışı
- Rule engine ayrışır
- AI önerileri daha güvenli zemine oturur

---

## FAZ 4 - Dinamik Takip ve Klinik İş Akışı
**Süre:** 4-8 hafta

### Hedef
Sistemi tek seferlik rapor uygulamasından bakım/takip platformuna çevirmek

### Yapılacaklar
- Hastalık bazlı follow-up planları
- Otomatik kontrol zamanları
- İlaç ve laboratuvar izlem kuralları
- Trigger tabanlı bildirimler
- Semptom + lab + radyoloji birleşik karar kartları

### Faz çıkışı
- Sürekli takip sistemi
- Hasta bazlı yol haritası üretimi

---

## FAZ 5 - Gelişmiş AI ve GraphRAG
**Süre:** 6+ hafta

### Hedef
Referanslı, açıklanabilir, düşük halüsinasyon riskli ileri bilgi katmanı kurmak

### Yapılacaklar
- Knowledge graph tasarımı
- Kaynaklı retrieval
- PubMed + guideline + lokal KB birleşimi
- GraphRAG prototipi
- Model değerlendirme / kalibrasyon / drift izleme

### Faz çıkışı
- Daha akıllı ama denetlenebilir karar destek
- Klinik açıklanabilirlikte sıçrama

---

## 🧪 Ölçülebilir Başarı Kriterleri

### Kısa vadeli
- Frontend lint hatası: 0
- Anamnez uçları: çalışan durumda
- Radyoloji uçtan uca akış: çalışan durumda
- Build + test pipeline: temiz

### Orta vadeli
- Standart hastalık şablonu: en az 10 koşul
- Terminoloji eşlemeleri: aktif kullanımda
- Rule engine: en az 3 klinik akışta devrede
- Follow-up protokolü: en az 2 kronik durum için canlı

### Uzun vadeli
- FHIR uyumlu iç veri modeli
- Kaynaklı AI karar desteği
- Klinik takip sistemi
- GraphRAG tabanlı açıklama katmanı

---

## ⛔ Şimdilik Yapılmaması Gerekenler

- Doğrudan tam GraphRAG inşasına atlamak
- FHIR entegrasyonunu veri modeli oturmadan başlatmak
- Kritik klinik kararları yalnızca LLM yanıtına bırakmak
- Hastalık şablonu oluşmadan çok sayıda koşul eklemek
- Uyum / audit / veri yönetişimini sona bırakmak

---

## ✅ Öncelik Kararı

Bu proje için doğru sıra:

1. **Mevcut sistemi düzelt**
2. **Klinik bilgi modelini kur**
3. **Terminoloji ve standart katmanını ekle**
4. **Kural motorunu ayır**
5. **Takip sistemini inşa et**
6. **En son GraphRAG ve ileri AI katmanına geç**

---

## 📝 Son Söz

Bu iki PDF birlikte okunduğunda ortaya net bir yön çıkıyor:

SağlıkCebim’in geleceği, yalnızca daha fazla özellik eklemek değil; klinik bilgiyi standartlaştırılmış veri, hesaplanabilir kural, güvenli entegrasyon ve izlenebilir AI katmanına dönüştürmektir.

Bu doküman, o dönüşüm için başlangıç yol haritasıdır.
