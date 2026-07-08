import React, { useState } from "react";
import {
  AlertTriangle, ShieldCheck, ShieldAlert, Info,
  ChevronDown, ChevronUp, ExternalLink, Stethoscope,
  FlaskConical, BookOpen, Ban, Clock
} from "lucide-react";
import { ClinicalRoadmap, DDxItem, RiskLevel } from "../types/roadmap";

// ── Risk renk / ikon yardımcıları ──────────────────────────────────────────

const RISK_CONFIG: Record<RiskLevel, { label: string; color: string; bg: string; Icon: React.ElementType }> = {
  low:      { label: "Düşük Risk",    color: "text-emerald-400", bg: "bg-emerald-400/10 border-emerald-400/20", Icon: ShieldCheck  },
  medium:   { label: "Orta Risk",     color: "text-amber-400",   bg: "bg-amber-400/10  border-amber-400/20",   Icon: ShieldAlert  },
  high:     { label: "Yüksek Risk",   color: "text-orange-400",  bg: "bg-orange-400/10 border-orange-400/20",  Icon: AlertTriangle },
  critical: { label: "Kritik Risk",   color: "text-red-500",     bg: "bg-red-500/10    border-red-500/20",     Icon: AlertTriangle },
};

const PHASE_LABEL: Record<string, string> = {
  immediate:  "Hemen",
  short_term: "Kısa Vadeli",
  long_term:  "Uzun Vadeli",
};

// ── Kalibre güven bar'ı ───────────────────────────────────────────────────

function ConfidenceBar({ item }: { item: DDxItem }) {
  const cal = item.calibrated_confidence;
  const raw = item.raw_confidence;

  if (cal == null) {
    // Kalibrasyon yoksa salt etiket göster
    const labelColor =
      item.confidence === "high"   ? "text-emerald-400" :
      item.confidence === "medium" ? "text-amber-400"   : "text-muted-foreground";
    return <span className={`text-xs font-medium ${labelColor}`}>{item.confidence}</span>;
  }

  const pct = Math.round(cal * 100);
  const barColor =
    pct >= 70 ? "bg-emerald-500" :
    pct >= 45 ? "bg-amber-500"   : "bg-slate-500";

  return (
    <div className="flex items-center gap-2 min-w-[100px]">
      <div className="flex-1 h-1.5 bg-muted/30 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-foreground tabular-nums w-8 text-right">{pct}%</span>
      {raw != null && (
        <span className="text-[10px] text-muted-foreground/60" title="Ham LLM skoru">
          ({Math.round(raw * 100)}%)
        </span>
      )}
    </div>
  );
}

// ── DDx satırı ────────────────────────────────────────────────────────────

function DdxRow({ item, idx }: { item: DDxItem; idx: number }) {
  const [open, setOpen] = useState(false);
  const hasDetail =
    item.supporting_findings.length > 0 ||
    item.against_findings.length > 0 ||
    item.missing_information.length > 0;

  return (
    <div className="border border-border rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-surface/50 transition-colors"
        onClick={() => hasDetail && setOpen(!open)}
      >
        <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold flex-shrink-0">
          {idx + 1}
        </span>
        <span className="flex-1 text-sm font-medium text-foreground">{item.condition}</span>
        <ConfidenceBar item={item} />
        {hasDetail && (
          open ? <ChevronUp className="w-4 h-4 text-muted-foreground flex-shrink-0" />
               : <ChevronDown className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        )}
      </button>

      {open && hasDetail && (
        <div className="px-4 pb-4 space-y-2 border-t border-border bg-surface/30">
          {item.supporting_findings.length > 0 && (
            <div className="pt-3">
              <p className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wide mb-1">Destekleyen Bulgular</p>
              <ul className="space-y-0.5">
                {item.supporting_findings.map((f, i) => (
                  <li key={i} className="text-xs text-foreground/80 flex gap-1.5"><span className="text-emerald-400 mt-0.5">+</span>{f}</li>
                ))}
              </ul>
            </div>
          )}
          {item.against_findings.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold text-destructive uppercase tracking-wide mb-1">Zayıflatan Bulgular</p>
              <ul className="space-y-0.5">
                {item.against_findings.map((f, i) => (
                  <li key={i} className="text-xs text-foreground/80 flex gap-1.5"><span className="text-destructive mt-0.5">−</span>{f}</li>
                ))}
              </ul>
            </div>
          )}
          {item.missing_information.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold text-amber-400 uppercase tracking-wide mb-1">Eksik Bilgi</p>
              <ul className="space-y-0.5">
                {item.missing_information.map((f, i) => (
                  <li key={i} className="text-xs text-foreground/80 flex gap-1.5"><span className="text-amber-400 mt-0.5">?</span>{f}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Ana kart ──────────────────────────────────────────────────────────────

interface Props {
  roadmap: ClinicalRoadmap;
}

export const ClinicalRoadmapCard: React.FC<Props> = ({ roadmap }) => {
  const riskCfg = RISK_CONFIG[roadmap.risk_level] ?? RISK_CONFIG.medium;
  const RiskIcon = riskCfg.Icon;

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-lg space-y-0">

      {/* ── Başlık / Risk ── */}
      <div className={`flex items-center gap-3 px-5 py-4 border-b border-border ${riskCfg.bg} border`}>
        <RiskIcon className={`w-5 h-5 ${riskCfg.color} flex-shrink-0`} />
        <div className="flex-1">
          <p className="text-sm font-bold text-foreground">Klinik Yol Haritası</p>
          <p className={`text-xs font-medium ${riskCfg.color}`}>{riskCfg.label}</p>
        </div>
        {!roadmap.safety_validated && (
          <span className="text-[10px] bg-destructive/10 text-destructive border border-destructive/20 rounded-full px-2 py-0.5">
            Güvenlik Uyarısı
          </span>
        )}
      </div>

      <div className="p-5 space-y-5">

        {/* ── Red Flags ── */}
        {roadmap.red_flags.length > 0 && (
          <div className="rounded-xl bg-destructive/8 border border-destructive/20 px-4 py-3">
            <p className="text-xs font-semibold text-destructive uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" /> Kırmızı Bayraklar
            </p>
            <ul className="space-y-1">
              {roadmap.red_flags.map((f, i) => (
                <li key={i} className="text-sm text-foreground/90">{f}</li>
              ))}
            </ul>
          </div>
        )}

        {/* ── Acil Eylem ── */}
        {roadmap.immediate_action && (
          <div className="rounded-xl bg-primary/6 border border-primary/20 px-4 py-3">
            <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-1 flex items-center gap-1.5">
              <Stethoscope className="w-3.5 h-3.5" /> Acil Eylem
            </p>
            <p className="text-sm text-foreground/90">{roadmap.immediate_action}</p>
          </div>
        )}

        {/* ── DDx — kalibre skor bar ile ── */}
        {roadmap.differential_diagnosis.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <FlaskConical className="w-3.5 h-3.5" /> Olası Tanılar
              <span className="text-[10px] normal-case text-muted-foreground/50 font-normal ml-1">
                (% = güven skoru)
              </span>
            </p>
            <div className="space-y-2">
              {roadmap.differential_diagnosis.map((d, i) => (
                <DdxRow key={i} item={d} idx={i} />
              ))}
            </div>
          </div>
        )}

        {/* ── Önerilen Bölümler ── */}
        {roadmap.recommended_departments.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Yönlendirme</p>
            <div className="flex flex-wrap gap-2">
              {roadmap.recommended_departments.map((d, i) => (
                <span key={i} className="text-xs bg-primary/10 text-primary border border-primary/20 rounded-full px-3 py-1">
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Tedavi Fazları ── */}
        {roadmap.treatment_phases.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" /> Tedavi Fazları
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {roadmap.treatment_phases.map((p, i) => (
                <div key={i} className="rounded-xl border border-border bg-surface/40 p-3">
                  <p className="text-[11px] font-semibold text-primary uppercase mb-1">{PHASE_LABEL[p.phase] ?? p.phase}</p>
                  <p className="text-xs text-muted-foreground mb-2">{p.timeframe}</p>
                  <ul className="space-y-1">
                    {p.actions.map((a, j) => (
                      <li key={j} className="text-xs text-foreground/80 flex gap-1.5">
                        <span className="text-primary mt-0.5 flex-shrink-0">•</span>{a}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── ClinicalKey Tedavi Rehberi ── */}
        {roadmap.treatment_guidance && roadmap.treatment_guidance.length > 0 && (
          <div className="rounded-xl bg-surface/40 border border-border px-4 py-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> ClinicalKey Tedavi Rehberi
            </p>
            <ul className="space-y-1">
              {roadmap.treatment_guidance.map((g, i) => (
                <li key={i} className="text-xs text-foreground/80">{g}</li>
              ))}
            </ul>
          </div>
        )}

        {/* ── Kanıt Referansları ── */}
        {roadmap.evidence_references.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> Kanıt Kaynakları
            </p>
            <div className="space-y-1.5">
              {roadmap.evidence_references.slice(0, 5).map((r, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-[10px] bg-muted/40 text-muted-foreground rounded px-1.5 py-0.5 flex-shrink-0 mt-0.5">
                    {r.source}
                  </span>
                  <div className="flex-1 min-w-0">
                    {r.url ? (
                      <a href={r.url} target="_blank" rel="noreferrer"
                        className="text-xs text-primary hover:underline flex items-center gap-1 truncate">
                        {r.title} <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                    ) : (
                      <p className="text-xs text-foreground/80 truncate">{r.title}</p>
                    )}
                    {r.year && <span className="text-[10px] text-muted-foreground">{r.year}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Yapılmaması Gerekenler ── */}
        {roadmap.do_not_do.length > 0 && (
          <div className="rounded-xl bg-amber-400/8 border border-amber-400/20 px-4 py-3">
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Ban className="w-3.5 h-3.5" /> Yapılmaması Gerekenler
            </p>
            <ul className="space-y-1">
              {roadmap.do_not_do.map((d, i) => (
                <li key={i} className="text-xs text-foreground/80 flex gap-1.5">
                  <span className="text-amber-400 flex-shrink-0 mt-0.5">✕</span>{d}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* ── Disclaimer ── */}
        {roadmap.disclaimer && (
          <div className="flex gap-2 pt-1">
            <Info className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />
            <p className="text-[11px] text-muted-foreground leading-relaxed">{roadmap.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClinicalRoadmapCard;
