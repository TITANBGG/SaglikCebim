from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class EvidenceResult(BaseModel):
    source: str
    title: str
    summary: Optional[str] = None
    url: Optional[str] = None
    evidence_level: Optional[str] = None
    year: Optional[str] = None
    pmid: Optional[str] = None


class EvidenceProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 3) -> list[EvidenceResult]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
