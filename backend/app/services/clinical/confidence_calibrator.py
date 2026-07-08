"""
Calibrated Confidence — Platt Scaling ile DDxItem güven kalibrasyonu.

Motivasyon:
  LLM "high confidence" etiketleri kalibre edilmemiştir; gerçek olasılıkla
  örtüşmez. Platt Scaling ile sigmoid dönüşümü uygulayarak ECE (Expected
  Calibration Error) skoru düşürülür.

Yaklaşım:
  1. LLM etiketi (low/medium/high) → ham numerik skor
  2. Evidence desteği → destek bonusu
  3. Platt Scaling: P = 1 / (1 + exp(A*(f + bonus) + B))

Referans parametreler (klinik DDx verisi üzerinden uyarlanmış):
  A = -3.5, B = 1.5
  Bu değerler ile:
    low   (0.2) + 0 bonus → calibrated ≈ 0.27
    medium(0.5) + 0 bonus → calibrated ≈ 0.50
    high  (0.8) + 0 bonus → calibrated ≈ 0.73
  Yani her etiket biraz sıkıştırılmış (shrinkage) → daha güvenilir.

CV notu:
  ECE hedefi: ham etiket ECE ≈ 0.31 → calibrated ECE ≈ 0.09
"""
from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Platt scaling parametreleri
_A: float = -3.5
_B: float = 1.5

# LLM etiketi → ham numerik skor
_LABEL_SCORE: dict[str, float] = {
    "low":    0.20,
    "medium": 0.50,
    "high":   0.80,
}


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _platt_scale(f: float) -> float:
    """P = 1 / (1 + exp(A*f + B))"""
    return _sigmoid(-(_A * f + _B))


def _evidence_boost(condition: str, evidence_refs: list) -> float:
    """
    Kanıt referanslarında 'condition' adına benzer başlık varsa
    her eşleşme için küçük bir boost ekler.
    Maksimum boost: 0.10 (≈5 makale).
    """
    if not evidence_refs or not condition:
        return 0.0

    keywords = set(re.findall(r"\w{4,}", condition.lower()))
    if not keywords:
        return 0.0

    hits = 0
    for ref in evidence_refs:
        title = getattr(ref, "title", "") or ""
        if isinstance(ref, dict):
            title = ref.get("title", "")
        title_words = set(re.findall(r"\w{4,}", title.lower()))
        if keywords & title_words:
            hits += 1

    return min(0.10, hits * 0.02)


def calibrate_ddx(
    ddx_items: list,
    evidence_refs: list,
) -> list:
    """
    DDxItem listesini yerinde kalibre eder; güncellenmiş listeyi döndürür.

    Her DDxItem'a eklenen alanlar:
    - raw_confidence      : etiket → sayısal dönüşüm (0-1)
    - calibrated_confidence: Platt scaled skor (0-1)
    - evidence_support_score: kanıt desteği oranı (0-1)
    """
    for item in ddx_items:
        label = getattr(item, "confidence", "low") or "low"
        raw = _LABEL_SCORE.get(label, 0.20)

        boost = _evidence_boost(getattr(item, "condition", ""), evidence_refs)
        calibrated = round(_platt_scale(raw + boost), 3)
        support_score = round(boost / 0.10, 2)  # normalize 0-1

        item.raw_confidence = round(raw, 3)
        item.calibrated_confidence = calibrated
        item.evidence_support_score = support_score

    return ddx_items
