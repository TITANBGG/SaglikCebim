from __future__ import annotations

import json
import os

import httpx

from .base import EvidenceProvider, EvidenceResult


class ClinicalKeyAIProvider(EvidenceProvider):
    BASE_URL = "https://ai.clinicalkey.com"
    CONVERSATION_URL = f"{BASE_URL}/api/conversation"

    def __init__(self) -> None:
        self.cookie = (
            os.getenv("CLINICALKEY_COOKIE", "").strip()
            or os.getenv("CLINICAL_KEY_COOKIE", "").strip()
        )

    def is_available(self) -> bool:
        placeholders = {"", "demo-cookie", "your-cookie-here", "buraya_cookie"}
        return self.cookie.lower() not in placeholders

    async def search(self, query: str, max_results: int = 3) -> list[EvidenceResult]:
        if not self.is_available():
            return []
        try:
            return await self._ask(query=query, max_results=max_results)
        except Exception as exc:
            print(f"[ClinicalKeyAI] Hata: {exc} - fallback aktif")
            return []

    async def _ask(self, query: str, max_results: int) -> list[EvidenceResult]:
        headers = {
            "Cookie": self.cookie,
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36"
            ),
            "Origin": "https://ai.clinicalkey.com",
            "Referer": "https://ai.clinicalkey.com/",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        payload = {
            "question": query,
            "languageCode": "en",
        }

        final_summary = ""
        references: list[dict] = []

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                self.CONVERSATION_URL,
                headers=headers,
                json=payload,
            ) as response:
                if response.status_code in (401, 403):
                    print("[ClinicalKeyAI] Cookie gecersiz veya expire olmus")
                    return []

                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    answer = chunk.get("answer", {}) if isinstance(chunk, dict) else {}
                    summary = answer.get("summary")
                    if isinstance(summary, str) and summary:
                        final_summary = summary

                    refs = answer.get("references")
                    if isinstance(refs, list) and refs:
                        references = refs

        return self._build_results(query, final_summary, references, max_results)

    def _build_results(
        self,
        query: str,
        summary: str,
        references: list[dict],
        max_results: int,
    ) -> list[EvidenceResult]:
        results: list[EvidenceResult] = []

        if summary:
            results.append(
                EvidenceResult(
                    source="ClinicalKey AI",
                    title=f"Clinical Overview: {query[:80]}",
                    summary=summary[:1000],
                    url="https://ai.clinicalkey.com",
                    evidence_level="clinical-overview",
                    year="2026",
                )
            )

        max_refs = max(1, max_results)
        for ref in references[:max_refs]:
            if not isinstance(ref, dict):
                continue
            year_raw = ref.get("year", ref.get("publicationDate", ""))
            year = str(year_raw)[:4] if year_raw else None
            results.append(
                EvidenceResult(
                    source="ClinicalKey AI",
                    title=str(ref.get("title", "")) or "ClinicalKey Reference",
                    summary=str(ref.get("abstract", ref.get("snippet", ""))) or None,
                    url=str(ref.get("url", ref.get("link", ""))) or None,
                    evidence_level=self._infer_level(ref),
                    year=year,
                )
            )

        return results

    def _infer_level(self, ref: dict) -> str:
        pub_type = str(ref.get("publicationType", ref.get("type", ""))).lower()
        if "guideline" in pub_type:
            return "guideline"
        if "systematic" in pub_type or "meta" in pub_type:
            return "systematic review"
        if "randomized" in pub_type or "rct" in pub_type:
            return "randomized controlled trial"
        if "review" in pub_type:
            return "review"
        return "article"

    def search_sync(self, query: str, max_results: int = 3) -> list[EvidenceResult]:
        """Synchronous helper for legacy call sites."""
        import asyncio

        return asyncio.run(self.search(query=query, max_results=max_results))
