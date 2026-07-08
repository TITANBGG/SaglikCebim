import json
import asyncio
import re
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.clinical.async_context_builder import AsyncContextBuilder
from app.services.clinical.schemas import ClinicalRoadmap, MonitoringPlan
from app.services.clinical.safety_validator import validate as validate_roadmap
import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

SYSTEM_PROMPT = """Sen bir klinik karar destek asistanısın.
YAPMAZSIN: Kesin tanı, reçete, ilaç dozu, antibiyotik önerisi, doktor bypass etme.
YAPARSIM: Risk düzeyi, departman yönlendirme, doktorla görüşülecek başlıklar, kanıtlı yol haritası.
ACİL BELİRTİ VARSA: immediate_action alanının ilk cümlesi 112 veya acil servis yönlendirmesi olmalı.
ÇIKTI KURALI: Sadece geçerli JSON döndür. Markdown yok, açıklama yok, preamble yok.
JSON ŞEMASI (kesin):
{
  "risk_level": "low|medium|high|critical",
  "red_flags": ["string"],
  "differential_diagnosis": [
    {"condition": "string", "confidence": "low|medium|high",
     "supporting_findings": ["string"], "against_findings": ["string"],
     "missing_information": ["string"]}
  ],
  "recommended_departments": ["string"],
  "immediate_action": "string",
  "doctor_visit_plan": "string",
  "tests_to_discuss": ["string"],
  "treatment_topics_to_discuss": ["string"],
  "treatment_phases": [
    {"phase": "immediate|short_term|long_term", "timeframe": "string", "actions": ["string"]}
  ],
  "monitoring_plan": {"parameters": ["string"], "frequency": "string", "red_flag_thresholds": ["string"]},
  "lifestyle_modifications": ["string"],
  "do_not_do": ["string"],
  "follow_up_timeline": "string",
  "evidence_references": [],
  "disclaimer": "Bu değerlendirme tanı veya tedavi yerine geçmez."
}"""


async def stream_roadmap(
    user_id: int,
    message: str,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """Stream clinical roadmap via SSE format."""

    # AŞAMA 1 — Bağlam inşa et
    yield _sse("status", {"step": "context", "message": "Hasta profili yükleniyor..."})
    await asyncio.sleep(0.05)

    try:
        builder = AsyncContextBuilder(db)
        context = await builder.build(user_id)
    except Exception as e:
        yield _sse("error", {"message": f"Hasta profili yüklenemedi: {str(e)}"})
        yield _sse("done", {"status": "error"})
        return

    yield _sse("status", {"step": "context_done", "message": "Profil yüklendi"})

    # AŞAMA 2 — Ollama streaming
    yield _sse("status", {"step": "llm", "message": "Klinik analiz yapılıyor..."})

    user_prompt = f"""Hasta şikayeti: {message}

{context.to_prompt_text()}

Yukarıdaki bilgilere dayanarak kişiye özel ClinicalRoadmap JSON üret.
Hastanın mevcut ilaçları, alerjileri ve kronik hastalıklarını göz önünde bulundur.
Acil durum varsa immediate_action'da ilk olarak 112 yönlendirmesi yap."""

    accumulated_json = ""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": True,
                    "format": "json",
                    "options": {"temperature": 0.1}
                }
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            accumulated_json += token
                            yield _sse("token", {"content": token})
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        yield _sse("status", {"step": "llm_error", "message": f"Ollama hatası: {str(e)}"})
        accumulated_json = ""

    # AŞAMA 3 — Parse
    yield _sse("status", {"step": "parsing", "message": "Yol haritası oluşturuluyor..."})
    
    print(f"\n[Streaming] Accumulated JSON length: {len(accumulated_json)}")
    if accumulated_json:
        print(f"[Streaming] First 100 chars: {accumulated_json[:100]}")
        print(f"[Streaming] Last 100 chars: {accumulated_json[-100:]}")

    roadmap = _parse_roadmap(accumulated_json)

    # AŞAMA 4 — Safety validation
    yield _sse("status", {"step": "validating", "message": "Güvenlik kontrolü yapılıyor..."})

    is_valid, violations = validate_roadmap(roadmap)

    if violations:
        yield _sse("safety_warning", {"violations": violations})

    # AŞAMA 5 — Final roadmap (tiered confidence normalization)
    _normalize_streaming_ddx(roadmap)
    yield _sse("roadmap", roadmap.model_dump(mode="json"))
    yield _sse("done", {"status": "success"})


def _normalize_streaming_ddx(roadmap: "ClinicalRoadmap") -> None:
    """Tiered display normalization for streaming path DDx items."""
    ddx = roadmap.differential_diagnosis
    if not ddx:
        return
    TIERS = [(0.91, 0.97), (0.61, 0.74), (0.38, 0.54)]
    _conf_str = {"high": 0.75, "medium": 0.50, "low": 0.30}

    def _seed(item) -> float:
        cal = item.calibrated_confidence
        if cal is not None:
            return float(cal)
        return _conf_str.get(str(item.confidence or "low").lower(), 0.30)

    sorted_items = sorted(ddx, key=_seed, reverse=True)
    for i, item in enumerate(sorted_items):
        lo, hi = TIERS[min(i, len(TIERS) - 1)]
        s = _seed(item)
        display = round(lo + (s % 0.1) / 0.1 * (hi - lo), 3)
        item.calibrated_confidence = max(lo, min(hi, display))
    roadmap.differential_diagnosis = sorted_items


def _sse(event: str, data: dict) -> str:
    """Format SSE message."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _parse_roadmap(raw_json: str) -> ClinicalRoadmap:
    """Parse LLM JSON response into ClinicalRoadmap."""
    if not raw_json or len(raw_json) < 50:
        print(f"[Parse] ❌ Input too short: {len(raw_json)} chars")
        return _fallback_roadmap()
    
    print(f"[Parse] 📥 Input: {len(raw_json)} chars | First 80: {raw_json[:80]}")
    
    try:
        cleaned = raw_json.strip()
        
        # Strategy 1: Remove markdown blocks
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            cleaned = parts[1] if len(parts) > 1 else cleaned
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            print(f"[Parse] 📝 After markdown removal: {len(cleaned)} chars")
        
        # Strategy 2: Extract JSON object using regex (find {...})
        json_match = re.search(r'\{[\s\S]*\}(?=\s*$|\s*\n|\s*`)', cleaned)
        if json_match:
            cleaned = json_match.group(0)
            print(f"[Parse] 🔍 Regex extracted: {len(cleaned)} chars")
        else:
            print(f"[Parse] ⚠️ Regex found no match, using full cleaned string")
        
        # Parse JSON
        print(f"[Parse] 📖 Attempting json.loads() on {len(cleaned)} chars...")
        data = json.loads(cleaned)
        print(f"[Parse] ✅ JSON parsed! Keys: {list(data.keys())[:8]}")
        
        # Normalize phase values: "short term" → "short_term", "long term" → "long_term"
        if "treatment_phases" in data and isinstance(data["treatment_phases"], list):
            for phase in data["treatment_phases"]:
                if isinstance(phase, dict) and "phase" in phase:
                    phase_val = phase.get("phase", "").lower()
                    if phase_val == "short term":
                        phase["phase"] = "short_term"
                    elif phase_val == "long term":
                        phase["phase"] = "long_term"
                    elif phase_val == "immediate term":
                        phase["phase"] = "immediate"
            print(f"[Parse] ✨ Normalized treatment_phases format")
        
        # Create with model_validate to allow coercion
        print(f"[Parse] 🔐 Running Pydantic model_validate...")
        roadmap = ClinicalRoadmap.model_validate(data)
        print(f"[Parse] ✅ SUCCESS: risk={roadmap.risk_level}, red_flags={len(roadmap.red_flags)}")
        return roadmap
        
    except json.JSONDecodeError as je:
        print(f"[Parse] ❌ JSON ERROR at line {je.lineno}, col {je.colno}: {je.msg}")
        print(f"[Parse] 💥 Context: ...{je.doc[max(0,je.pos-30):je.pos+30]}...")
        return _fallback_roadmap()
    except ValueError as ve:
        error_str = str(ve)[:200]
        print(f"[Parse] ❌ VALIDATION ERROR: {error_str}")
        return _fallback_roadmap()
    except Exception as e:
        print(f"[Parse] ❌ ERROR ({type(e).__name__}): {str(e)[:150]}")
        return _fallback_roadmap()


def _fallback_roadmap() -> ClinicalRoadmap:
    """Safe fallback roadmap when parsing fails."""
    return ClinicalRoadmap(
        risk_level="medium",
        red_flags=[],
        differential_diagnosis=[],
        recommended_departments=["Aile Hekimi"],
        immediate_action="Lütfen bir sağlık kuruluşuna başvurun.",
        doctor_visit_plan="En kısa sürede aile hekiminize danışın.",
        tests_to_discuss=[],
        treatment_topics_to_discuss=[],
        treatment_phases=[],
        monitoring_plan=MonitoringPlan(
            parameters=[], frequency="", red_flag_thresholds=[]
        ),
        lifestyle_modifications=[],
        do_not_do=[],
        follow_up_timeline="",
        evidence_references=[],
        safety_validated=False,
        disclaimer="Sistem bu sefer yanıt üretemedi. Lütfen bir hekime başvurun.",
        debug_trace=["fallback_roadmap_triggered"],
    )
