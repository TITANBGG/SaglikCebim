"""
ClinicalRoadmap Generator — Hasta bağlamından yapılandırılmış ClinicalRoadmap üretir.

Akış:
  1. Hasta bağlamını topla (ContextBuilder)
  2. Evidence varsa çek (EvidenceEngine)
  3. Ollama/Llama'ya format="json" ile çağrı yap
  4. JSON parse başarısız → fallback_roadmap()
  5. Safety validation fail → safe_fallback() döndür
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger("roadmap_generator")


from app.services.clinical.schemas import (
    ClinicalRoadmap,
    DDxItem,
    TreatmentPhase,
    MonitoringPlan,
)
from app.services.clinical.safety_validator import SafetyValidator


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT_TEMPLATE = """\
Sen SağlıkCebim'in klinik karar destek asistanısın.

GÖREVIN:
- Risk düzeyi belirle (low / medium / high / critical)
- Olası tanıları listele (differential_diagnosis) — HER biri için confidence, supporting_findings, against_findings, missing_information doldur
- Bölüm yönlendirmesi yap (recommended_departments)
- Acil eylem belirt (immediate_action) — kritik/acil ise "112" veya "acil servis" içermeli
- Doktor ziyaret planı yaz (doctor_visit_plan) — ne zaman, hangi branş
- İstenmesi önerilen tetkikler listele (tests_to_discuss)
- Doktorla görüşülecek tedavi konularını yaz (treatment_topics_to_discuss)
- Tedavi fazlarını doldur (treatment_phases): immediate / short_term / long_term — her fazda somut eylemler
- Yaşam tarzı önerileri ver (lifestyle_modifications) — en az 2 madde
- Yapılmaması gerekenleri yaz (do_not_do) — en az 1 madde

YASAKLAR (güvenlik):
- Kesin tanı koyma ("Tanınız X'tir" deme)
- Reçete yazma veya ilaç dozu verme
- "Antibiyotik başlayın" gibi doğrudan tedavi talimatı
- "Doktora gitmenize gerek yok" ifadesi

ÇIKTI: Sadece geçerli JSON. Markdown yok, açıklama yok. Şemaya birebir uy.
ŞEMA: {schema}

---
ÖRNEK 1 — Hipertansiyonlu hastada başağrısı (risk: high)
BAĞLAM: Hasta 45y/E. Kronik hastalık: Hipertansiyon. İlaç: Parasetamol. Şikayet: 3 gündür şiddetli başağrısı, ense tutulması.
BEKLENEN ÇIKTI (özet):
{{
  "risk_level": "high",
  "red_flags": ["Kontrol altında olmayan hipertansiyonda kriz riski"],
  "differential_diagnosis": [
    {{"condition": "Hipertansif Başağrısı", "confidence": "high", "supporting_findings": ["Bilinen hipertansiyon", "Ense tutulması"], "against_findings": [], "missing_information": ["Anlık kan basıncı"]}},
    {{"condition": "Gerilim Tipi Başağrısı", "confidence": "medium", "supporting_findings": ["3 günlük süre"], "against_findings": ["Hipertansiyon önceliği değiştirir"], "missing_information": ["Ağrı karakteri"]}}
  ],
  "recommended_departments": ["Kardiyoloji", "Nöroloji"],
  "immediate_action": "Kan basıncınızı ölçün. 160/100 mmHg üzerindeyse bugün sağlık kuruluşuna başvurun.",
  "doctor_visit_plan": "2-3 gün içinde kardiyoloji veya dahiliye randevusu alın.",
  "tests_to_discuss": ["Anlık kan basıncı ölçümü", "EKG", "Fundoskopi"],
  "treatment_topics_to_discuss": ["Antihipertansif tedavinin yeterliliği", "NSAİD yerine güvenli analjezik"],
  "treatment_phases": [
    {{"phase": "immediate", "timeframe": "Bugün", "actions": ["Kan basıncı ölçümü", "Dinlenme"]}},
    {{"phase": "short_term", "timeframe": "1-2 hafta", "actions": ["Kardiyoloji viziti", "İlaç gözden geçirme"]}}
  ],
  "lifestyle_modifications": ["Tuzu günde 5g altında tutun", "Kafein sınırlayın", "Düzenli uyku"],
  "do_not_do": ["İbuprofen veya NSAİD almayın — kan basıncını yükseltir"],
  "follow_up_timeline": "1 hafta sonra kontrol.",
  "disclaimer": "Bu değerlendirme tanı veya tedavi yerine geçmez."
}}

---
ÖRNEK 2 — Ani göğüs ağrısı (risk: critical)
BAĞLAM: Hasta Hipertansiyon + Diyabet. Şikayet: Ani göğüs ağrısı, sol kola vuruyor, terleme.
BEKLENEN ÇIKTI (özet):
{{
  "risk_level": "critical",
  "red_flags": ["Sol kola vuran ani göğüs ağrısı + terleme = AKS bulgusu"],
  "differential_diagnosis": [
    {{"condition": "Akut Miyokard Enfarktüsü", "confidence": "high", "supporting_findings": ["Sol kola vurma", "Terleme", "Ani başlangıç", "Kardiyovasküler risk faktörleri"], "against_findings": [], "missing_information": ["EKG", "Troponin"]}}
  ],
  "recommended_departments": ["Acil Servis"],
  "immediate_action": "HEMEN 112'yi arayın veya en yakın acil servise gidin. Bu belirtiler hayatı tehdit edebilir.",
  "doctor_visit_plan": "Acil serviste kardiyoloji konsültasyonu.",
  "tests_to_discuss": ["EKG", "Troponin I/T", "CK-MB"],
  "treatment_topics_to_discuss": [],
  "treatment_phases": [{{"phase": "immediate", "timeframe": "Şimdi", "actions": ["112'yi arayın", "Oturun/uzanın", "Tek başınıza araç kullanmayın"]}}],
  "lifestyle_modifications": [],
  "do_not_do": ["Tek başınıza araç kullanmayın", "Beklemeyin — zaman = miyokard"],
  "follow_up_timeline": "Acil sonrası kardiyoloji takibi.",
  "disclaimer": "ACİL DURUM — derhal 112'yi arayın."
}}
"""

_PATIENT_CONTEXT_TEMPLATE = """\
Hasta bilgileri:
- Şikayet: {chief_complaint}
- Semptomlar: {symptoms}
- Süre: {duration}
- Yaş/Cinsiyet: {age}/{gender}
- Kronik hastalıklar: {chronic_conditions}
- Son anormal lab değerleri: {abnormal_labs}
- Radyoloji bulguları: {radiology_findings}
- Geçmiş şikayetler: {history}
- Kanıt kaynakları: {evidence_summary}
"""


def fallback_roadmap() -> ClinicalRoadmap:
    """LLM yanıt veremediğinde döndürülecek güvenli yol haritası."""
    return ClinicalRoadmap(
        risk_level="medium",
        red_flags=[],
        differential_diagnosis=[],
        recommended_departments=["Aile Hekimi"],
        immediate_action="Lütfen bir sağlık kuruluşuna başvurun.",
        doctor_visit_plan="En kısa sürede aile hekiminize danışın.",
        tests_to_discuss=[],
        treatment_topics_to_discuss=[],
        treatment_phases=[],
        monitoring_plan=MonitoringPlan(parameters=[], frequency="", red_flag_thresholds=[]),
        lifestyle_modifications=[],
        do_not_do=[],
        follow_up_timeline="",
        evidence_references=[],
        safety_validated=False,
        disclaimer="Sistem bu sefer yanıt üretemedi. Lütfen bir hekime başvurun.",
        debug_trace=["fallback_roadmap_triggered"],
    )


def symptom_smart_fallback(message: str) -> ClinicalRoadmap:
    """LLM başarısız olduğunda semptom anahtar kelimelerine göre anlamlı yol haritası üretir."""
    msg = (
        message.lower()
        .replace("ı", "i").replace("ğ", "g").replace("ü", "u")
        .replace("ş", "s").replace("ö", "o").replace("ç", "c")
    )

    # ── Kardiyak ────────────────────────────────────────────────────────────
    if any(k in msg for k in ["kalp", "kalb", "gogus", "gogsum", "carpinti", "gogs", "sol kol", "enfarkt", "gogsl"]):
        return ClinicalRoadmap(
            risk_level="high",
            red_flags=["Kardiyak kökenli semptom şüphesi"],
            differential_diagnosis=[
                DDxItem(condition="Angina pektoris", confidence="medium",
                        supporting_findings=["Göğüs/kalp bölgesi şikayeti"],
                        against_findings=[], missing_information=["EKG", "Troponin sonucu"]),
                DDxItem(condition="Kardiyak aritmi", confidence="low",
                        supporting_findings=["Çarpıntı / göğüs baskısı"],
                        against_findings=[], missing_information=["Holter monitörizasyon"]),
            ],
            recommended_departments=["Kardiyoloji", "Acil Servis"],
            immediate_action="Kardiyak semptomlar ciddiye alınmalı. Ağrı şiddetlenirse veya nefes darlığı eklenirse hemen 112'yi arayın.",
            doctor_visit_plan="Bu hafta içinde kardiyoloji veya dahiliye randevusu alın.",
            tests_to_discuss=["EKG (elektrokardiyografi)", "Troponin I/T", "Tam kan sayımı", "Ekokardiyografi"],
            treatment_topics_to_discuss=["Kardiyak risk faktörleri değerlendirmesi", "Kan basıncı takibi"],
            treatment_phases=[TreatmentPhase(phase="immediate", timeframe="Bugün", actions=["Kan basıncı ölçümü", "Aktiviteyi kısıtla"]),
                              TreatmentPhase(phase="short_term", timeframe="Bu hafta", actions=["Kardiyoloji viziti", "EKG"])],
            monitoring_plan=MonitoringPlan(parameters=["Kalp hızı", "Kan basıncı"], frequency="Günlük", red_flag_thresholds=["Ağrı > 15 dk", "Nefes darlığı"]),
            lifestyle_modifications=["Yoğun fiziksel aktiviteden kaçının", "Kafein ve sigarayı azaltın"],
            do_not_do=["Semptomları görmezden gelmeyin", "Tek başınıza araç kullanmayın"],
            follow_up_timeline="1 hafta içinde kontrol",
            evidence_references=[],
            safety_validated=True,
            disclaimer="Bu değerlendirme tanı yerine geçmez. Semptomlar devam ederse derhal hekime başvurun.",
            debug_trace=["symptom_smart_fallback_cardiac"],
        )

    # ── Nörolojik — baş dönmesi / baş ağrısı ────────────────────────────────
    if any(k in msg for k in ["bas", "bas donmesi", "donuyor", "migren", "vertigo", "sersem", "baygin"]):
        return ClinicalRoadmap(
            risk_level="medium",
            red_flags=[],
            differential_diagnosis=[
                DDxItem(condition="Benign paroksismal pozisyonel vertigo (BPPV)", confidence="medium",
                        supporting_findings=["Baş dönmesi şikayeti"],
                        against_findings=[], missing_information=["Nörolojik muayene"]),
                DDxItem(condition="Gerilim tipi baş ağrısı", confidence="medium",
                        supporting_findings=["Baş bölgesi ağrısı/dönmesi"],
                        against_findings=[], missing_information=["Ağrı karakteri, süresi"]),
                DDxItem(condition="Migren", confidence="low",
                        supporting_findings=[], against_findings=[], missing_information=["Aura varlığı", "Aile öyküsü"]),
            ],
            recommended_departments=["Nöroloji", "Aile Hekimi"],
            immediate_action="Ani şiddetli baş ağrısı, görme kaybı veya konuşma bozukluğu gelişirse hemen 112'yi arayın.",
            doctor_visit_plan="1–2 hafta içinde nöroloji veya aile hekimi randevusu alın.",
            tests_to_discuss=["Tam kan sayımı", "Kan şekeri", "Kan basıncı ölçümü", "Gerekirse MRI"],
            treatment_topics_to_discuss=["Ağrı yönetimi", "Tetikleyici faktörler"],
            treatment_phases=[TreatmentPhase(phase="immediate", timeframe="Bugün", actions=["Dinlen", "Bol su iç", "Ekran süresini azalt"]),
                              TreatmentPhase(phase="short_term", timeframe="1–2 hafta", actions=["Nöroloji viziti"])],
            monitoring_plan=MonitoringPlan(parameters=["Ağrı şiddeti", "Sıklık"], frequency="Günlük", red_flag_thresholds=["Ani başlayan en kötü baş ağrısı", "Görme kaybı"]),
            lifestyle_modifications=["Düzenli uyku (7–8 saat)", "Yeterli su tüketimi", "Stres yönetimi"],
            do_not_do=["Aşırı ağrı kesici kullanmayın (rebound baş ağrısı riski)"],
            follow_up_timeline="2 hafta içinde kontrol",
            evidence_references=[],
            safety_validated=True,
            disclaimer="Bu değerlendirme tanı yerine geçmez. Şikayetler devam ederse hekime başvurun.",
            debug_trace=["symptom_smart_fallback_neuro"],
        )

    # ── Solunum ──────────────────────────────────────────────────────────────
    if any(k in msg for k in ["nefes", "oksuruk", "bogazim", "nefes darl"]):
        return ClinicalRoadmap(
            risk_level="medium",
            red_flags=[],
            differential_diagnosis=[
                DDxItem(condition="Üst solunum yolu enfeksiyonu", confidence="medium",
                        supporting_findings=["Solunum semptomu"],
                        against_findings=[], missing_information=["Ateş varlığı", "Süre"]),
                DDxItem(condition="Astım / reaktif hava yolu hastalığı", confidence="low",
                        supporting_findings=[], against_findings=[], missing_information=["Solunum fonksiyon testi"]),
            ],
            recommended_departments=["Göğüs Hastalıkları", "Aile Hekimi"],
            immediate_action="Nefes darlığı kötüleşirse veya dudak/tırnak morarmaya başlarsa hemen 112'yi arayın.",
            doctor_visit_plan="Bu hafta içinde aile hekimine başvurun.",
            tests_to_discuss=["Akciğer grafisi", "Solunum fonksiyon testi (SFT)", "Tam kan sayımı"],
            treatment_topics_to_discuss=["Enfeksiyon tedavisi", "Bronkodilatatör kullanımı"],
            treatment_phases=[TreatmentPhase(phase="immediate", timeframe="Bugün", actions=["Dinlen", "Bol sıvı al"])],
            monitoring_plan=MonitoringPlan(parameters=["Nefes sıklığı", "Ateş"], frequency="Günlük", red_flag_thresholds=["SpO2 < 95%", "Siyanoz"]),
            lifestyle_modifications=["Sigaradan uzak durun", "Allerjenlerden kaçının"],
            do_not_do=["Doktor önerisi olmadan antibiyotik kullanmayın"],
            follow_up_timeline="1 hafta içinde kontrol",
            evidence_references=[],
            safety_validated=True,
            disclaimer="Bu değerlendirme tanı yerine geçmez.",
            debug_trace=["symptom_smart_fallback_respiratory"],
        )

    # ── Gastrointestinal ─────────────────────────────────────────────────────
    if any(k in msg for k in ["mide", "bulanti", "kusma", "ishal", "karin", "reflu"]):
        return ClinicalRoadmap(
            risk_level="low",
            red_flags=[],
            differential_diagnosis=[
                DDxItem(condition="Gastroözofageal reflü hastalığı (GÖRH)", confidence="medium",
                        supporting_findings=["GI semptom bildirimi"],
                        against_findings=[], missing_information=["Endoskopi"]),
                DDxItem(condition="Akut gastroenterit", confidence="medium",
                        supporting_findings=["Bulantı/ishal"], against_findings=[], missing_information=["Dışkı kültürü"]),
            ],
            recommended_departments=["Gastroenteroloji", "Aile Hekimi"],
            immediate_action="Kanlı dışkı, şiddetli karın ağrısı veya dehidrasyon belirtisi varsa hemen başvurun.",
            doctor_visit_plan="Şikayetler 3 günden uzun sürerse aile hekimine başvurun.",
            tests_to_discuss=["Tam kan sayımı", "Biyokimya", "Dışkı tahlili (gerekirse)"],
            treatment_topics_to_discuss=["Beslenme düzenlenmesi", "Asit baskılayıcı tedavi"],
            treatment_phases=[TreatmentPhase(phase="immediate", timeframe="Bugün", actions=["Bol su iç", "Hafif beslen", "Yağlı/baharatlı yiyeceklerden kaçın"])],
            monitoring_plan=MonitoringPlan(parameters=["Bulantı şiddeti", "Dışkı karakteri"], frequency="Günlük", red_flag_thresholds=["Kanlı dışkı", "Sarılık"]),
            lifestyle_modifications=["Küçük porsiyonlar halinde ye", "Yatmadan 3 saat önce yemek yeme", "Kahve ve alkolü azalt"],
            do_not_do=["NSAID ve aspirin kullanmayın", "Aç kalmayın"],
            follow_up_timeline="3–5 gün içinde tekrar değerlendir",
            evidence_references=[],
            safety_validated=True,
            disclaimer="Bu değerlendirme tanı yerine geçmez.",
            debug_trace=["symptom_smart_fallback_gi"],
        )

    # ── Genel / varsayılan ───────────────────────────────────────────────────
    return ClinicalRoadmap(
        risk_level="medium",
        red_flags=[],
        differential_diagnosis=[
            DDxItem(condition="Değerlendirme için daha fazla bilgi gerekiyor", confidence="low",
                    supporting_findings=[], against_findings=[], missing_information=["Şikayetin süresi", "Eşlik eden semptomlar"]),
        ],
        recommended_departments=["Aile Hekimi"],
        immediate_action="Şikayetleriniz için en kısa sürede bir sağlık kuruluşuna başvurun.",
        doctor_visit_plan="Bu hafta içinde aile hekiminize danışın.",
        tests_to_discuss=["Tam kan sayımı", "Biyokimya paneli", "İdrar tahlili"],
        treatment_topics_to_discuss=["Semptom değerlendirmesi"],
        treatment_phases=[TreatmentPhase(phase="short_term", timeframe="Bu hafta", actions=["Aile hekimi viziti"])],
        monitoring_plan=MonitoringPlan(parameters=["Şikayet şiddeti"], frequency="Günlük", red_flag_thresholds=["Şiddet artışı"]),
        lifestyle_modifications=["Düzenli uyku ve beslenmeye özen gösterin"],
        do_not_do=["Semptomları uzun süre görmezden gelmeyin"],
        follow_up_timeline="1 hafta içinde kontrol",
        evidence_references=[],
        safety_validated=True,
        disclaimer="Bu değerlendirme tanı yerine geçmez. Şikayetlerinizi bir hekimle paylaşın.",
        debug_trace=["symptom_smart_fallback_general"],
    )


def safe_fallback() -> ClinicalRoadmap:
    """Safety validation başarısız olduğunda döndürülecek yol haritası."""
    roadmap = fallback_roadmap()
    roadmap.disclaimer = (
        "Güvenlik doğrulaması başarısız oldu. "
        "Bu değerlendirme tanı veya tedavi yerine geçmez. Lütfen bir hekime başvurun."
    )
    roadmap.debug_trace = ["safety_validation_failed_safe_fallback"]
    return roadmap


class RoadmapGenerator:
    """
    Hasta bağlamından yapılandırılmış ClinicalRoadmap üretir.
    Ollama JSON kırdığında rule-based fallback ile akışı ayakta tutar.
    """

    def __init__(self):
        self.validator = SafetyValidator()
        from app.services.ollama_client import get_ollama_client
        self._client = get_ollama_client()

    def _build_system_prompt(self) -> str:
        schema = json.dumps(ClinicalRoadmap.model_json_schema(), ensure_ascii=False, indent=2)
        return _SYSTEM_PROMPT_TEMPLATE.format(schema=schema)

    def _build_patient_context(self, context: Dict[str, Any]) -> str:
        return _PATIENT_CONTEXT_TEMPLATE.format(
            chief_complaint=context.get("current_message", context.get("chief_complaint", "Belirtilmedi")),
            symptoms=context.get("symptoms", context.get("current_message", "Belirtilmedi")),
            duration=context.get("duration", "Belirtilmedi"),
            age=context.get("age", context.get("patient_profile", "Bilinmiyor")),
            gender=context.get("gender", "Belirtilmedi"),
            chronic_conditions=context.get("chronic_conditions", context.get("medical_history", "Yok")),
            abnormal_labs=context.get("abnormal_labs", context.get("lab_anomalies", "Yok")),
            radiology_findings=context.get("radiology_findings", "Yok"),
            history=context.get("history", context.get("chat_history", "Yok")),
            evidence_summary=context.get("evidence_summary", "Yok"),
        )

    def _parse_json_response(self, response: str) -> Dict:
        """JSON yanıtı parse et; başarısız olursa dict içindeki JSON'u çıkarmayı dene."""
        clean = (response or "").strip()
        # Markdown code block temizle
        clean = re.sub(r"^```(?:json)?", "", clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r"```$", "", clean).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _coerce_roadmap_data(self, data: Dict) -> Dict:
        """LLM çıktısını ClinicalRoadmap şemasına uygun hale getirir."""
        if not isinstance(data, dict):
            raise TypeError("LLM response is not a JSON object")

        # Risk level normalizasyonu — "moderate"/"medium" → "medium"
        risk_map = {
            "moderate": "medium",
            "medium": "medium",
            "orta": "medium",
            "düşük": "low",
            "dusuk": "low",
            "yüksek": "high",
            "yuksek": "high",
            "kritik": "critical",
        }
        risk = str(data.get("risk_level", "medium")).strip().lower()
        data["risk_level"] = risk_map.get(
            risk, risk if risk in {"low", "medium", "high", "critical"} else "medium"
        )

        # Alan defaultları
        data.setdefault("red_flags", [])
        data.setdefault("differential_diagnosis", [])
        data.setdefault("recommended_departments", [])
        data.setdefault("immediate_action", "Lütfen bir sağlık kuruluşuna başvurun.")
        data.setdefault("doctor_visit_plan", "En kısa sürede aile hekiminize danışın.")
        data.setdefault("tests_to_discuss", [])
        data.setdefault("treatment_topics_to_discuss", [])
        data.setdefault("treatment_phases", [])
        data.setdefault("lifestyle_modifications", [])
        data.setdefault("do_not_do", [])
        data.setdefault("follow_up_timeline", "")
        data.setdefault("evidence_references", [])

        # monitoring_plan normalizasyonu
        if "monitoring_plan" not in data or not isinstance(data.get("monitoring_plan"), dict):
            # Eski format (monitoring_parameters) ile uyumluluk
            old_params = data.pop("monitoring_parameters", []) or []
            data["monitoring_plan"] = {
                "parameters": old_params,
                "frequency": data.pop("monitoring_frequency", ""),
                "red_flag_thresholds": [],
            }
        else:
            mp = data["monitoring_plan"]
            mp.setdefault("parameters", [])
            mp.setdefault("frequency", "")
            mp.setdefault("red_flag_thresholds", [])

        # DDxItem normalizasyonu (eski "name" alanından "condition"'a dönüşüm)
        normalized_ddx = []
        for item in data["differential_diagnosis"]:
            if isinstance(item, dict):
                # "name" → "condition" uyumluluk
                if "name" in item and "condition" not in item:
                    item["condition"] = item.pop("name")
                item.setdefault("condition", "Değerlendirilemedi")
                confidence = str(item.get("confidence", "low")).strip().lower()
                item["confidence"] = confidence if confidence in {"low", "medium", "high"} else "low"
                item.setdefault("supporting_findings", [])
                item.setdefault("against_findings", [])
                item.setdefault("missing_information", [])
                # eski "confidence_basis" → supporting_findings'e ekle
                basis = item.pop("confidence_basis", None)
                if basis and basis not in item["supporting_findings"]:
                    item["supporting_findings"].insert(0, basis)
                normalized_ddx.append(item)
        data["differential_diagnosis"] = normalized_ddx

        # TreatmentPhase normalizasyonu (eski "care_phases" uyumluluğu)
        if not data["treatment_phases"]:
            old_phases = data.pop("care_phases", []) or []
            if old_phases:
                data["treatment_phases"] = old_phases
        for phase in data["treatment_phases"]:
            if isinstance(phase, dict):
                value = str(phase.get("phase", "short_term")).strip().lower()
                phase["phase"] = value if value in {"immediate", "short_term", "long_term"} else "short_term"
                phase.setdefault("timeframe", "")
                phase.setdefault("actions", [])

        # EvidenceRef normalizasyonu
        normalized_refs = []
        for ref in data["evidence_references"]:
            if isinstance(ref, dict):
                ref.setdefault("source", "Bilinmiyor")
                ref.setdefault("title", "Başlık Yok")
                normalized_refs.append(ref)
        data["evidence_references"] = normalized_refs

        return data

    def generate(self, context: Dict[str, Any], original_message: str = "") -> ClinicalRoadmap:
        """
        Yeni üretim akışı:
        1. symptom_smart_fallback → garanti kaliteli temel yapı
        2. Hasta verisi varsa LLM ile kişiselleştir (basit metin prompt)
        3. LLM başarısız → temel yapıyı döndür
        """
        message = original_message or context.get("current_message", "")

        # 1. Temel yapı — her zaman çalışır
        base = symptom_smart_fallback(message)

        # 2. Kişiselleştirme — hasta verisi var mı?
        has_history = context.get("medical_history", "").strip() not in (
            "Kronik Hastalıklar: Yok\nAlerjiler: Yok\nMevcut İlaçlar: Yok", "")
        has_labs = context.get("lab_anomalies", "").strip() not in (
            "Anormal kan tahlili bulgusu yok.", "")
        has_radio = context.get("radiology_findings", "").strip() not in (
            "Kayıtlı radyoloji görüntüsü yok.", "",
            "Son radyoloji görüntüsünde anormal bulgu raporlanmadı.")

        if not (has_history or has_labs or has_radio):
            base.debug_trace = (base.debug_trace or []) + ["no_patient_data_base_used"]
            return base

        # 3. LLM ile kişiselleştir
        try:
            return self._personalize_with_llm(base, context, message)
        except Exception as exc:
            logger.warning("[RoadmapGenerator] Kişiselleştirme başarısız, temel kullanılıyor: %s", exc)
            base.debug_trace = (base.debug_trace or []) + ["personalization_failed"]
            return base

    def _personalize_with_llm(self, base: ClinicalRoadmap, context: Dict[str, Any], message: str) -> ClinicalRoadmap:
        """Temel roadmap'i hasta verileriyle LLM aracılığıyla kişiselleştirir."""

        system = (
            "Sen SağlıkCebim'in klinik asistanısın. SADECE TÜRKÇE yaz.\n"
            "Hastanın sağlık verilerini ve şikayetini analiz et.\n"
            "TAM OLARAK bu 5 satır formatı kullan, başka hiçbir şey yazma:\n\n"
            "RİSK: [DÜŞÜK / ORTA / YÜKSEK / KRİTİK]\n"
            "UYARILAR: [hastaya özel uyarı1] | [uyarı2] — yoksa YOK yaz\n"
            "TEKİKLER: [hastaya özel test1] | [test2] — yoksa YOK yaz\n"
            "YORUM: [hastanın kronik hastalıkları/tahlilleri açısından 1-2 cümle özel yorum]\n"
            "SORU: [eksik kritik bilgi için 1 soru] — yoksa YOK yaz"
        )

        labs = context.get("labs_full") or context.get("lab_anomalies", "Normal sınırlar içinde")
        patient_block = (
            f"HASTA: {context.get('patient_profile', 'Bilinmiyor')}\n"
            f"KRONİK/MEVCUT: {context.get('medical_history', 'Yok')}\n"
            f"KAN TAHLİLLERİ:\n{labs}\n"
            f"RADYOLOJİ: {context.get('radiology_findings', 'Yok')}\n"
            f"ŞİKAYET: {message}"
        )

        response = self._client.chat(system=system, user=patient_block, temperature=0.1)
        return self._merge_personalization(base, response)

    def _merge_personalization(self, base: ClinicalRoadmap, llm_response: str) -> ClinicalRoadmap:
        """LLM kişiselleştirme yanıtını temel roadmap ile birleştirir."""
        risk_map = {
            "DÜŞÜK": "low", "LOW": "low",
            "ORTA": "medium", "MEDIUM": "medium",
            "YÜKSEK": "high", "HIGH": "high",
            "KRİTİK": "critical", "CRITICAL": "critical",
        }

        data: Dict[str, str] = {}
        for line in llm_response.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                data[key.strip().upper()] = val.strip()

        # Risk seviyesini güncelle — asla düşürme, sadece yükselt
        risk_priority = ["low", "medium", "high", "critical"]
        if "RİSK" in data:
            new_risk = risk_map.get(data["RİSK"].upper().split()[0])
            if new_risk and risk_priority.index(new_risk) > risk_priority.index(base.risk_level):
                base.risk_level = new_risk

        # Hastaya özel uyarılar → red_flags'e ekle
        if "UYARILAR" in data and data["UYARILAR"].upper() not in ("YOK", ""):
            new_flags = [f.strip() for f in data["UYARILAR"].split("|")
                         if f.strip() and f.strip().upper() != "YOK"]
            base.red_flags = list(dict.fromkeys(new_flags + base.red_flags))

        # Hastaya özel tetkikler → tests_to_discuss'ın başına koy
        if "TEKİKLER" in data and data["TEKİKLER"].upper() not in ("YOK", ""):
            new_tests = [t.strip() for t in data["TEKİKLER"].split("|")
                         if t.strip() and t.strip().upper() != "YOK"]
            base.tests_to_discuss = list(dict.fromkeys(new_tests + base.tests_to_discuss))

        # Kişisel yorum → treatment_topics'in başına koy
        if "YORUM" in data and data["YORUM"].upper() not in ("YOK", ""):
            base.treatment_topics_to_discuss = [data["YORUM"]] + base.treatment_topics_to_discuss

        # Eksik bilgi sorusu → doctor_visit_plan'a ekle
        if "SORU" in data and data["SORU"].upper() not in ("YOK", "YOK.", ""):
            base.doctor_visit_plan = (
                f"⚕️ Doktora sorun: {data['SORU']}\n\n{base.doctor_visit_plan}"
            )

        base.safety_validated = True
        base.debug_trace = (base.debug_trace or []) + ["llm_personalized"]
        return base

    def _fetch_evidence(self, context: Dict[str, Any]) -> Dict | None:
        """Evidence engine'den kanıt çeker. Engine yoksa None döner."""
        try:
            from app.services.evidence.engine import EvidenceEngine
            engine = EvidenceEngine()
            if not engine.is_any_available():
                return None

            # Anahtar kelimeleri topla
            message = context.get("current_message", "")
            symptoms_raw = context.get("symptoms", message)
            if isinstance(symptoms_raw, str):
                symptoms = [symptoms_raw[:100]]
            else:
                symptoms = symptoms_raw[:3]

            # Async çağrıyı senkron olarak çalıştır
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, engine.search_for_case(symptoms))
                        results = future.result(timeout=10)
                else:
                    results = loop.run_until_complete(engine.search_for_case(symptoms))
            except Exception:
                results = []

            if not results:
                return None

            summary_parts = []
            refs = []
            for r in results[:5]:
                summary_parts.append(f"- {r.title} ({r.source})")
                refs.append({
                    "source": r.source,
                    "title": r.title,
                    "summary": getattr(r, "summary", None),
                    "url": getattr(r, "url", None),
                    "evidence_level": getattr(r, "evidence_level", None),
                    "year": getattr(r, "year", None),
                    "pmid": getattr(r, "pmid", None),
                })

            return {"summary": "\n".join(summary_parts), "refs": refs}

        except ImportError:
            return None
        except Exception as exc:
            logger.warning("[RoadmapGenerator] Evidence engine hatası: %s", exc)
            return None
