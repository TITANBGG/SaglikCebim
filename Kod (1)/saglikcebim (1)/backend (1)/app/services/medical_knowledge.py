"""Tıbbi bilgi tabanı — test açıklamaları ve kişisel soru yanıtları."""

MEDICAL_KNOWLEDGE: dict[str, dict] = {
    "trombosit": {
        "name": "Trombosit (Platelet - PLT)",
        "description": "Trombositler, kanın pıhtılaşmasında görev alan küçük hücre parçacıklarıdır. Kemik iliğinde üretilirler ve yaralanma durumunda kanamayı durdurmak için bir araya gelerek pıhtı oluştururlar.",
        "normal_range": "150.000 - 400.000 /µL",
        "high_meaning": "Trombositoz (yükseklik); enfeksiyon, demir eksikliği, inflamasyon, ameliyat sonrası veya nadiren kemik iliği hastalıkları ile ilişkili olabilir.",
        "low_meaning": "Trombositopeni (düşüklük); viral enfeksiyonlar, bazı ilaçlar, otoimmün hastalıklar, karaciğer hastalığı veya kemik iliği sorunları ile ilişkili olabilir.",
        "tips": "Trombosit değeri çok düşükse morarma ve kanama riski artar. Çok yüksekse pıhtılaşma riski artabilir. Her iki durumda da doktor değerlendirmesi önemlidir.",
    },
    "hemoglobin": {
        "name": "Hemoglobin (Hgb/Hb)",
        "description": "Hemoglobin, kırmızı kan hücrelerinde bulunan ve akciğerlerden dokulara oksijen taşıyan bir proteindir. Demir içerir ve kana kırmızı rengini verir.",
        "normal_range": "Erkek: 13.5-17.5 g/dL | Kadın: 12.0-16.0 g/dL",
        "high_meaning": "Polisitemi, dehidratasyon, yüksek rakımda yaşam, kronik akciğer hastalığı veya sigara kullanımı ile ilişkili olabilir.",
        "low_meaning": "Anemi (kansızlık); demir eksikliği, B12/folat eksikliği, kronik hastalık, kanama veya kemik iliği sorunları ile ilişkili olabilir.",
        "tips": "Düşük hemoglobin halsizlik, solgunluk ve nefes darlığına neden olabilir. Demir, B12 ve folat açısından zengin beslenme önemlidir.",
    },
    "glukoz": {
        "name": "Açlık Kan Şekeri (Glukoz)",
        "description": "Glukoz, vücudun temel enerji kaynağıdır. Kan şekeri düzeyi, pankreastan salgılanan insülin hormonuyla düzenlenir. Açlık kan şekeri en az 8 saat aç karnına ölçülür.",
        "normal_range": "70-100 mg/dL (açlık)",
        "high_meaning": "Prediyabet (100-125 mg/dL) veya diyabet (≥126 mg/dL) ile ilişkili olabilir. Stres, enfeksiyon ve bazı ilaçlar da geçici yüksekliğe neden olabilir.",
        "low_meaning": "Hipoglisemi; aşırı açlık, insülin fazlalığı, karaciğer hastalığı veya bazı ilaçlar ile ilişkili olabilir. Terleme, titreme ve baş dönmesi yapabilir.",
        "tips": "Lifli gıdalar, tam tahıllar ve düzenli öğünler kan şekerini dengede tutar. Şekerli içecek ve işlenmiş gıdalardan kaçının.",
    },
    "kolesterol": {
        "name": "Total Kolesterol",
        "description": "Kolesterol, hücre zarlarının yapımında ve hormon üretiminde kullanılan yağımsı bir maddedir. Karaciğer tarafından üretilir ve besinlerle de alınır.",
        "normal_range": "< 200 mg/dL (istenen)",
        "high_meaning": "Kardiyovasküler hastalık riski artar. Genetik yatkınlık, doymuş yağ ağırlıklı beslenme, obezite ve hareketsizlik başlıca nedenlerdir.",
        "low_meaning": "Çok düşük kolesterol nadir görülür; malnütrisyon, hipertiroidizm veya karaciğer hastalığı ile ilişkili olabilir.",
        "tips": "Zeytinyağı, balık, yulaf ve kuruyemiş faydalıdır. Trans yağ, kızartma ve işlenmiş etlerden kaçının.",
    },
    "ldl": {
        "name": "LDL Kolesterol (Kötü Kolesterol)",
        "description": "LDL (Low-Density Lipoprotein), kolesterolü damar duvarlarına taşıyarak plak oluşumuna yol açabilir. 'Kötü kolesterol' olarak bilinir.",
        "normal_range": "< 130 mg/dL (istenen) | < 100 mg/dL (riskli hasta)",
        "high_meaning": "Ateroskleroz, kalp krizi ve inme riskini artırır.",
        "low_meaning": "Genellikle sorun oluşturmaz.",
        "tips": "Akdeniz tipi beslenme, düzenli egzersiz ve gerekirse statin tedavisi LDL'yi düşürebilir.",
    },
    "hdl": {
        "name": "HDL Kolesterol (İyi Kolesterol)",
        "description": "HDL (High-Density Lipoprotein), damar duvarlarından kolesterolü toplayıp karaciğere geri taşır. 'İyi kolesterol' olarak bilinir ve koruyucu etkisi vardır.",
        "normal_range": "Erkek: > 40 mg/dL | Kadın: > 50 mg/dL",
        "high_meaning": "Genellikle koruyucudur ve olumlu kabul edilir.",
        "low_meaning": "Kardiyovasküler risk artar. Hareketsizlik, obezite ve sigara HDL'yi düşürür.",
        "tips": "Düzenli egzersiz, zeytinyağı ve omega-3 HDL'yi yükseltir.",
    },
    "trigliserid": {
        "name": "Trigliserid (TG)",
        "description": "Trigliseridler, kanda bulunan bir yağ türüdür. Yediğiniz fazla kaloriler trigliseride dönüştürülüp yağ hücrelerinde depolanır.",
        "normal_range": "< 150 mg/dL (açlık)",
        "high_meaning": "Kalp hastalığı riski artar. Şekerli beslenme, alkol, obezite ve genetik yatkınlık başlıca nedenlerdir.",
        "low_meaning": "Genellikle sorun oluşturmaz.",
        "tips": "Balık, sebze, tam tahıllar tüketin. Şekerli içecek ve alkolü sınırlayın.",
    },
    "tsh": {
        "name": "TSH (Tiroid Uyarıcı Hormon)",
        "description": "TSH, hipofiz bezinden salgılanır ve tiroid bezini uyararak T3/T4 hormonlarının üretimini düzenler. Tiroid fonksiyonunun en önemli tarama testidir.",
        "normal_range": "0.4-4.0 mIU/L",
        "high_meaning": "Hipotiroidizm (tiroid yavaşlaması); yorgunluk, kilo alımı, üşüme, kabızlık gibi belirtiler olabilir.",
        "low_meaning": "Hipertiroidizm (tiroid hızlanması); kilo kaybı, çarpıntı, terleme, sinirlilik gibi belirtiler olabilir.",
        "tips": "TSH anormalliğinde serbest T3 ve T4 ile birlikte değerlendirme yapılmalıdır.",
    },
    "ferritin": {
        "name": "Ferritin",
        "description": "Ferritin, vücuttaki demir depolarını gösteren bir proteindir. Demir eksikliği anemisinin en erken belirtecidir.",
        "normal_range": "Erkek: 20-250 ng/mL | Kadın: 10-120 ng/mL",
        "high_meaning": "İnflamasyon, karaciğer hastalığı, hemokromatozis veya demir yüklenmesi ile ilişkili olabilir.",
        "low_meaning": "Demir eksikliği; yetersiz beslenme, kanama veya emilim bozuklukları ile ilişkili olabilir.",
        "tips": "Düşük ferritinde kırmızı et, koyu yeşil yapraklılar ve C vitamini ile birlikte tüketim önerilir.",
    },
    "demir": {
        "name": "Serum Demir",
        "description": "Serum demiri, kanda dolaşan demir miktarını gösterir. Hemoglobin üretimi ve oksijen taşınması için gereklidir.",
        "normal_range": "60-170 µg/dL",
        "high_meaning": "Hemokromatozis, tekrarlayan kan transfüzyonu veya aşırı demir takviyesi ile ilişkili olabilir.",
        "low_meaning": "Demir eksikliği anemisi, yetersiz beslenme, kronik kanama ile ilişkili olabilir.",
        "tips": "Demir emilimini artırmak için C vitamini ile birlikte tüketin. Çay ve kahve emilimi azaltabilir.",
    },
    "wbc": {
        "name": "WBC (Beyaz Kan Hücresi / Lökosit)",
        "description": "Beyaz kan hücreleri, bağışıklık sisteminin temel savunma hücreleridir. Enfeksiyon, inflamasyon ve bağışıklık yanıtlarında görev alırlar.",
        "normal_range": "4.000 - 11.000 /µL",
        "high_meaning": "Lökositoz; enfeksiyon, stres, inflamasyon, alerji veya nadiren lösemi ile ilişkili olabilir.",
        "low_meaning": "Lökopeni; viral enfeksiyonlar, bazı ilaçlar, otoimmün hastalıklar veya kemik iliği sorunları ile ilişkili olabilir.",
        "tips": "Yüksek WBC'de enfeksiyon belirtileri (ateş, kırgınlık) varsa doktora başvurun.",
    },
    "crp": {
        "name": "CRP (C-Reaktif Protein)",
        "description": "CRP, karaciğer tarafından üretilen ve vücutta inflamasyon/enfeksiyon olduğunda yükselen bir akut faz proteinidir.",
        "normal_range": "< 5 mg/L (veya < 0.5 mg/dL)",
        "high_meaning": "Enfeksiyon, otoimmün hastalık, travma veya kronik inflamasyon ile ilişkili olabilir. Kardiyovasküler risk göstergesi olarak da kullanılır.",
        "low_meaning": "Genellikle klinik anlam taşımaz.",
        "tips": "Yüksek CRP ile birlikte ateş veya şiddetli ağrı varsa acil değerlendirme gerekebilir.",
    },
    "alt": {
        "name": "ALT (Alanin Aminotransferaz / SGPT)",
        "description": "ALT, ağırlıklı olarak karaciğerde bulunan bir enzimdir. Karaciğer hücrelerinde hasar olduğunda kana geçer ve yükselir.",
        "normal_range": "7-56 U/L",
        "high_meaning": "Hepatit, yağlı karaciğer, ilaç toksisitesi, alkol hasarı veya karaciğer sirozu ile ilişkili olabilir.",
        "low_meaning": "Genellikle klinik anlam taşımaz.",
        "tips": "ALT yüksekliğinde alkol, gereksiz ilaç ve takviyelerden kaçının. AST ve GGT ile birlikte değerlendirin.",
    },
    "ast": {
        "name": "AST (Aspartat Aminotransferaz / SGOT)",
        "description": "AST, karaciğer, kalp ve kaslarda bulunan bir enzimdir. Karaciğer hasarı dışında yoğun egzersiz sonrası da yükselebilir.",
        "normal_range": "10-40 U/L",
        "high_meaning": "Karaciğer hastalığı, kalp krizi, kas hasarı veya yoğun egzersiz sonrası yükselebilir.",
        "low_meaning": "Genellikle klinik anlam taşımaz.",
        "tips": "AST/ALT oranı karaciğer hastalığının tipini belirlemeye yardımcı olabilir.",
    },
    "kreatinin": {
        "name": "Kreatinin",
        "description": "Kreatinin, kas metabolizmasının bir yan ürünüdür ve böbrekler tarafından atılır. Böbrek fonksiyonunun en temel göstergelerinden biridir.",
        "normal_range": "Erkek: 0.7-1.3 mg/dL | Kadın: 0.6-1.1 mg/dL",
        "high_meaning": "Böbrek yetmezliği, dehidratasyon, aşırı protein tüketimi veya kas hasarı ile ilişkili olabilir.",
        "low_meaning": "Düşük kas kütlesi, malnütrisyon veya karaciğer hastalığı ile ilişkili olabilir.",
        "tips": "Yüksek kreatininde bol su için ve ağrı kesici kullanımına dikkat edin. eGFR ile birlikte değerlendirin.",
    },
    "üre": {
        "name": "Üre (BUN)",
        "description": "Üre, proteinlerin yıkımı sonucu karaciğerde oluşur ve böbrekler tarafından atılır. Böbrek fonksiyonunu değerlendirmekte kullanılır.",
        "normal_range": "17-43 mg/dL",
        "high_meaning": "Böbrek hastalığı, dehidratasyon, yüksek proteinli diyet, gastrointestinal kanama ile ilişkili olabilir.",
        "low_meaning": "Karaciğer hastalığı veya düşük proteinli diyet ile ilişkili olabilir.",
        "tips": "Kreatinin ile birlikte değerlendirilmelidir.",
    },
    "bilirubin": {
        "name": "Bilirubin (Total/Direkt)",
        "description": "Bilirubin, kırmızı kan hücrelerinin yıkılması sonucu oluşan sarı-turuncu renkli bir pigmenttir. Karaciğer tarafından işlenir ve safra ile atılır.",
        "normal_range": "Total: 0.1-1.2 mg/dL | Direkt: 0-0.3 mg/dL",
        "high_meaning": "Sarılık (ikter); karaciğer hastalığı, safra yolu tıkanıklığı veya aşırı kırmızı kan hücresi yıkımı (hemoliz) ile ilişkili olabilir.",
        "low_meaning": "Genellikle klinik anlam taşımaz.",
        "tips": "Gözlerde veya deride sararma varsa acil değerlendirme gerekir.",
    },
    "hba1c": {
        "name": "HbA1c (Glikozile Hemoglobin)",
        "description": "HbA1c, son 2-3 aydaki ortalama kan şekeri düzeyini gösteren bir testtir. Diyabet tanı ve takibinde kullanılır.",
        "normal_range": "< %5.7 (normal) | %5.7-6.4 (prediyabet) | ≥ %6.5 (diyabet)",
        "high_meaning": "Diyabet veya prediyabet. Uzun süreli kan şekeri kontrolünün yetersiz olduğunu gösterir.",
        "low_meaning": "Hipoglisemi eğilimi, anemi veya kan kaybı durumlarında düşük çıkabilir.",
        "tips": "Düzenli egzersiz, dengeli beslenme ve karbonhidrat kontrolü HbA1c'yi düşürmeye yardımcı olur.",
    },
    "b12": {
        "name": "Vitamin B12 (Kobalamin)",
        "description": "B12 vitamini, sinir sistemi fonksiyonu ve kırmızı kan hücresi üretimi için gereklidir. Hayvansal gıdalardan alınır.",
        "normal_range": "200-900 pg/mL",
        "high_meaning": "Genellikle sorun oluşturmaz. Nadiren karaciğer hastalığı ile ilişkili olabilir.",
        "low_meaning": "Megaloblastik anemi, nöropati (uyuşma, karıncalanma), unutkanlık ve halsizlik ile ilişkili olabilir.",
        "tips": "Et, balık, yumurta ve süt ürünleri B12 kaynaklarıdır. Vejetaryenlerde takviye önerilir.",
    },
    "folat": {
        "name": "Folat (Folik Asit / B9)",
        "description": "Folat, DNA sentezi ve hücre bölünmesi için gerekli bir B vitaminidir. Gebelikte nöral tüp defektlerini önlemek için çok önemlidir.",
        "normal_range": "3-17 ng/mL",
        "high_meaning": "Genellikle sorun oluşturmaz.",
        "low_meaning": "Megaloblastik anemi, yetersiz beslenme veya emilim bozukluğu ile ilişkili olabilir.",
        "tips": "Yeşil yapraklı sebzeler, baklagiller ve turunçgiller folat açısından zengindir.",
    },
    "vitamin d": {
        "name": "25-OH Vitamin D",
        "description": "D vitamini, kemik sağlığı, bağışıklık sistemi ve kas fonksiyonu için gereklidir. Güneş ışığıyla deride sentezlenir.",
        "normal_range": "30-100 ng/mL (yeterli) | 20-29 (yetersiz) | < 20 (eksik)",
        "high_meaning": "Aşırı takviye kullanımı sonucu toksik düzeylere ulaşabilir (> 100 ng/mL). Hiperkalsemi riski.",
        "low_meaning": "Kemik erimesi (osteoporoz), kas güçsüzlüğü, bağışıklık zayıflığı ve depresyon ile ilişkili olabilir.",
        "tips": "Günde 15-20 dk güneşlenme ve gerekirse 1000-2000 IU D vitamini takviyesi önerilir.",
    },
    "eritrosit": {
        "name": "Eritrosit (RBC - Kırmızı Kan Hücresi)",
        "description": "Eritrositler, oksijeni akciğerlerden tüm vücuda taşıyan kırmızı kan hücreleridir. Kemik iliğinde üretilirler.",
        "normal_range": "Erkek: 4.5-5.5 milyon/µL | Kadın: 4.0-5.0 milyon/µL",
        "high_meaning": "Polisitemi, dehidratasyon veya kronik hipoksi ile ilişkili olabilir.",
        "low_meaning": "Anemi, kanama veya kemik iliği sorunları ile ilişkili olabilir.",
        "tips": "Hemoglobin ve hematokrit ile birlikte değerlendirilmelidir.",
    },
    "hematokrit": {
        "name": "Hematokrit (Hct)",
        "description": "Hematokrit, kanın yüzde kaçının kırmızı kan hücrelerinden oluştuğunu gösteren bir ölçümdür.",
        "normal_range": "Erkek: %40-54 | Kadın: %36-48",
        "high_meaning": "Dehidratasyon, polisitemi veya kronik akciğer hastalığı ile ilişkili olabilir.",
        "low_meaning": "Anemi, kanama veya sıvı yüklenmesi ile ilişkili olabilir.",
        "tips": "Hemoglobin ile paralel değerlendirilir.",
    },
    "mcv": {
        "name": "MCV (Ortalama Eritrosit Hacmi)",
        "description": "MCV, kırmızı kan hücrelerinin ortalama büyüklüğünü gösterir. Anemi tipini belirlemede önemlidir.",
        "normal_range": "80-100 fL",
        "high_meaning": "Makrositer anemi; B12 veya folat eksikliği, karaciğer hastalığı ile ilişkili olabilir.",
        "low_meaning": "Mikrositer anemi; demir eksikliği veya talasemi ile ilişkili olabilir.",
        "tips": "Anemi araştırmasında ilk bakılan parametrelerden biridir.",
    },
    "sedimantasyon": {
        "name": "Sedimantasyon (ESR)",
        "description": "Sedimantasyon, kırmızı kan hücrelerinin belirli sürede çökme hızını ölçer. İnflamasyon belirtecidir.",
        "normal_range": "Erkek: 0-15 mm/saat | Kadın: 0-20 mm/saat",
        "high_meaning": "Enfeksiyon, otoimmün hastalık, kanser veya kronik inflamasyon ile ilişkili olabilir.",
        "low_meaning": "Genellikle klinik anlam taşımaz.",
        "tips": "Nonspesifik bir testtir; CRP ve klinik bulgularla birlikte değerlendirilmelidir.",
    },
}

# Ek alias → knowledge key eşleştirmesi
KNOWLEDGE_ALIASES: dict[str, str] = {
    "plt": "trombosit", "platelet": "trombosit", "kan pulcuğu": "trombosit",
    "hgb": "hemoglobin", "hb": "hemoglobin",
    "şeker": "glukoz", "kan şekeri": "glukoz", "blood sugar": "glukoz", "glucose": "glukoz",
    "chol": "kolesterol", "cholesterol": "kolesterol", "total kolesterol": "kolesterol",
    "kötü kolesterol": "ldl", "iyi kolesterol": "hdl",
    "tg": "trigliserid", "triglyceride": "trigliserid",
    "tiroid": "tsh", "thyroid": "tsh",
    "iron": "demir", "serum demiri": "demir",
    "lökosit": "wbc", "beyaz küre": "wbc", "leukocyte": "wbc", "akyuvar": "wbc",
    "sgpt": "alt", "sgot": "ast",
    "karaciğer enzimi": "alt", "böbrek": "kreatinin",
    "bun": "üre", "urea": "üre",
    "kobalamin": "b12", "folik asit": "folat", "folic acid": "folat",
    "d vitamini": "vitamin d", "d3": "vitamin d",
    "rbc": "eritrosit", "kırmızı küre": "eritrosit", "alyuvar": "eritrosit",
    "hct": "hematokrit",
    "esr": "sedimantasyon", "sedim": "sedimantasyon",
    "glikozile hemoglobin": "hba1c", "a1c": "hba1c",
}


def find_knowledge(query: str) -> dict | None:
    """Mesajdan test adı bul ve bilgi tabanından açıklama döndür."""
    q = query.lower().strip()
    # Direkt anahtar eşleşmesi
    for key in MEDICAL_KNOWLEDGE:
        if key in q:
            return MEDICAL_KNOWLEDGE[key]
    # Alias eşleşmesi
    for alias, key in KNOWLEDGE_ALIASES.items():
        if alias in q:
            return MEDICAL_KNOWLEDGE.get(key)
    return None


# Kişisel / off-topic soruları tespit
PERSONAL_PATTERNS: list[list[str]] = [
    ["nasılsın", "nasilsin", "naber", "ne haber", "iyi misin"],
    ["kadın mısın", "erkek misin", "cinsiyetin", "kız mısın", "bay mısın", "bayan mısın"],
    ["adın ne", "ismin ne", "sen kimsin", "kim olduğun", "kendini tanıt"],
    ["kaç yaşındasın", "yaşın kaç", "ne zaman doğdun"],
    ["nerelisin", "nereden geliyorsun", "hangi şehir"],
    ["sevgilin var mı", "evli misin", "bekar mısın", "aşk", "flört"],
    ["seni seviyorum", "güzelsin", "tatlısın", "yakışıklısın"],
    ["hava nasıl", "hava durumu", "bugün hava"],
    ["futbol", "basketbol", "maç skoru", "galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor"],
    ["yemek tarifi", "pizza", "hamburger", "pasta tarifi"],
    ["şaka yap", "fıkra anlat", "komik bir şey", "espri"],
    ["şarkı söyle", "müzik öner", "film öner", "dizi öner"],
    ["siyaset", "politika", "seçim", "cumhurbaşkanı", "parti"],
    ["din", "allah", "namaz", "kilise", "ibadet"],
    ["para kazan", "borsa", "kripto", "bitcoin", "dolar kuru"],
    ["ödev yap", "matematik", "fizik", "tarih", "coğrafya"],
]

PERSONAL_RESPONSE = (
    "Ben **SağlıkCebim Sağlık Asistanı**yım 🏥\n\n"
    "Yalnızca **sağlık ve tıbbi konularda** size yardımcı olmak için tasarlandım. "
    "Kan tahlili sonuçlarınızı yorumlama, beslenme önerileri ve bilimsel makaleler konusunda sorularınızı yanıtlayabilirim.\n\n"
    "Sağlıkla ilgili bir sorunuz varsa memnuniyetle yardımcı olurum! 😊"
)


def is_personal_question(message: str) -> bool:
    msg = message.lower().strip()
    for group in PERSONAL_PATTERNS:
        if any(p in msg for p in group):
            return True
    return False
