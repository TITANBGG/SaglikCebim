from __future__ import annotations

import os

import httpx

from .base import EvidenceProvider, EvidenceResult


class UpToDateProvider(EvidenceProvider):
    def __init__(self) -> None:
        self.api_key = os.getenv("UPTODATE_API_KEY", "").strip()
        self.base_url = os.getenv("UPTODATE_BASE_URL", "https://api.uptodate.com/v1/search")

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, max_results: int = 3) -> list[EvidenceResult]:
        if self.api_key:
            try:
                return await self._real_search(query, max_results)
            except Exception as exc:
                print(f"[UpToDate] real search error: {exc}; mock fallback")
        return self._mock_search(query, max_results)

    async def _real_search(self, query: str, max_results: int) -> list[EvidenceResult]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"query": query, "max_results": max_results}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()

        items = payload.get("results", []) if isinstance(payload, dict) else []
        out: list[EvidenceResult] = []
        for item in items[:max_results]:
            if not isinstance(item, dict):
                continue
            out.append(
                EvidenceResult(
                    source="UpToDate",
                    title=str(item.get("title", "UpToDate Topic")),
                    summary=str(item.get("summary", "")) or None,
                    url=str(item.get("url", "")) or None,
                    evidence_level="guideline",
                    year=str(item.get("year", "2024")),
                )
            )
        return out

    def _mock_search(self, query: str, max_results: int) -> list[EvidenceResult]:
        fixtures = [
            EvidenceResult(
                source="UpToDate",
                title=f"Evidence-based approach: {query[:80]}",
                summary="Mock clinical guidance from UpToDate adapter.",
                url="https://www.uptodate.com",
                evidence_level="guideline",
                year="2024",
            )
        ]
        return fixtures[:max_results]
