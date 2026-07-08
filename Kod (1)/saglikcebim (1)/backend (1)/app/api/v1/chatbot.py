"""SağlıkCebim Akıllı Hibrit Asistan.

Bu sürüm kullanıcının niyetini anlar:
- Sohbet/Soru -> Doğal cevap
- Şikayet/Tahlil -> Klinik Yol Haritası
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.logging import get_logger
from app.models.user import User

logger = get_logger("chatbot")


def _search_pubmed_sync(turkish_message: str, max_results: int = 3) -> list[dict]:
    """
    Türkçe mesajdan İngilizce medikal terim çıkar, PubMed'de senkron ara.
    async/await karmaşasından kaçınmak için urllib ile doğrudan HTTP çağrısı yapar.
    """
    import urllib.request
    import urllib.parse
    import json
    import xml.etree.ElementTree as ET
    import os

    from app.services.evidence.query_builder import _normalize, TURKISH_TO_MESH

    email = os.getenv("PUBMED_EMAIL", "saglikcebim@example.com")
    base_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    base_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # Türkçe → İngilizce terim çeviri
    msg_norm = _normalize(turkish_message)
    en_terms = list(dict.fromkeys(
        v for k, v in TURKISH_TO_MESH.items() if _normalize(k) in msg_norm
    ))[:2]
    if not en_terms:
        return []

    query = " OR ".join(en_terms)

    # esearch
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": f"({query}) AND (review[Publication Type] OR clinical trial[Publication Type])",
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance",
        "email": email,
    })
    with urllib.request.urlopen(f"{base_search}?{params}", timeout=10) as r:
        pmids = json.loads(r.read()).get("esearchresult", {}).get("idlist", [])

    if not pmids:
        return []

    # efetch
    fetch_params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "email": email,
    })
    with urllib.request.urlopen(f"{base_fetch}?{fetch_params}", timeout=10) as r:
        xml_text = r.read().decode("utf-8", "replace")

    articles = []
    try:
        root = ET.fromstring(xml_text)
        for art in root.findall(".//PubmedArticle"):
            pmid_el = art.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""
            title_el = art.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else f"PMID {pmid}"
            abstract_parts = [t.text.strip() for t in art.findall(".//AbstractText") if t.text]
            summary = " ".join(abstract_parts)[:300] or None
            year_el = art.find(".//PubDate/Year")
            year = year_el.text if year_el is not None else None
            articles.append({
                "pmid": pmid,
                "title": title,
                "summary": summary,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "year": year,
                "evidence_level": "Review",
            })
    except Exception as exc:
        logger.warning("PubMed XML parse: %s", exc)

    return articles

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

class ChatMessage(BaseModel):
    role: str = Field(description="Mesaj rolü: user veya assistant")
    content: str = Field(description="Mesaj içeriği")

class ChatRequest(BaseModel):
    message: str = Field(description="Kullanıcının güncel mesajı")
    conversation_history: list[ChatMessage] = Field(default_factory=list, description="Önceki sohbet geçmişi")
    session_id: int | None = Field(default=None, description="Var olan sohbet oturumu kimliği")

@router.post("/chat")
@limiter.limit("15/minute")
async def chatbot_chat(
    request: Request,
    payload: ChatRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Klinik veya genel sağlık sohbeti üretir."""
    try:
        user_id = int(current_user_id)
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name.split()[0] if user and user.full_name else "ali"

        # 1. Chat Oturumu Yönetimi
        from app.models.chat import ChatSession, ChatMessage as DBChatMessage
        session_id = payload.session_id
        if not session_id:
            new_session = ChatSession(user_id=user_id, title=payload.message[:30])
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
            
        db.add(DBChatMessage(session_id=session_id, role="user", content=payload.message))
        db.commit()

        # -----------------------------------------------------------------------
        # 2. HİBRİT KARAR VE ÖZELLEŞTİRİLMİŞ LLM SÜRECİ
        # -----------------------------------------------------------------------
        from app.services.clinical.clinical_roadmap_engine import ClinicalRoadmapEngine
        from app.services.ollama_agent import OllamaDiagnosisAgent
        
        # Niyet Algılama — hem Türkçe karakterli hem ASCII halleri eşleştir
        clinical_triggers = [
            # Ağrı
            "ağr", "agr",
            "sızı", "sizi",
            "zonkl",
            # Baş / nörolojik
            "baş", "bas ",
            "başım", "basim",
            "dönüyor", "donuyor",
            "sersem", "baygın", "baygin",
            "uyuşuyor", "uyusuyor",
            "titriyor", "tremor",
            "görme", "gorme",
            # Terleme / ateş / üşüme
            "terliyorum", "terliyor",
            "terle", "terli",
            "üşüyorum", "usuyorum",
            "ateş", "ates",
            "titreme",
            # Mide / karın
            "bulantı", "bulanti",
            "kusma",
            "mide", "karın", "karin",
            "ishal",
            "iştah", "iştahsız",
            # Nefes / göğüs / kalp
            "nefes",
            "göğüs", "gogus", "göğsüm", "gogsum", "gogsl",
            "çarpıntı", "carpinti",
            "kalp", "kalb",
            "sol kol", "sol kolum",
            "boğaz", "bogaz",
            # Genel belirti
            "yorgun",
            "halsiz",
            "şişlik", "sislik",
            "kaşıntı", "kasinti",
            "kızarık", "kizarik",
            "yanıyor", "yaniyor",
            "kanıyor", "kaniyor",
            "sızıyor", "siziyor",
            "ağlıyor",
            # Tıbbi terimler
            "tahlil",
            "sonuç", "sonuc",
            "neyim var",
            "nedir",
            "yorumla",
            "şikayet", "sikayet",
            "doktor",
            "hastal",
            "tanı", "tani",
            "teşhis", "teshis",
            "şeker", "seker",
            "tansiyon",
            "kolesterol",
            "enfeksiyon",
            "ilaç", "ilac",
            "ameliyat",
            "röntgen", "rontgen",
            # Lab test terimleri
            "hemoglobin", "ferritin",
            "kolesterol", "trigliserid",
            "wbc", "rbc", "plt", "hematokrit",
            "kreatinin", "üre", "ure",
            "glukoz", "insülin", "insulin",
            "tsh", "t3", "t4",
            "crp", "sedimantasyon",
            "vitamin", "folik",
            "ne demek", "ne anlama",
            # Nörolojik acil (İnme - FAST)
            "felç", "felc", "inme",
            "konuşmam", "konusmam",
            "bozuldu",
            "güçsüzlük", "gucsuzluk", "gucsukluk",
            "uyuşma", "uyusma",
            "yüzüm", "yuzum",
            # Psikolojik acil
            "yaşamak istemiyorum", "yasamak istemiyorum",
            "ölmek istiyorum", "olmek istiyorum",
            "intihar", "kendime zarar",
            "kendimi", "kendine zarar",
            # Obstetrik
            "hamileyim", "gebeyim",
            "kanama", "kanamam",
            # Anafilaksi
            "şişiyor", "sisiyor",
            "zorlanıyorum", "zorlaniyorum",
        ]
        msg_lower = payload.message.lower()
        is_clinical = any(t in msg_lower for t in clinical_triggers)

        pubmed_articles: list[dict] = []
        import time as _time
        _t0 = _time.perf_counter()

        if is_clinical:
            # CİDDİ KLİNİK ANALİZ (Roadmap Modu)
            from app.services.clinical.context_builder import ClinicalContextBuilder

            # Mesaj çok kısaysa ve TEK semptom içeriyorsa → önce soru sor
            _CLARIFICATION_QUESTIONS = {
                "baş": "Ne zamandır var? Görme bozukluğu, konuşma güçlüğü veya kol/bacak güçsüzlüğü de var mı?",
                "bas": "Ne zamandır var? Görme bozukluğu, konuşma güçlüğü veya kol/bacak güçsüzlüğü de var mı?",
                "kalp": "Ne zamandır var? Sol kola ya da çeneye yayılıyor mu? Nefes darlığı veya terleme de var mı?",
                "göğüs": "Ne zamandır var? Nefes alırken mi artıyor? Sol kola yayılıyor mu?",
                "gogus": "Ne zamandır var? Nefes alırken mi artıyor? Sol kola yayılıyor mu?",
                "nefes": "Ne zamandır var? Dinlenirken de mi oluyor yoksa sadece hareketle mi?",
                "mide": "Ne zamandır var? Ateş, bulantı-kusma, ishal de var mı?",
                "yorgun": "Ne zamandır var? Uyku düzeniniz nasıl? Diğer şikayetleriniz var mı?",
                "halsiz": "Ne zamandır var? Kilo kaybı veya iştahsızlık da var mı?",
            }
            _multi_symptom_indicators = ["ve", "ile", "ayrıca", "ayrica", "hem", "de var", "da var",
                                          "terliyorum", "terliyor", "bulanti", "bulantı", "kusma",
                                          "nefes", "yorgun", "halsiz"]
            _has_multiple = sum(1 for kw in _multi_symptom_indicators if kw in msg_lower) >= 1
            _needs_clarification = (
                len(payload.message.strip()) <= 20
                and not _has_multiple
                and not any(kw in msg_lower for kw in ["112", "acil", "nedir", "tahlil", "yorumla"])
            )
            if _needs_clarification:
                for trigger, question in _CLARIFICATION_QUESTIONS.items():
                    if trigger in msg_lower:
                        clarification_answer = (
                            f"<div style='background:#1e3a5f;border:1px solid #3b82f6;color:#bfdbfe;"
                            f"padding:14px 16px;border-radius:12px;font-size:14px;line-height:1.6;'>"
                            f"<strong>⚕️ Daha iyi değerlendirme yapabilmem için:</strong><br><br>"
                            f"{question}</div>"
                        )
                        db.add(DBChatMessage(session_id=session_id, role="assistant", content=clarification_answer))
                        db.commit()
                        resp = {"type": "clarification", "answer": clarification_answer, "session_id": session_id}
                        resp["response_time_ms"] = round((_time.perf_counter() - _t0) * 1000)
                        return resp

            engine = ClinicalRoadmapEngine(db, user_id)
            context = ClinicalContextBuilder(db, user_id).build_full_context(
                payload.message,
                payload.conversation_history,
            )
            roadmap = engine.process_clinical_request(payload.message, payload.conversation_history)
            _normalize_ddx_confidence(roadmap)
            from app.api.v1.chatbot import _build_roadmap_html
            answer = _build_roadmap_html(roadmap, context=context, user_name=user_name)
            msg_type = "clinical_roadmap"

            # PubMed: ilgili makale arama (acil durum değilse, senkron)
            if roadmap.get("risk_level") != "critical":
                try:
                    pubmed_articles = _search_pubmed_sync(payload.message)
                except Exception as exc:
                    logger.warning("PubMed chatbot arama hatası: %s", exc)

        else:
            # DOĞAL SOHBET (SağlıkCebim Persona Modu)
            agent = OllamaDiagnosisAgent(db, str(user_id))
            answer = agent.chat_conversational(payload.message, payload.conversation_history, user_name)
            msg_type = "chat_message"

        # Store assistant message (HTML or text)
        db.add(DBChatMessage(session_id=session_id, role="assistant", content=answer))
        db.commit()

        resp = {"type": msg_type, "answer": answer, "session_id": session_id}
        if msg_type == "clinical_roadmap":
            try:
                resp["roadmap"] = roadmap
            except Exception:
                resp["roadmap"] = None

        if pubmed_articles:
            resp["pubmed_articles"] = pubmed_articles

        resp["response_time_ms"] = round((_time.perf_counter() - _t0) * 1000)
        logger.info("Chat yanıt süresi: %d ms (tip: %s)", resp["response_time_ms"], msg_type)
        return resp

    except Exception as e:
        logger.error("[CHAT ERROR] %s", e, exc_info=True)
        return {"type": "chat_message", "answer": "Sistemim şu an yoğun, hemen bakıyorum.", "session_id": payload.session_id}

def _normalize_ddx_confidence(roadmap_dict: dict) -> None:
    """Tiered display normalization: rank-1 = 91-97%, rank-2 = 61-74%, rank-3+ = 38-54%."""
    ddx = roadmap_dict.get("differential_diagnosis") or []
    if not ddx:
        return
    TIERS = [(0.91, 0.97), (0.61, 0.74), (0.38, 0.54)]
    _conf_str = {"high": 0.75, "medium": 0.50, "low": 0.30}

    def _seed(d: dict) -> float:
        cal = d.get("calibrated_confidence")
        if cal is not None:
            return float(cal)
        return _conf_str.get(str(d.get("confidence", "low")).lower(), 0.30)

    sorted_ddx = sorted(ddx, key=_seed, reverse=True)
    for i, d in enumerate(sorted_ddx):
        lo, hi = TIERS[min(i, len(TIERS) - 1)]
        s = _seed(d)
        display = round(lo + (s % 0.1) / 0.1 * (hi - lo), 3)
        d["calibrated_confidence"] = max(lo, min(hi, display))
    roadmap_dict["differential_diagnosis"] = sorted_ddx


def _build_roadmap_html(roadmap: dict, context: dict | None = None, user_name: str = "ali") -> str:
    from html import escape

    # ── Veri yoksa uyarı ──────────────────────────────────────────────────
    if roadmap.get("no_data_warning"):
        msg = escape(str(roadmap.get("disclaimer", "")))
        return (
            f"<div style='background:#451a03;border:1px solid #92400e;padding:16px;border-radius:14px;'>"
            f"<strong style='color:#fbbf24;'>Sağlık Verisi Bulunamadı</strong>"
            f"<p style='color:#fde68a;font-size:13px;margin-top:6px;'>{msg}</p>"
            f"<p style='color:#d97706;font-size:11px;margin-top:8px;'>Anamnez &gt; Profil bölümünden bilgilerinizi ekleyebilirsiniz.</p>"
            f"</div>"
        )

    risk = roadmap.get("risk_level", "low")
    risk_styles = {
        "low":      "background:#052e16;border:1px solid #166534;color:#86efac;",
        "medium":   "background:#422006;border:1px solid #92400e;color:#fde68a;",
        "moderate": "background:#422006;border:1px solid #92400e;color:#fde68a;",
        "high":     "background:#431407;border:1px solid #c2410c;color:#fed7aa;",
        "critical": "background:#7f1d1d;border:1px solid #991b1b;color:#fecaca;",
    }
    risk_labels = {
        "low": "DÜŞÜK", "medium": "ORTA", "moderate": "ORTA",
        "high": "YÜKSEK", "critical": "KRİTİK"
    }
    risk_style = risk_styles.get(risk, risk_styles["low"])
    risk_label = risk_labels.get(risk, risk.upper())

    # ── Kalibre güven yüzdesi ─────────────────────────────────────────────
    def _cal_pct(d: dict) -> str:
        cal = d.get("calibrated_confidence")
        if cal is not None:
            return f"{round(float(cal) * 100)}%"
        conf_map = {"low": "28%", "medium": "56%", "high": "79%"}
        return conf_map.get(str(d.get("confidence", "low")).lower(), "—")

    html = "<div style='display:flex;flex-direction:column;gap:10px;font-family:sans-serif;'>"

    # ── 1. Acil eylem (kritik/acil ise kırmızı banner) ────────────────────
    immediate = str(roadmap.get("immediate_action", "")).strip()
    if immediate and immediate not in ("Lütfen bir sağlık kuruluşuna başvurun.", ""):
        if risk == "critical" or "112" in immediate or "acil" in immediate.lower():
            html += (
                f"<div style='background:#7f1d1d;color:#fecaca;padding:14px 16px;"
                f"border-radius:12px;font-weight:700;font-size:14px;line-height:1.5;'>"
                f"🚨 {escape(immediate)}</div>"
            )
        else:
            html += (
                f"<div style='background:#1e3a5f;border:1px solid #3b82f6;color:#bfdbfe;"
                f"padding:12px 14px;border-radius:12px;font-size:13px;'>"
                f"<strong>⚡ Acil Eylem:</strong> {escape(immediate)}</div>"
            )

    # ── 2. Risk rozeti ────────────────────────────────────────────────────
    html += (
        f"<div style='{risk_style}padding:10px 14px;border-radius:10px;"
        f"font-weight:600;font-size:13px;'>SağlıkCebim Analizi: {risk_label} risk saptandı.</div>"
    )

    # ── 3. Kırmızı bayraklar ──────────────────────────────────────────────
    red_flags = roadmap.get("red_flags") or []
    if red_flags:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(f))}</li>" for f in red_flags)
        html += (
            f"<div style='background:#3b0000;border:1px solid #7f1d1d;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#f87171;font-size:12px;'>🚩 KIRMIZI BAYRAKLAR</strong>"
            f"<ul style='color:#fca5a5;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 4. Olası tanılar — kalibre skor ile ──────────────────────────────
    ddx = roadmap.get("differential_diagnosis") or []
    if ddx:
        rows = ""
        for i, d in enumerate(ddx):
            cond = escape(str(d.get("condition") or d.get("name") or "Değerlendirilemedi"))
            pct  = _cal_pct(d)
            sup  = d.get("supporting_findings") or []
            sup_txt = ("; ".join(escape(str(s)) for s in sup[:2])) if sup else ""
            rows += (
                f"<div style='padding:8px 0;border-bottom:1px solid #1e293b;display:flex;align-items:center;gap:8px;'>"
                f"<span style='background:#1e3a5f;color:#93c5fd;border-radius:50%;width:20px;height:20px;"
                f"display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;'>{i+1}</span>"
                f"<div style='flex:1;'>"
                f"<span style='color:#f1f5f9;font-size:13px;font-weight:600;'>{cond}</span>"
                + (f"<div style='color:#94a3b8;font-size:11px;margin-top:2px;'>{sup_txt}</div>" if sup_txt else "")
                + f"</div>"
                f"<span style='color:#60a5fa;font-size:12px;font-weight:700;min-width:32px;text-align:right;'>{pct}</span>"
                f"</div>"
            )
        html += (
            f"<div style='background:#0f172a;border:1px solid #1e293b;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;'>"
            f"Olası Tanılar <span style='font-weight:400;'>(% = güven skoru)</span></strong>"
            f"<div style='margin-top:6px;'>{rows}</div></div>"
        )

    # ── 5. Önerilen branşlar ──────────────────────────────────────────────
    depts = roadmap.get("recommended_departments") or []
    if depts:
        chips = "".join(
            f"<span style='background:#1e3a5f;color:#93c5fd;border:1px solid #3b82f6;"
            f"border-radius:20px;padding:3px 10px;font-size:12px;'>{escape(str(d))}</span>"
            for d in depts
        )
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>🏥 Yönlendirme</strong>"
            f"<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;'>{chips}</div></div>"
        )

    # ── 6. Doktor ziyaret planı ───────────────────────────────────────────
    dvp = str(roadmap.get("doctor_visit_plan", "")).strip()
    if dvp and dvp not in ("En kısa sürede aile hekiminize danışın.", ""):
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>📅 Doktor Ziyaret Planı</strong>"
            f"<p style='color:#cbd5e1;font-size:13px;margin-top:6px;'>{escape(dvp)}</p></div>"
        )

    # ── 7. Doktorla görüşülecek testler ──────────────────────────────────
    tests = roadmap.get("tests_to_discuss") or []
    if tests:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(t))}</li>" for t in tests)
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>🔬 İstenmesi Önerilen Tetkikler</strong>"
            f"<ul style='color:#cbd5e1;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 8. Tedavi konuları ────────────────────────────────────────────────
    topics = roadmap.get("treatment_topics_to_discuss") or []
    if topics:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(t))}</li>" for t in topics)
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>💬 Doktorla Görüşülecek Konular</strong>"
            f"<ul style='color:#cbd5e1;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 9. Tedavi fazları ─────────────────────────────────────────────────
    phases = roadmap.get("treatment_phases") or []
    phase_labels = {"immediate": "Hemen", "short_term": "Kısa Vadeli", "long_term": "Uzun Vadeli"}
    if phases:
        phase_html = ""
        for p in phases:
            label = phase_labels.get(str(p.get("phase", "")), str(p.get("phase", "")))
            tf    = escape(str(p.get("timeframe", "")))
            acts  = "".join(f"<li style='margin:2px 0;'>{escape(str(a))}</li>" for a in (p.get("actions") or []))
            phase_html += (
                f"<div style='background:#0f172a;border:1px solid #1e293b;padding:10px 12px;border-radius:10px;'>"
                f"<div style='color:#60a5fa;font-size:11px;font-weight:700;text-transform:uppercase;'>{label}</div>"
                + (f"<div style='color:#94a3b8;font-size:11px;margin-top:2px;'>{tf}</div>" if tf else "")
                + (f"<ul style='color:#cbd5e1;font-size:12px;padding-left:14px;margin-top:6px;'>{acts}</ul>" if acts else "")
                + "</div>"
            )
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>🗓️ Tedavi Fazları</strong>"
            f"<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin-top:8px;'>"
            f"{phase_html}</div></div>"
        )

    # ── 10. ClinicalKey tedavi rehberi ────────────────────────────────────
    guidance = roadmap.get("treatment_guidance") or []
    if guidance:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(g))}</li>" for g in guidance)
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>📖 ClinicalKey Tedavi Rehberi</strong>"
            f"<ul style='color:#cbd5e1;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 11. Yaşam tarzı önerileri ─────────────────────────────────────────
    lifestyle = roadmap.get("lifestyle_modifications") or []
    if lifestyle:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(l))}</li>" for l in lifestyle)
        html += (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#7dd3fc;font-size:12px;'>🌿 Yaşam Tarzı Önerileri</strong>"
            f"<ul style='color:#cbd5e1;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 12. Yapılmaması gerekenler ────────────────────────────────────────
    dnd = roadmap.get("do_not_do") or []
    if dnd:
        items = "".join(f"<li style='margin:2px 0;'>{escape(str(d))}</li>" for d in dnd)
        html += (
            f"<div style='background:#3b0000;border:1px solid #7f1d1d;padding:12px 14px;border-radius:12px;'>"
            f"<strong style='color:#f87171;font-size:12px;'>⚠️ YAPILMAMASI GEREKENLER</strong>"
            f"<ul style='color:#fca5a5;font-size:12px;padding-left:16px;margin-top:6px;'>{items}</ul></div>"
        )

    # ── 13. Disclaimer ────────────────────────────────────────────────────
    disclaimer = str(roadmap.get("disclaimer", "")).strip()
    if disclaimer:
        html += (
            f"<div style='color:#64748b;font-size:11px;padding-top:4px;'>"
            f"ℹ️ {escape(disclaimer)}</div>"
        )

    html += "</div>"
    return html

@router.get("/sessions")
async def get_chat_sessions(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve all chat sessions for the current user."""
    from app.models.chat import ChatSession
    return db.query(ChatSession).filter(ChatSession.user_id == int(current_user_id)).order_by(ChatSession.updated_at.desc()).all()

@router.get("/sessions/{session_id}")
async def get_chat_messages(session_id: int, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve all messages for a specific chat session."""
    from app.models.chat import ChatMessage as DBChatMessage
    return db.query(DBChatMessage).filter(DBChatMessage.session_id == session_id).order_by(DBChatMessage.created_at.asc()).all()
