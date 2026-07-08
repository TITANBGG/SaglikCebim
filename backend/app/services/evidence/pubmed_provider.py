"""
PubMed (NCBI Entrez) evidence provider — BM25 re-ranking.

Akış:
  esearch → max 15 PMID → efetch → parse → BM25 re-rank → top-k döndür
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from .base import EvidenceProvider, EvidenceResult
from app.core.logging import get_logger

logger = get_logger("pubmed_provider")

_EMAIL   = os.getenv("PUBMED_EMAIL", "saglikcebim@example.com")
_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_EFETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
_TIMEOUT = 15
_CANDIDATE_MULTIPLIER = 5  # max_results * 5 aday çek, sonra re-rank


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _bm25_scores(query: str, corpus: list[str]) -> list[float]:
    """
    Pure-Python BM25 (rank_bm25 kütüphanesi varsa) veya TF-IDF fallback.
    Her iki durumda da liste döner; sıralama doğru çalışır.
    """
    tokenized_query = _tokenize(query)
    tokenized_corpus = [_tokenize(doc) for doc in corpus]

    try:
        from rank_bm25 import BM25Okapi  # type: ignore
        bm25 = BM25Okapi(tokenized_corpus)
        return list(bm25.get_scores(tokenized_query))
    except ImportError:
        # TF-IDF fallback: sorgu token'larının corpus'ta kaç kez geçtiğini say
        scores = []
        for tokens in tokenized_corpus:
            token_set = set(tokens)
            score = sum(1 for t in tokenized_query if t in token_set)
            scores.append(float(score))
        return scores


class PubMedProvider(EvidenceProvider):

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, max_results: int = 3) -> list[EvidenceResult]:
        candidate_count = min(max_results * _CANDIDATE_MULTIPLIER, 20)
        pmids = await self._esearch(query, candidate_count)
        if not pmids:
            return []
        candidates = await self._efetch(pmids)
        return self._rerank(query, candidates, top_k=max_results)

    # ── BM25 Re-ranking ───────────────────────────────────────────────────────

    def _rerank(
        self, query: str, results: list[EvidenceResult], top_k: int
    ) -> list[EvidenceResult]:
        if not results:
            return []

        corpus = [f"{r.title} {r.summary or ''}" for r in results]
        scores = _bm25_scores(query, corpus)

        ranked = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
        return [r for _, r in ranked[:top_k]]

    # ── NCBI API ──────────────────────────────────────────────────────────────

    async def _esearch(self, query: str, max_results: int) -> list[str]:
        params = {
            "db": "pubmed",
            "term": (
                f"({query}) AND ("
                "review[Publication Type] OR "
                "clinical trial[Publication Type] OR "
                "systematic review[Publication Type])"
            ),
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance",
            "email": _EMAIL,
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(_ESEARCH, params=params)
                resp.raise_for_status()
                data: dict[str, Any] = resp.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:
            logger.warning("PubMed esearch hatası: %s", exc)
            return []

    async def _efetch(self, pmids: list[str]) -> list[EvidenceResult]:
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
            "email": _EMAIL,
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(_EFETCH, params=params)
                resp.raise_for_status()
                xml_text = resp.text
        except Exception as exc:
            logger.warning("PubMed efetch hatası: %s", exc)
            return [
                EvidenceResult(
                    source="PubMed",
                    title=f"PMID {pmid}",
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    pmid=pmid,
                )
                for pmid in pmids
            ]

        return self._parse_xml(xml_text)

    def _parse_xml(self, xml_text: str) -> list[EvidenceResult]:
        results: list[EvidenceResult] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            logger.warning("PubMed XML parse hatası: %s", exc)
            return results

        for article in root.findall(".//PubmedArticle"):
            try:
                pmid_el  = article.find(".//PMID")
                pmid     = pmid_el.text if pmid_el is not None else ""

                title_el = article.find(".//ArticleTitle")
                title    = "".join(title_el.itertext()).strip() if title_el is not None else ""
                title    = title or f"PMID {pmid}"

                abstract_parts = [
                    t.strip()
                    for t in article.findall(".//AbstractText")
                    if t.text
                ]
                summary = " ".join(abstract_parts)[:500] or None

                year_el  = article.find(".//PubDate/Year")
                year     = year_el.text if year_el is not None else None

                journal_el = article.find(".//Journal/Title")
                journal    = journal_el.text if journal_el is not None else None

                authors        = article.findall(".//Author")
                evidence_level = "Review" if len(authors) > 5 else "Article"

                pub_types = [
                    pt.text or ""
                    for pt in article.findall(".//PublicationType")
                ]
                if any("Systematic Review" in pt or "Meta-Analysis" in pt for pt in pub_types):
                    evidence_level = "Systematic Review"
                elif any("Randomized Controlled Trial" in pt for pt in pub_types):
                    evidence_level = "Randomized Controlled Trial"

                results.append(EvidenceResult(
                    source="PubMed",
                    title=title,
                    summary=(summary or "") + (f" ({journal})" if journal else ""),
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    evidence_level=evidence_level,
                    year=year,
                    pmid=pmid,
                ))
            except Exception as exc:
                logger.debug("Makale parse hatası: %s", exc)
                continue

        return results
