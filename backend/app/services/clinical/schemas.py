from pydantic import BaseModel, Field
from typing import Literal, Optional


class DDxItem(BaseModel):
    """Ayırıcı Tanı (Differential Diagnosis) Öğesi"""
    condition: str = Field(description="Olası klinik senaryonun veya tanının adı")
    confidence: Literal["low", "medium", "high"] = Field(description="Bu senaryonun hastadaki verilere göre ihtimal derecesi")
    supporting_findings: list[str] = Field(default_factory=list, description="Bu senaryoyu destekleyen spesifik bulgular")
    against_findings: list[str] = Field(default_factory=list, description="Bu senaryoyu zayıflatan veya dışlayan bulgular")
    missing_information: list[str] = Field(default_factory=list, description="Bu tanıyı netleştirecek eksik bilgiler")
    # Calibrated Confidence fields (engine tarafından doldurulur, LLM doldurmaz)
    raw_confidence: Optional[float] = Field(default=None, description="LLM etiketinden türetilen ham sayısal skor (0-1)")
    calibrated_confidence: Optional[float] = Field(default=None, description="Platt scaling ile kalibre edilmiş skor (0-1)")
    evidence_support_score: Optional[float] = Field(default=None, description="PubMed kanıt desteği skoru (0-1)")


class TreatmentPhase(BaseModel):
    """Klinik Yol Haritası Tedavi Fazı"""
    phase: Literal["immediate", "short_term", "long_term"] = Field(description="Tedavinin aciliyet/zaman fazı")
    timeframe: str = Field(description="Aksiyon için öngörülen zaman dilimi")
    actions: list[str] = Field(description="Bu fazda atılması gereken somut klinik adımlar")


class MonitoringPlan(BaseModel):
    """İzlem Planı"""
    parameters: list[str] = Field(default_factory=list, description="Takip edilecek parametreler")
    frequency: str = Field(default="", description="İzlem sıklığı")
    red_flag_thresholds: list[str] = Field(default_factory=list, description="Acile yönlendirme gerektiren eşik değerler")


class EvidenceRef(BaseModel):
    """Kanıt Referansı"""
    source: str = Field(description="Kaynak adı (PubMed, ClinicalKey, UpToDate, vb.)")
    title: str = Field(description="Makale veya rehber başlığı")
    summary: Optional[str] = Field(default=None, description="Kısa özet")
    url: Optional[str] = Field(default=None, description="Kaynak URL")
    evidence_level: Optional[str] = Field(default=None, description="Kanıt düzeyi (Ia, Ib, IIa, vb.)")
    year: Optional[str] = Field(default=None, description="Yayın yılı")
    pmid: Optional[str] = Field(default=None, description="PubMed ID")


class ClinicalRoadmap(BaseModel):
    """LLM tarafından üretilecek yapılandırılmış Klinik Yol Haritası Çıktısı"""
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        description="Mevcut bulgulara göre genel klinik risk düzeyi"
    )
    red_flags: list[str] = Field(default_factory=list, description="Acil müdahale gerektirebilecek bulgular")
    differential_diagnosis: list[DDxItem] = Field(default_factory=list, description="Olası klinik senaryolar (DDx)")
    recommended_departments: list[str] = Field(default_factory=list, description="Yönlendirilmesi gereken tıbbi branşlar")
    immediate_action: str = Field(default="", description="Hemen alınması gereken aksiyon")
    doctor_visit_plan: str = Field(default="", description="Hekim başvuru planı")
    tests_to_discuss: list[str] = Field(default_factory=list, description="Doktorla görüşülecek tetkikler")
    treatment_topics_to_discuss: list[str] = Field(default_factory=list, description="Doktorla görüşülecek tedavi başlıkları")
    treatment_phases: list[TreatmentPhase] = Field(default_factory=list, description="Zaman çizelgesine göre tedavi fazları")
    monitoring_plan: MonitoringPlan = Field(default_factory=lambda: MonitoringPlan(), description="İzlem planı")
    lifestyle_modifications: list[str] = Field(default_factory=list, description="Yaşam tarzı önerileri")
    do_not_do: list[str] = Field(default_factory=list, description="Hastanın KESİNLİKLE YAPMAMASI gerekenler")
    follow_up_timeline: str = Field(default="", description="Takip zaman çizelgesi")
    evidence_references: list[EvidenceRef] = Field(default_factory=list, description="Kanıt referansları")
    safety_validated: bool = Field(default=False, description="SafetyValidator kontrolünden geçti mi?")
    disclaimer: str = Field(
        default="Bu değerlendirme tanı veya tedavi yerine geçmez.",
        description="Sorumluluk reddi beyanı"
    )

    # ClinicalKey tedavi rehberi (engine tarafından doldurulur)
    treatment_guidance: Optional[list[str]] = Field(default=None, description="ClinicalKey tedavi önerileri")

    # Ek debug/metadata alanları (önceki sistemle uyumluluk)
    safety_violations: Optional[list[str]] = Field(default=None, description="SafetyValidator ihlalleri")
    debug_trace: Optional[list[str]] = Field(default=None, description="Klinik motorun çalışma adımları")
