"""
SağlıkCebim — Altın Standart Klinik Senaryolar

Kullanım alanları:
  1. LLM prompt'una few-shot örnek olarak eklenir (çıktı kalitesini artırır)
  2. Regresyon test senaryoları
  3. Sistem davranışının belgelenmesi

Her senaryo:
  - input_context : Hastanın klinik bağlamı (anamnez + lab + radyoloji)
  - user_message  : Kullanıcı mesajı
  - expected      : Sistemin üretmesi gereken cevabın kriterleri
"""

from __future__ import annotations

GOLDEN_SCENARIOS: list[dict] = [

    # ──────────────────────────────────────────────────────────────────────────
    # S1 — Hipertansiyonlu hastada başağrısı
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S1",
        "title": "Hipertansiyonlu hastada başağrısı",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Hipertansiyon\nMevcut İlaçlar: Parasetamol 500mg\nAlerjiler: Yok",
            "lab_anomalies": "Anormal kan tahlili bulgusu yok.",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "3 gündür şiddetli başım ağrıyor, ensem tutuldu gibi hissediyorum",
        "expected": {
            "risk_level": ["high", "medium"],
            "differential_diagnosis_conditions": [
                "Hipertansif Başağrısı",
                "Gerilim Tipi Başağrısı",
            ],
            "recommended_departments_contains": ["Kardiyoloji", "Nöroloji"],
            "tests_to_discuss_contains": ["kan basıncı", "EKG"],
            "immediate_action_not_empty": True,
            "lifestyle_modifications_not_empty": True,
        },
        "should_not_contain": [
            "reçete",
            "mg/gün",
            "antibiyotik",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S2 — Yorgunluk + nefes darlığı (anemi şüphesi)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S2",
        "title": "Yorgunluk ve nefes darlığı",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Yok\nMevcut İlaçlar: Yok\nAlerjiler: Yok",
            "lab_anomalies": "Hemoglobin: 9.2 g/dL [Düşük], MCV: 71 fL [Düşük], Ferritin: 4 ng/mL [Düşük]",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "Son zamanlarda çok çabuk yoruluyorum, merdiven çıkınca nefesim kesiliyor",
        "expected": {
            "risk_level": ["medium", "high"],
            "differential_diagnosis_conditions": [
                "Demir Eksikliği Anemisi",
                "B12 Vitamini Eksikliği",
            ],
            "recommended_departments_contains": ["Dahiliye", "Hematoloji"],
            "tests_to_discuss_contains": ["ferritin", "B12", "tam kan"],
            "lifestyle_modifications_not_empty": True,
        },
        "should_not_contain": ["ilaç yaz", "reçete"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S3 — Ani göğüs ağrısı (ACİL)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S3",
        "title": "Ani göğüs ağrısı — ACİL",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Hipertansiyon, Diyabet Tip 2\nMevcut İlaçlar: Metformin\nAlerjiler: Yok",
            "lab_anomalies": "Anormal kan tahlili bulgusu yok.",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "Ani göğüs ağrım başladı, sol koluma vuruyor, terliyorum",
        "expected": {
            "risk_level": ["critical"],
            "immediate_action_contains_any": ["112", "acil servis", "ambulans"],
            "recommended_departments_contains": ["Acil Servis"],
            "do_not_do_not_empty": True,
        },
        "should_not_contain": ["bekleyebilirsiniz", "birkaç gün izleyin"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S4 — TSH yüksek (hipotiroidizm)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S4",
        "title": "Yüksek TSH — hipotiroidizm şüphesi",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Yok\nMevcut İlaçlar: Yok\nAlerjiler: Yok",
            "lab_anomalies": "TSH: 8.4 mIU/L [Yüksek], Serbest T4: 0.7 ng/dL [Düşük]",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "TSH değerim 8.4 çıktı, ne anlama geliyor, ne yapmalıyım",
        "expected": {
            "risk_level": ["medium"],
            "differential_diagnosis_conditions": ["Hipotiroidizm", "Hashimoto"],
            "recommended_departments_contains": ["Endokrinoloji"],
            "tests_to_discuss_contains": ["Anti-TPO", "Anti-TG", "Tiroid USG"],
            "lifestyle_modifications_not_empty": True,
        },
        "should_not_contain": ["reçete", "ilaç başla"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S5 — Karın ağrısı + ishal
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S5",
        "title": "Karın ağrısı ve ishal",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Yok\nMevcut İlaçlar: Yok\nAlerjiler: Penisilin",
            "lab_anomalies": "CRP: 18 mg/L [Yüksek], WBC: 11.2 K/uL [Yüksek]",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "3 gündür karın ağrım var, günde 4-5 kez ishalim oluyor, hafif ateşim de var",
        "expected": {
            "risk_level": ["medium", "high"],
            "differential_diagnosis_conditions": [
                "Akut Gastroenterit",
                "Enflamatuvar Bağırsak Hastalığı",
            ],
            "recommended_departments_contains": ["Gastroenteroloji", "Dahiliye"],
            "tests_to_discuss_contains": ["dışkı", "USG", "kolonoskopi"],
            "do_not_do_not_empty": True,
        },
        "should_not_contain": ["antibiyotik başla", "reçete"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S6 — Göğüs röntgeninde radyoloji bulgusu
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S6",
        "title": "Röntgende konsolidasyon bulgusu",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Astım\nMevcut İlaçlar: Salbutamol inhaler\nAlerjiler: Yok",
            "lab_anomalies": "CRP: 42 mg/L [Yüksek], WBC: 13.8 K/uL [Yüksek]",
            "radiology_findings": "Sol alt lobda konsolidasyon (güven: %82, Orta şiddet). Plevral efüzyon şüphesi.",
        },
        "user_message": "Göğsümde ağrı var, öksürüyorum ve ateşim 38.5",
        "expected": {
            "risk_level": ["high", "medium"],
            "differential_diagnosis_conditions": ["Pnömoni", "Plevral Efüzyon"],
            "recommended_departments_contains": ["Göğüs Hastalıkları", "Enfeksiyon Hastalıkları"],
            "tests_to_discuss_contains": ["balgam kültürü", "PA akciğer", "BT"],
            "immediate_action_not_empty": True,
        },
        "should_not_contain": ["antibiyotik yaz", "reçete", "evde tedavi"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # S7 — Sohbet / klinik olmayan mesaj
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "S7",
        "title": "Klinik olmayan sohbet mesajı",
        "input_context": {
            "medical_history": "Kronik Hastalıklar: Yok\nMevcut İlaçlar: Yok\nAlerjiler: Yok",
            "lab_anomalies": "Anormal kan tahlili bulgusu yok.",
            "radiology_findings": "Kayıtlı radyoloji görüntüsü yok.",
        },
        "user_message": "selam, nasılsın",
        "expected": {
            "response_type": "chat_message",   # clinical_roadmap DEĞİL
            "should_not_trigger_roadmap": True,
        },
        "should_not_contain": ["risk saptandı", "differential_diagnosis"],
    },
]


# ── Few-shot örnekler (LLM prompt'u için) ─────────────────────────────────────
# Her örnekte: hasta bağlamı + mesaj → beklenen JSON çıktısı
# Sadece en temsili 2 senaryo kullanılır (token tasarrufu için)

FEW_SHOT_EXAMPLES = [
    {
        "scenario_id": "S1",
        "context": (
            "Hasta: 45 yaşında erkek. "
            "Kronik Hastalıklar: Hipertansiyon. Mevcut İlaçlar: Parasetamol. "
            "Anormal lab: Yok. Radyoloji: Yok. "
            "Şikayet: 3 gündür şiddetli başağrısı, ense tutulması."
        ),
        "ideal_output": {
            "risk_level": "high",
            "red_flags": ["Kontrol altında olmayan hipertansiyonda hipertansif kriz riski"],
            "differential_diagnosis": [
                {
                    "condition": "Hipertansif Başağrısı",
                    "confidence": "high",
                    "supporting_findings": ["Bilinen hipertansiyon öyküsü", "Ense tutulması"],
                    "against_findings": [],
                    "missing_information": ["Anlık kan basıncı değeri"],
                },
                {
                    "condition": "Gerilim Tipi Başağrısı",
                    "confidence": "medium",
                    "supporting_findings": ["3 gündür süregelen ağrı"],
                    "against_findings": ["Hipertansiyon varlığı önceliği değiştirir"],
                    "missing_information": ["Ağrı karakteri (zonklayıcı mı?)", "Bulantı var mı?"],
                },
            ],
            "recommended_departments": ["Kardiyoloji", "Nöroloji"],
            "immediate_action": "Kan basıncınızı ölçün. 160/100 mmHg üzerindeyse bugün bir sağlık kuruluşuna başvurun.",
            "doctor_visit_plan": "2-3 gün içinde kardiyoloji veya dahiliye randevusu alın.",
            "tests_to_discuss": ["Anlık ve 24 saatlik kan basıncı takibi", "EKG", "Fundoskopi (göz dibi)"],
            "treatment_topics_to_discuss": [
                "Mevcut antihipertansif tedavinin yeterliliği",
                "Parasetamol dışı analjezik seçeneği (NSAİD kontraendike)",
            ],
            "treatment_phases": [
                {
                    "phase": "immediate",
                    "timeframe": "Bugün",
                    "actions": ["Kan basıncı ölçümü", "Dinlenme ve stres azaltma", "Yeterli sıvı alımı"],
                },
                {
                    "phase": "short_term",
                    "timeframe": "1-2 hafta",
                    "actions": ["Kardiyoloji viziti", "İlaç dozunun gözden geçirilmesi"],
                },
            ],
            "lifestyle_modifications": [
                "Tuzu günde 5 gramın altında tutun",
                "Kafein ve alkolü sınırlayın",
                "Düzenli uyku ve stres yönetimi",
            ],
            "do_not_do": [
                "İbuprofen veya naproksen gibi NSAİD almayın — kan basıncını yükseltir",
                "Başağrısını 'sadece yorgunluk' diye geçiştirmeyin",
            ],
            "follow_up_timeline": "1 hafta sonra kontrolü aksatmayın.",
            "disclaimer": "Bu değerlendirme tanı veya tedavi yerine geçmez. Mutlaka bir hekime danışın.",
        },
    },
    {
        "scenario_id": "S3",
        "context": (
            "Hasta: Hipertansiyon + Diyabet öyküsü. "
            "Şikayet: ANİ göğüs ağrısı, sol kola vurma, terleme."
        ),
        "ideal_output": {
            "risk_level": "critical",
            "red_flags": [
                "Akut koroner sendrom bulguları (sol kola vuran ağrı + terleme)",
                "Kardiyovasküler risk faktörleri: hipertansiyon + diyabet",
            ],
            "differential_diagnosis": [
                {
                    "condition": "Akut Miyokard Enfarktüsü (Kalp Krizi)",
                    "confidence": "high",
                    "supporting_findings": ["Sol kola vuran ağrı", "Terleme", "Ani başlangıç", "Kardiyovasküler risk faktörleri"],
                    "against_findings": [],
                    "missing_information": ["EKG bulguları", "Troponin değeri"],
                },
            ],
            "recommended_departments": ["Acil Servis"],
            "immediate_action": "HEMEN 112'yi arayın veya en yakın acil servise gidin. Bu belirtiler hayatı tehdit eden bir kalp kriziyle uyumludur. Beklemeden hareket edin.",
            "doctor_visit_plan": "Acil serviste kardiyoloji konsültasyonu.",
            "tests_to_discuss": ["EKG", "Troponin I/T", "CK-MB", "Acil ekokardiyografi"],
            "treatment_topics_to_discuss": [],
            "treatment_phases": [
                {
                    "phase": "immediate",
                    "timeframe": "Şimdi",
                    "actions": ["112'yi arayın", "Oturun veya uzanın", "Tek başınıza araç kullanmayın"],
                },
            ],
            "lifestyle_modifications": [],
            "do_not_do": [
                "Tek başınıza araç kullanmayın",
                "Beklemeden hareket edin — zaman = miyokard",
                "Ağrı geçer diye beklemeyin",
            ],
            "follow_up_timeline": "Acil servis sonrası kardiyoloji takibi.",
            "disclaimer": "Bu değerlendirme tanı veya tedavi yerine geçmez. ACİL DURUM — HEMEN 112.",
        },
    },
]
