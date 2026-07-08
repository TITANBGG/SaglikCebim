from __future__ import annotations

import asyncio

from .base import EvidenceResult
from .clinicalkey_ai_provider import ClinicalKeyAIProvider
from .evidence_ranker import get_top_by_source, rank
from .pubmed_provider import PubMedProvider
from .query_builder import build_clinicalkey_query
from .uptodate_provider import UpToDateProvider


class EvidenceEngine:
    def __init__(self) -> None:
        self.providers = [
            PubMedProvider(),
            ClinicalKeyAIProvider(),
            UpToDateProvider(),
        ]

    def is_any_available(self) -> bool:
        return any(provider.is_available() for provider in self.providers)

    async def search_all(self, query: str, max_per_source: int = 3) -> list[EvidenceResult]:
        async def _run(provider):
            if not provider.is_available():
                return []
            try:
                return await provider.search(query, max_results=max_per_source)
            except Exception as exc:
                print(f"[EvidenceEngine] provider error: {provider.__class__.__name__}: {exc}")
                return []

        chunks = await asyncio.gather(*[_run(provider) for provider in self.providers])
        merged: list[EvidenceResult] = [item for chunk in chunks for item in chunk]
        ranked = rank(merged)
        return get_top_by_source(ranked, max_per_source=max_per_source)

    async def search_for_case(
        self,
        symptoms: list[str],
        suspected_condition: str | None = None,
        max_per_source: int = 3,
    ) -> list[EvidenceResult]:
        query = build_clinicalkey_query(symptoms, suspected_condition)
        return await self.search_all(query, max_per_source=max_per_source)
