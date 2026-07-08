from __future__ import annotations

from typing import Optional


TURKISH_TO_MESH = {
    # Baş / nörolojik
    "baş ağrısı": "headache", "bas agrisi": "headache",
    "migren": "migraine",
    "baş dönmesi": "vertigo dizziness", "bas donmesi": "vertigo dizziness",
    "inme": "stroke", "felç": "stroke", "felc": "stroke",
    "epilepsi": "epilepsy", "sara": "epilepsy",
    # Kardiyovasküler
    "göğüs ağrısı": "chest pain", "gogus agrisi": "chest pain",
    "çarpıntı": "palpitation", "carpinti": "palpitation",
    "yüksek tansiyon": "hypertension", "yuksek tansiyon": "hypertension",
    "tansiyon": "hypertension",
    "kalp yetmezliği": "heart failure", "kalp yetmezligi": "heart failure",
    "kalp krizi": "myocardial infarction",
    "kolesterol": "dyslipidemia cholesterol",
    "trigliserid": "hypertriglyceridemia",
    # Solunum
    "nefes darlığı": "dyspnea", "nefes darligi": "dyspnea",
    "öksürük": "cough", "oksuruk": "cough",
    "zatürre": "pneumonia", "zaturre": "pneumonia",
    "astım": "asthma", "astim": "asthma",
    "bronşit": "bronchitis", "bronsit": "bronchitis",
    # Metabolik
    "diyabet": "diabetes mellitus", "şeker": "diabetes mellitus", "seker": "diabetes mellitus",
    "obezite": "obesity", "şişmanlık": "obesity",
    "tiroid": "thyroid disease",
    # Kan / hematoloji
    "demir eksikliği": "iron deficiency anemia", "demir eksikligi": "iron deficiency anemia",
    "anemi": "anemia", "kansızlık": "anemia", "kansizlik": "anemia",
    "hemoglobin": "hemoglobin anemia",
    "ferritin": "ferritin iron deficiency",
    "wbc": "leukocytosis leukopenia",
    # Mide / gastrointestinal
    "mide": "gastric disease", "mide ağrısı": "epigastric pain",
    "bulantı": "nausea vomiting", "bulanti": "nausea vomiting",
    "kusma": "vomiting",
    "ishal": "diarrhea",
    "reflü": "gastroesophageal reflux", "reflu": "gastroesophageal reflux",
    # Kas / iskelet
    "eklem ağrısı": "arthralgia", "eklem agrisi": "arthralgia",
    "bel ağrısı": "low back pain", "bel agrisi": "low back pain",
    "romatizma": "rheumatoid arthritis",
    # Genel
    "yorgunluk": "fatigue", "halsizlik": "fatigue",
    "ateş": "fever", "ates": "fever",
    "enfeksiyon": "infection",
    "antibiyotik": "antibiotic treatment",
    "alerji": "allergy",
}


def _normalize(value: str) -> str:
    return (
        str(value)
        .lower()
        .replace("ı", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
        .strip()
    )


def translate_symptoms(symptoms: list[str]) -> list[str]:
    translated: list[str] = []
    for symptom in symptoms:
        key = _normalize(symptom)
        translated.append(TURKISH_TO_MESH.get(key, symptom))
    return translated


def build_clinicalkey_query(
    symptoms: list[str],
    suspected_condition: Optional[str] = None,
    workflow: str = "physician",
) -> str:
    translated = translate_symptoms(symptoms)
    symptoms_str = ", ".join(translated) if translated else "non-specific symptoms"

    if suspected_condition:
        return (
            "Clinical overview and evidence-based management approach for a patient "
            f"presenting with {symptoms_str}. "
            f"Suspected condition: {suspected_condition}. "
            "What are the recommended diagnostic workup and treatment considerations?"
        )

    return (
        "What is the evidence-based clinical approach for a patient "
        f"presenting with {symptoms_str}? "
        "Include differential diagnosis, recommended workup, and management guidelines."
    )


def build_pubmed_query(symptoms: list[str], suspected_condition: Optional[str] = None) -> str:
    translated = translate_symptoms(symptoms)
    core = " OR ".join(translated) if translated else "clinical symptoms"
    if suspected_condition:
        core = f"({core}) AND ({suspected_condition})"
    return f"{core} AND (review[Publication Type] OR guideline) AND humans[MeSH Terms]"


class QueryBuilder:
    """Backward compatible helper used by older providers."""

    MAPPING = TURKISH_TO_MESH

    @classmethod
    def build_english_query(cls, term: str) -> str:
        key = _normalize(term)
        return cls.MAPPING.get(key, term)
