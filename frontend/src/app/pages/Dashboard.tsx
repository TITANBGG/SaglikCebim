import { useEffect, useState } from "react";
import { Activity, FileCheck, FileText, ImageIcon, FlaskConical, Loader2, Search, UserCircle, TestTube2, ScanLine, CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { ReportRow } from "../components/ReportRow";
import { TopBar } from "../components/TopBar";
import { TrendChart } from "../components/TrendChart";
import { HealthChatBot } from "../components/HealthChatBot";
import { apiClient } from "../../api/client";

interface DashboardData {
  total_reports?: number;
  abnormal_count?: number;
  normal_count?: number;
  radiology_count?: number;
  recent_reports?: any[];
}

interface PatientSummary {
  has_profile: boolean;
  has_lab: boolean;
  has_radiology: boolean;
  completion_score: number;
  missing_modalities: string[];
  profile: { age?: string; gender?: string; height?: string; weight?: string; blood_type?: string };
  conditions_count: number;
  medications_count: number;
  allergies_count: number;
  last_lab_date?: string;
  last_radiology_date?: string;
  abnormal_lab_count: number;
}

const MODALITY_META: Record<string, { label: string; icon: React.ElementType; route: string }> = {
  anamnez:     { label: "Anamnez Profili",  icon: UserCircle,  route: "/anamnez"  },
  kan_tahlili: { label: "Kan Tahlili",      icon: TestTube2,   route: "/upload"   },
  radyoloji:   { label: "Radyoloji",        icon: ScanLine,    route: "/radiology" },
};

export function Dashboard({ onNavigate }: { onNavigate?: (route: string) => void }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [patientSummary, setPatientSummary] = useState<PatientSummary | null>(null);
  const [clinicalKeyQuery, setClinicalKeyQuery] = useState("pneumonia treatment guidelines");
  const [clinicalKeyResult, setClinicalKeyResult] = useState<{
    query?: string;
    results_count?: number;
    sources?: string[];
    results?: Array<{ source?: string; title?: string; url?: string; level?: string; summary?: string }>;
  } | null>(null);
  const [clinicalKeyLoading, setClinicalKeyLoading] = useState(false);
  const [clinicalKeyError, setClinicalKeyError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setIsLoading(true);
        setError("");
        const [dashRes, summaryRes] = await Promise.allSettled([
          apiClient.getDashboardMonitoring(),
          apiClient.getPatientSummary(),
        ]);
        if (dashRes.status === "fulfilled") setData(dashRes.value);
        if (summaryRes.status === "fulfilled") setPatientSummary(summaryRes.value);
      } catch (err: any) {
        console.error("Dashboard load error:", err);
        setError("Dashboard yüklenemedi. Lütfen sayfayı yenileyin.");
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const handleClinicalKeyTest = async () => {
    if (!clinicalKeyQuery.trim() || clinicalKeyLoading) {
      return;
    }

    try {
      setClinicalKeyLoading(true);
      setClinicalKeyError("");
      setClinicalKeyResult(null);
      const response = await apiClient.testClinicalKey(clinicalKeyQuery.trim());
      setClinicalKeyResult(response);
    } catch (err: any) {
      console.error("ClinicalKey test error:", err);
      setClinicalKeyError(
        err?.response?.data?.detail || err?.message || "ClinicalKey testi başarısız oldu."
      );
    } finally {
      setClinicalKeyLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="p-6">
          <div className="h-8 bg-muted/30 rounded-lg w-48 mb-4 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-muted/30 rounded-lg animate-pulse"></div>
            ))}
          </div>
          <div className="h-64 bg-muted/30 rounded-lg animate-pulse"></div>
        </div>
      </div>
    );
  }

  const totalReports = data?.total_reports || 0;
  const abnormalCount = data?.abnormal_count || 0;
  const normalCount = data?.normal_count || 0;
  const radiologyCount = data?.radiology_count || 0;

  return (
    <>
      <TopBar
        title="Sağlık Analiz Paneli"
        subtitle="PDF tahliller, grafikler ve radyoloji sonuçları tek ekranda."
      />

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          {error}
        </div>
      )}

      {/* ── Veri Tamamlanma Kartı ───────────────────────────────────────── */}
      {patientSummary && (
        <div className="mb-8 bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex flex-col lg:flex-row lg:items-center gap-6">

            {/* Sol: progress ring + skor */}
            <div className="flex items-center gap-5 flex-shrink-0">
              <div className="relative w-20 h-20">
                <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="34" fill="none" stroke="currentColor"
                    className="text-muted/20" strokeWidth="8" />
                  <circle cx="40" cy="40" r="34" fill="none"
                    stroke={patientSummary.completion_score === 100 ? "#22c55e"
                      : patientSummary.completion_score >= 67 ? "#3b82f6"
                      : patientSummary.completion_score >= 34 ? "#f59e0b" : "#ef4444"}
                    strokeWidth="8"
                    strokeDasharray={`${2 * Math.PI * 34}`}
                    strokeDashoffset={`${2 * Math.PI * 34 * (1 - patientSummary.completion_score / 100)}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-bold text-foreground">
                    {patientSummary.completion_score}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground">Veri Tamamlanma</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {patientSummary.completion_score === 100
                    ? "Tüm modüller dolu"
                    : `${patientSummary.missing_modalities.length} modül eksik`}
                </p>
                {patientSummary.abnormal_lab_count > 0 && (
                  <span className="inline-flex items-center gap-1 mt-1.5 text-[11px] font-medium bg-destructive/10 text-destructive px-2 py-0.5 rounded-full">
                    <AlertCircle className="w-3 h-3" />
                    {patientSummary.abnormal_lab_count} anormal tahlil
                  </span>
                )}
              </div>
            </div>

            {/* Sağ: modalite satırları */}
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-3">
              {(["anamnez", "kan_tahlili", "radyoloji"] as const).map((key) => {
                const meta = MODALITY_META[key];
                const Icon = meta.icon;
                const done = key === "anamnez" ? patientSummary.has_profile
                  : key === "kan_tahlili" ? patientSummary.has_lab
                  : patientSummary.has_radiology;
                return (
                  <button
                    key={key}
                    onClick={() => onNavigate?.(meta.route)}
                    className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-colors ${
                      done
                        ? "border-success/20 bg-success/5 cursor-default"
                        : "border-warning/30 bg-warning/5 hover:bg-warning/10"
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      done ? "bg-success/15 text-success" : "bg-warning/15 text-warning"
                    }`}>
                      {done ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-foreground truncate">{meta.label}</p>
                      <p className={`text-[11px] ${done ? "text-success" : "text-warning"}`}>
                        {done ? "Tamamlandı" : "Eksik — Ekle"}
                      </p>
                    </div>
                    {!done && <ArrowRight className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={FileText}
          label="Analiz Edilen PDF"
          value={totalReports.toString()}
          trend={{ value: "12%", positive: true }}
          iconColor="text-primary"
        />
        <MetricCard
          icon={Activity}
          label="Anormal Bulgu"
          value={abnormalCount.toString()}
          trend={{ value: "3%", positive: false }}
          iconColor="text-warning"
        />
        <MetricCard
          icon={FileCheck}
          label="Normal Sonuç"
          value={normalCount.toString()}
          trend={{ value: "8%", positive: true }}
          iconColor="text-success"
        />
        <MetricCard
          icon={ImageIcon}
          label="X-Ray Analizi"
          value={radiologyCount.toString()}
          trend={{ value: "5%", positive: true }}
          iconColor="text-info"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-foreground mb-1">Analiz Edilen Raporlar</h3>
            <p className="text-sm text-muted-foreground">Son yüklenen dosyalar</p>
          </div>

          <div className="space-y-3">
            {data?.recent_reports && data.recent_reports.length > 0 ? (
              data.recent_reports.map((report, idx) => (
                <ReportRow
                  key={idx}
                  fileName={report.file_name || `Report ${idx + 1}`}
                  status={report.status || "pending"}
                  date={report.date || new Date().toLocaleDateString("tr-TR")}
                  type={report.type || "pdf"}
                />
              ))
            ) : (
              <>
                <ReportRow
                  fileName="e-Nabiz Kan Tahlili.pdf"
                  status="analyzed"
                  date="28 Nisan 2026"
                  type="pdf"
                />
                <ReportRow
                  fileName="Check-up Sonuçları.pdf"
                  status="parsed"
                  date="27 Nisan 2026"
                  type="pdf"
                />
                <ReportRow
                  fileName="Radyoloji X-Ray.png"
                  status="reviewed"
                  date="26 Nisan 2026"
                  type="image"
                />
                <ReportRow
                  fileName="Hormon Panel Raporu.pdf"
                  status="analyzed"
                  date="25 Nisan 2026"
                  type="pdf"
                />
                <ReportRow
                  fileName="Göğüs Röntgeni.png"
                  status="reviewed"
                  date="24 Nisan 2026"
                  type="image"
                />
              </>
            )}
          </div>
        </div>

        <TrendChart />
      </div>

      <div className="mt-8 bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <h3 className="text-lg font-bold text-foreground mb-1">ClinicalKey Test Alanı</h3>
            <p className="text-sm text-muted-foreground">
              Buradan backend&apos;deki evidence endpoint&apos;ini çalıştırıp sonuçları görebilirsiniz.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/40 border border-border rounded-full px-3 py-2">
            <FlaskConical className="w-3.5 h-3.5 text-primary" />
            Live evidence test
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-3 mb-4">
          <div className="flex-1">
            <label className="block text-xs font-medium text-muted-foreground mb-2">
              Test sorgusu
            </label>
            <input
              type="text"
              value={clinicalKeyQuery}
              onChange={(e) => setClinicalKeyQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleClinicalKeyTest();
                }
              }}
              className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground outline-none transition-colors focus:border-primary"
              placeholder="Örn: pneumonia treatment guidelines"
            />
          </div>
          <div className="lg:self-end">
            <button
              type="button"
              onClick={handleClinicalKeyTest}
              disabled={clinicalKeyLoading}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {clinicalKeyLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Test Et
            </button>
          </div>
        </div>

        {clinicalKeyError && (
          <div className="mb-4 rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {clinicalKeyError}
          </div>
        )}

        {clinicalKeyResult && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="rounded-xl border border-border bg-background/60 p-4">
                <p className="text-xs text-muted-foreground mb-1">Sorgu</p>
                <p className="text-sm font-medium text-foreground break-words">
                  {clinicalKeyResult.query || clinicalKeyQuery}
                </p>
              </div>
              <div className="rounded-xl border border-border bg-background/60 p-4">
                <p className="text-xs text-muted-foreground mb-1">Sonuç sayısı</p>
                <p className="text-2xl font-bold text-foreground">
                  {clinicalKeyResult.results_count ?? 0}
                </p>
              </div>
              <div className="rounded-xl border border-border bg-background/60 p-4">
                <p className="text-xs text-muted-foreground mb-1">Kaynaklar</p>
                <p className="text-sm font-medium text-foreground break-words">
                  {clinicalKeyResult.sources?.join(", ") || "-"}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {(clinicalKeyResult.results || []).slice(0, 4).map((result, idx) => (
                <div key={idx} className="rounded-xl border border-border bg-background/60 p-4">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <p className="text-sm font-semibold text-foreground">{result.title || "Sonuç"}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {result.source || "Unknown source"}{result.level ? ` · ${result.level}` : ""}
                      </p>
                    </div>
                    {result.url && (
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:text-primary/80"
                      >
                        Aç
                      </a>
                    )}
                  </div>
                  {result.summary && (
                    <p className="text-sm text-muted-foreground leading-6">{result.summary}</p>
                  )}
                </div>
              ))}
              {(clinicalKeyResult.results || []).length === 0 && (
                <div className="rounded-xl border border-border bg-background/60 p-4 text-sm text-muted-foreground">
                  Sonuç döndü ama detay listesi boş.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Kişiye Özel Sağlık Asistanı Chatbot */}
      <HealthChatBot />
    </>
  );
}
