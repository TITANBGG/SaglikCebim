from __future__ import annotations

from .base import EvidenceResult


EVIDENCE_PRIORITY = {
    "guideline": 6,
    "systematic review": 5,
    "meta-analysis": 5,
    "randomized controlled trial": 4,
    "clinical-overview": 3,
    "review": 2,
    "article": 1,
}


def _score(level: str | None) -> int:
    if not level:
        return 0
    return EVIDENCE_PRIORITY.get(level.lower(), 0)


def deduplicate(results: list[EvidenceResult]) -> list[EvidenceResult]:
    seen: set[str] = set()
    unique: list[EvidenceResult] = []
    for item in results:
        key = (item.url or "").strip().lower() or item.title.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def rank(results: list[EvidenceResult]) -> list[EvidenceResult]:
    unique = deduplicate(results)
    return sorted(
        unique,
        key=lambda r: (_score(r.evidence_level), int(r.year or 0)),
        reverse=True,
    )


def get_top_by_source(results: list[EvidenceResult], max_per_source: int = 3) -> list[EvidenceResult]:
    buckets: dict[str, int] = {}
    out: list[EvidenceResult] = []
    for item in results:
        count = buckets.get(item.source, 0)
        if count >= max_per_source:
            continue
        buckets[item.source] = count + 1
        out.append(item)
    return out
