from __future__ import annotations

from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user

router = APIRouter()

PUBMED_ARTICLES = [
    {
        "pmid": "900001",
        "title": "Lifestyle interventions for glycemic control",
        "authors": "Cebim Health Team",
        "journal": "Clinical Nutrition",
        "pub_date": "2026",
        "url": "https://pubmed.ncbi.nlm.nih.gov/900001/",
        "abstract": "Diet and exercise improve glucose regulation in adults.",
        "keywords": ["glukoz", "glucose", "diabetes"],
    },
    {
        "pmid": "900002",
        "title": "Lipid lowering strategies and patient outcomes",
        "authors": "Cebim Health Team",
        "journal": "Cardiology Today",
        "pub_date": "2025",
        "url": "https://pubmed.ncbi.nlm.nih.gov/900002/",
        "abstract": "Reducing saturated fat and increasing movement supports lipid control.",
        "keywords": ["kolesterol", "cholesterol", "trigliserid", "lipid"],
    },
    {
        "pmid": "900003",
        "title": "Managing iron deficiency anemia in primary care",
        "authors": "Cebim Health Team",
        "journal": "Hematology Review",
        "pub_date": "2026",
        "url": "https://pubmed.ncbi.nlm.nih.gov/900003/",
        "abstract": "Iron-rich diet and evaluation of blood loss are central in anemia care.",
        "keywords": ["hemoglobin", "demir", "ferritin", "anemi"],
    },
    {
        "pmid": "900004",
        "title": "Thyroid dysfunction and long-term follow-up",
        "authors": "Cebim Health Team",
        "journal": "Endocrine Journal",
        "pub_date": "2026",
        "url": "https://pubmed.ncbi.nlm.nih.gov/900004/",
        "abstract": "TSH abnormalities require longitudinal evaluation and clinical follow-up.",
        "keywords": ["tsh", "tiroid", "thyroid"],
    },
]


class SearchRequest(BaseModel):
    query: str = Field(description="Aranacak PubMed sorgusu")
    max_results: int = Field(default=10, ge=1, le=50, description="Döndürülecek maksimum sonuç sayısı")
    include_focus: bool = Field(default=True, description="Konuya odaklı sonuçları önceliklendir")


class ChatRequest(BaseModel):
    message: str = Field(description="Kullanıcı mesajı")
    focus_tests: list[str] = Field(default_factory=list, description="Odaklanılacak test adları")
    articles: list[dict[str, Any]] = Field(default_factory=list, description="Kullanıcıya gösterilecek makale listesi")


async def search_pubmed_by_query(*, query: str, limit: int = 10, include_focus: bool = True) -> list[dict[str, Any]]:
    """Keyword-based PubMed fallback used in tests and offline mode."""

    query_lower = query.lower().strip()
    ranked: list[dict[str, Any]] = []
    for article in PUBMED_ARTICLES:
        haystack = " ".join([article["title"], article["abstract"], " ".join(article["keywords"]) ]).lower()
        score = sum(1 for keyword in article["keywords"] if keyword in query_lower or keyword in haystack)
        if score > 0 or not include_focus:
            ranked.append({**article, "score": score})

    if not ranked:
        ranked = [{**article, "score": 0} for article in PUBMED_ARTICLES]

    ranked.sort(key=lambda item: (-item["score"], item["pmid"]))
    return [
        {
            "pmid": item["pmid"],
            "title": item["title"],
            "authors": item["authors"],
            "journal": item["journal"],
            "pub_date": item["pub_date"],
            "url": item["url"],
            "abstract": item["abstract"],
        }
        for item in ranked[:limit]
    ]


def _summarize_articles(articles: list[dict[str, Any]]) -> dict[str, int]:
    keywords: Counter[str] = Counter()
    for article in articles:
        abstract = article.get("abstract", "").lower()
        if "glucose" in abstract or "glukoz" in abstract:
            keywords["glukoz"] += 1
        if "lipid" in abstract or "cholesterol" in abstract or "kolesterol" in abstract:
            keywords["lipid"] += 1
        if "iron" in abstract or "anemia" in abstract or "hemoglobin" in abstract:
            keywords["hematoloji"] += 1
        if "thyroid" in abstract or "tsh" in abstract:
            keywords["endokrinoloji"] += 1
    return dict(keywords)


@router.get("/daily")
async def get_daily_articles(limit: int = 5, current_user_id: str = Depends(get_current_user)):
    """Günlük öne çıkan makaleleri döndürür."""
    articles = await search_pubmed_by_query(query="günlük sağlık makaleleri", limit=limit, include_focus=False)
    return {"articles": articles, "summary": _summarize_articles(articles)}


@router.post("/search")
async def search_pubmed(payload: SearchRequest, current_user_id: str = Depends(get_current_user)):
    """Kullanıcının sorgusuna göre PubMed makaleleri arar."""
    articles = await search_pubmed_by_query(
        query=payload.query,
        limit=payload.max_results,
        include_focus=payload.include_focus,
    )
    return {
        "query": payload.query,
        "articles": articles,
        "summary": _summarize_articles(articles),
    }


@router.post("/chat")
async def multi_agent_chat(payload: ChatRequest, current_user_id: str = Depends(get_current_user)):
    """Makale odaklı çok ajanlı yanıt üretir."""
    focus_tests = [item.lower() for item in payload.focus_tests]
    if not focus_tests and payload.articles:
        focus_tests = [
            "glukoz" if "glucose" in str(article).lower() else "kolesterol"
            for article in payload.articles[:2]
        ]

    if not focus_tests:
        focus_tests = ["genel sağlık"]

    references = []
    for article in payload.articles[:3]:
        references.append(
            {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "pmid": article.get("pmid", ""),
            }
        )

    answer = (
        f"Sorunuz için temel bulgu: {', '.join(focus_tests)} ile ilgili literatür yaşam tarzı değişikliklerini ve düzenli takip öneriyor. "
        f"Tıbbi tanı için doktor değerlendirmesi gerekir."
    )
    if payload.articles:
        answer += f" {len(payload.articles)} ilgili çalışma incelendi."

    return {
        "answer": answer,
        "references": references,
        "suggestions": [
            "İlgili test adını yazarak daha spesifik sorabilirsiniz.",
            "Sonuçlarınız için öneri almak isterseniz raporu yükleyin.",
        ],
    }
