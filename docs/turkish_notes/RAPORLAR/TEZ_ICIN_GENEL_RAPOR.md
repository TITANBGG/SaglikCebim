# SağlıkCebim Projesi Genel Raporu

**Proje Adı:** SağlıkCebim  
**Kapsam:** Yapay zeka destekli sağlık asistanı ve klinik karar destek sistemi  
**Hazırlanma Amacı:** Tez çalışmasında proje tanıtımı, sistem mimarisi ve teknik yaklaşımın özetlenmesi

---

## 1. Projenin Amacı

SağlıkCebim, sağlık verilerinin tek bir platformda toplanarak analiz edilmesini amaçlayan web tabanlı bir sağlık asistanı ve klinik karar destek sistemi olarak geliştirilmiştir. Proje; kullanıcıların şikayetlerini, laboratuvar sonuçlarını, radyoloji raporlarını ve hasta öyküsünü birlikte değerlendirerek daha anlamlı ve yönlendirici çıktılar üretmeyi hedefler. Bu yaklaşım, hem kullanıcıların sağlık verilerini daha anlaşılır biçimde yorumlamasına yardımcı olmakta hem de yanlış branş seçimi veya gecikmiş yönlendirme gibi sorunları azaltmayı amaçlamaktadır.

Sistemin temel felsefesi, dağınık halde bulunan sağlık bilgilerinin tek bir klinik bağlam altında birleştirilmesidir. Böylece kullanıcı yalnızca ham veri değil, aynı zamanda özetlenmiş, yorumlanmış ve yönlendirici bir sağlık geri bildirimi alabilmektedir.

---

## 2. Sistem Özeti

SağlıkCebim, modern web teknolojileri ile yapay zeka bileşenlerini birleştiren çok katmanlı bir yazılım sistemidir. Uygulama mimarisi genel olarak iki ana bölümden oluşur:

- Backend katmanı: FastAPI tabanlı servisler, iş kuralları, veri doğrulama, analiz ve veritabanı işlemleri
- Frontend katmanı: React ve Vite ile geliştirilmiş kullanıcı arayüzü

Sistem; kullanıcı doğrulama, PDF formatında rapor yükleme, tahlil ayrıştırma, radyoloji analizi, chatbot destekli yönlendirme, bildirim yönetimi ve sağlık geçmişi takibi gibi işlevleri birlikte sunar. Proje, yalnızca veri gösteren bir uygulama değil, aynı zamanda veriyi yorumlayan ve işleyen bir sağlık bilişimi platformu olarak tasarlanmıştır.

---

## 3. Teknik Mimari

### 3.1 Backend Mimarisi

Backend tarafında Python ve FastAPI kullanılmıştır. Bu seçim, yüksek performanslı ve modüler bir API yapısı oluşturmayı mümkün kılmıştır. Backend katmanında aşağıdaki temel bileşenler yer almaktadır:

- FastAPI: REST API servisleri
- SQLAlchemy: ORM ve veri erişim katmanı
- Alembic: veritabanı migration yönetimi
- Pydantic: veri doğrulama ve şema tanımı
- JWT: kimlik doğrulama ve oturum yönetimi
- pdfplumber: PDF raporlarından metin çıkarımı
- Yerel yapay zeka entegrasyonu: kullanıcı mesajlarının ve sağlık bağlamının yorumlanması

Backend servisleri; kullanıcı yönetimi, rapor işleme, laboratuvar analizi, radyoloji verisi işleme, chatbot yönlendirmesi ve sağlık geçmişi bileşenlerini API düzeyinde organize etmektedir.

### 3.2 Frontend Mimarisi

Frontend tarafında React ve Vite kullanılmıştır. Arayüz, kullanıcı dostu ve hızlı etkileşim sağlayacak şekilde yapılandırılmıştır. Kullanıcı giriş ekranları, dashboard, rapor yükleme alanları ve analiz sonuçlarının gösterildiği sayfalar bu katmanda yer alır. Uygulama arayüzü, sağlık verilerinin anlaşılır biçimde sunulmasına odaklanır.

### 3.3 Veritabanı Yapısı

Sistemde ilişkisel bir veritabanı yapısı kullanılmıştır. Kullanıcılar, raporlar, test sonuçları, radyoloji verileri, bildirimler ve hasta profiline ilişkin bilgiler tablolar halinde modellenmiştir. Bu yapı, sağlık verilerinin düzenli biçimde saklanmasına ve geçmiş veriler üzerinde karşılaştırmalı analiz yapılmasına olanak tanır.

---

## 4. Temel Modüller

### 4.1 Kimlik Doğrulama ve Kullanıcı Yönetimi

Sistem, kullanıcı kaydı ve giriş işlemlerini JWT tabanlı kimlik doğrulama ile yönetir. Bu yapı sayesinde kullanıcıya ait sağlık verileri oturum bazlı olarak korunur ve yetkisiz erişim riski azaltılır.

### 4.2 Laboratuvar Sonuçlarının İşlenmesi

Kullanıcıların yüklediği PDF formatındaki laboratuvar sonuçları ayrıştırılarak yapılandırılmış veri haline getirilir. Bu süreçte test isimleri, ölçüm değerleri, birimler ve referans aralıkları tespit edilir. Ardından sonuçlar normal, yüksek veya düşük gibi kategorilere ayrılır. Böylece ham PDF dosyaları yerine yorumlanabilir tahlil çıktıları elde edilir.

### 4.3 Radyoloji Analizi

Radyoloji bileşeni, görüntü raporlarını veya ilişkili metinsel bulguları analiz ederek sağlık bağlamına dahil eder. Bu sayede laboratuvar verileri ile radyolojik bulgular aynı sistem içinde birleştirilir ve daha kapsamlı bir değerlendirme yapılabilir.

### 4.4 Akıllı Triyaj ve Chatbot Yapısı

Sistemde yer alan yapay zeka destekli sohbet bileşeni, kullanıcı mesajlarını sınıflandırarak uygun iş akışına yönlendirir. Niyet tespiti sayesinde mesajın klinik soru, bilgi talebi veya genel sohbet olup olmadığı belirlenebilir. Ardından ilgili departman önerisi veya açıklayıcı geri bildirim üretilir.

### 4.5 Beslenme ve Yaşam Tarzı Yönlendirmeleri

Uygulama yalnızca klinik analiz değil, aynı zamanda beslenme ve yaşam tarzı önerileri de sunar. Kullanıcının sağlık durumu ile ilişkili olarak temel beslenme uyarıları ve destekleyici tavsiyeler üretilebilir.

---

## 5. Veri Akışı

Sistemde veri akışı genel olarak şu adımlarla ilerler:

1. Kullanıcı sisteme giriş yapar.
2. Şikayetini yazar veya sağlık raporu yükler.
3. Backend, gelen veriyi doğrular ve sınıflandırır.
4. PDF, laboratuvar veya radyoloji verileri analiz edilir.
5. Sonuçlar veritabanına kaydedilir.
6. Frontend tarafında özet, grafik veya açıklama olarak kullanıcıya sunulur.

Bu yapı, ham veriden yorumlanmış sağlık çıktısına doğru ilerleyen kontrollü bir işleme hattı oluşturur.

---

## 6. Güvenlik ve Gizlilik Yaklaşımı

Sağlık verileri hassas olduğu için proje tasarımında güvenlik önemli bir kriter olarak ele alınmıştır. Kimlik doğrulama, yetkilendirme ve veri erişim kontrolü sistemin temel güvenlik katmanlarını oluşturur. Ayrıca yerel AI bileşenlerinin kullanılması, harici servislere veri gönderme ihtiyacını azaltarak gizlilik açısından avantaj sağlar. Bu yaklaşım, özellikle sağlık alanında veri mahremiyetini korumaya yönelik uygun bir mimari tercih olarak değerlendirilebilir.

---

## 7. Test ve Doğrulama Süreci

Proje geliştirme sürecinde sistemin yalnızca çalışması değil, güvenli ve tutarlı davranması da hedeflenmiştir. Bu nedenle API uçları, kullanıcı akışları, PDF ayrıştırma mekanizması ve chatbot yanıtları çeşitli test senaryoları ile doğrulanmıştır. Özellikle kritik sağlık senaryolarında sistemin yanlış yönlendirme üretmemesi için senaryo tabanlı kontrol mekanizmaları kullanılmıştır.

---

## 8. Projenin Katkısı

SağlıkCebim projesi, sağlık verilerinin dijital ortamda bir araya getirilmesi ve yapay zeka ile anlamlandırılması konusunda uygulamalı bir örnek sunmaktadır. Proje; tam yığın web geliştirme, veri modeli tasarımı, yapay zeka entegrasyonu, rapor işleme ve klinik karar destek yaklaşımını aynı çatı altında toplar. Bu nedenle hem yazılım mühendisliği hem de sağlık bilişimi açısından öğretici ve uygulanabilir bir çalışma niteliği taşır.

---

## 9. Sonuç

Sonuç olarak SağlıkCebim, sağlık verilerinin toplanması, analiz edilmesi ve kullanıcıya anlaşılır biçimde sunulması için geliştirilmiş bütünleşik bir dijital sağlık platformudur. Proje, laboratuvar sonuçları, radyoloji bulguları ve kullanıcı şikayetlerini birleştirerek klinik karar desteği sağlamayı amaçlar. Kullanılan teknolojiler, sistem mimarisi ve veri işleme yaklaşımı dikkate alındığında SağlıkCebim, tez çalışmasında teknik ve kavramsal olarak güçlü bir örnek olarak sunulabilir.

---

## 10. Kısa Özet

SağlıkCebim;

- sağlık verilerini tek platformda birleştiren,
- laboratuvar ve radyoloji sonuçlarını yorumlayan,
- yapay zeka destekli yönlendirme sunan,
- güvenlik ve gizliliği merkeze alan,
- modern web teknolojileriyle geliştirilmiş

bir sağlık asistanı ve klinik karar destek sistemi olarak tasarlanmıştır.
