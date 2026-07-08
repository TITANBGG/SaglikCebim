import { useEffect, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, Download, Eye, FileText, Loader2, RefreshCw, Upload, XCircle } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";
import { HealthChatBot } from "../components/HealthChatBot";
import { apiClient } from "../../api/client";

interface AnalysisResult {
  id: string;
  file_name?: string;
  filename?: string;
  original_filename?: string;
  status: "pending" | "processing" | "parsed" | "analyzed" | "uploaded" | "error";
  total_tests?: number;
  created_at?: string;
  date?: string;
  type?: string;
}

interface ReportDetailResponse {
  report_id: string;
  filename: string;
  status: string;
  total_tests: number;
  results: Array<{
    test_name: string;
    original_name?: string;
    value: number;
    unit?: string;
    ref_min?: number | null;
    ref_max?: number | null;
    status: string;
    created_at?: string | null;
  }>;
}

export function PDFAnaliz() {
  const [files, setFiles] = useState<AnalysisResult[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [reportDetail, setReportDetail] = useState<ReportDetailResponse | null>(null);
  const [recommendations, setRecommendations] = useState<Record<string, any> | null>(null);
  const [pubmedArticles, setPubmedArticles] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setIsLoading(true);
      setError("");
      const response = await apiClient.listReports();
      setFiles(Array.isArray(response) ? response : response.reports || []);
    } catch (err: any) {
      console.error("Failed to load reports:", err);
      setError("Raporlar yüklenemedi");
    } finally {
      setIsLoading(false);
    }
  };

  const loadReportDetails = async (reportId: string) => {
    try {
      setSelectedReportId(reportId);
      setIsDetailLoading(true);
      setError("");

      const [detail, recs, pubmed] = await Promise.all([
        apiClient.getReportResults(reportId),
        apiClient.getReportRecommendations(reportId),
        apiClient.getReportPubmed(reportId),
      ]);

      setReportDetail(detail);
      setRecommendations(recs?.data || {});
      setPubmedArticles(pubmed?.articles || []);
    } catch (err: any) {
      console.error("Failed to load report details:", err);
      setError(err.response?.data?.detail || "Rapor detayları yüklenemedi");
      setReportDetail(null);
      setRecommendations(null);
      setPubmedArticles([]);
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleParseSelected = async () => {
    if (!selectedReportId) return;
    try {
      setIsDetailLoading(true);
      await apiClient.parseReport(selectedReportId);
      await loadReportDetails(selectedReportId);
      await loadReports();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Analiz başlatılamadı");
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedReportId) return;
    try {
      const blob = await apiClient.downloadReportPdf(selectedReportId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `report_${selectedReportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || "PDF indirilemedi");
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles && droppedFiles.length > 0) {
      await uploadFiles(droppedFiles);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFiles(e.target.files);
    }
  };

  const uploadFiles = async (filesToUpload: FileList) => {
    try {
      setIsUploading(true);
      setError("");

      for (let i = 0; i < filesToUpload.length; i++) {
        const file = filesToUpload[i];

        if (file.size > 10 * 1024 * 1024) {
          setError("Dosya boyutu 10MB'dan az olmalıdır");
          continue;
        }

        const formData = new FormData();
        formData.append("file", file);
        const uploadResponse = await apiClient.uploadReport(formData);
        const uploadedReportId = uploadResponse?.report_id || uploadResponse?.id;

        if (uploadedReportId && file.name.toLowerCase().endsWith(".pdf")) {
          await apiClient.parseReport(uploadedReportId);
          setSelectedReportId(uploadedReportId);
          await loadReportDetails(uploadedReportId);
        }
      }

      await loadReports();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Dosya yükleme başarısız");
    } finally {
      setIsUploading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "analyzed":
      case "completed":
        return <CheckCircle2 className="w-4 h-4 text-success" />;
      case "processing":
      case "uploaded":
      case "pending":
        return <Clock className="w-4 h-4 text-warning" />;
      case "error":
        return <XCircle className="w-4 h-4 text-destructive" />;
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  return (
    <>
      <TopBar
        title="PDF Tahlil Analizi"
        subtitle="Raporları yükleyin, analiz sonuçlarını ve önerileri görüntüleyin."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Dosya Yükleme</h3>

          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
              dragActive
                ? "border-primary bg-primary/5"
                : "border-border-strong hover:border-primary/50 hover:bg-primary/5"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <p className="text-foreground font-medium mb-2">PDF veya görüntü dosyanızı yükleyin</p>
            <p className="text-sm text-muted-foreground mb-4">Dosya analiz edildikten sonra sonuçlar sağ tarafta görünür.</p>
            <button
              disabled={isUploading}
              className="px-6 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all disabled:opacity-50 inline-flex items-center gap-2"
            >
              {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {isUploading ? "Yükleniyor..." : "Dosya Seç"}
            </button>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp,.dcm"
              onChange={handleFileInput}
              className="hidden"
              disabled={isUploading}
            />
          </div>

          <div className="mt-6 p-4 bg-info/10 border border-info/20 rounded-xl">
            <p className="text-sm text-info">
              <strong>Desteklenen formatlar:</strong> PDF, JPG, PNG, DICOM
            </p>
            <p className="text-sm text-info mt-1">
              <strong>Maksimum boyut:</strong> 10 MB
            </p>
          </div>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-foreground">Analiz Sonuçları</h3>
            <button
              onClick={loadReports}
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="w-4 h-4" />
              Yenile
            </button>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">Yükleniyor...</div>
          ) : files.length > 0 ? (
            <div className="space-y-4">
              {files.map((file) => {
                const fileId = file.id;
                const isSelected = selectedReportId === fileId;
                return (
                  <div
                    key={fileId}
                    onClick={() => loadReportDetails(fileId)}
                    className={`p-5 bg-surface border rounded-xl cursor-pointer transition-all ${
                      isSelected ? "border-primary ring-1 ring-primary/30" : "border-border hover:border-primary/40"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h4 className="font-bold text-foreground mb-1">{file.file_name || file.original_filename || file.filename}</h4>
                        <p className="text-sm text-muted-foreground">{file.date || file.created_at || ""}</p>
                      </div>
                      <Badge className="bg-success/10 text-success border-success/20">
                        {getStatusIcon(file.status)}
                        <span className="ml-2">
                          {file.status === "analyzed" || file.status === "completed"
                            ? "Tamamlandı"
                            : file.status === "processing"
                            ? "İşleniyor"
                            : file.status === "error"
                            ? "Hata"
                            : file.status === "uploaded"
                            ? "Yüklendi"
                            : "Beklemede"}
                        </span>
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>Rapor ID: {file.id}</span>
                      <button
                        onClick={(event) => {
                          event.stopPropagation();
                          loadReportDetails(fileId);
                        }}
                        className="inline-flex items-center gap-1 hover:text-foreground"
                      >
                        <Eye className="w-3 h-3" />
                        Detayları aç
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Henüz dosya yüklenmemiş</p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-foreground">Rapor Detayları</h3>
            <div className="flex gap-2">
              <button
                onClick={handleParseSelected}
                disabled={!selectedReportId || isDetailLoading}
                className="px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm disabled:opacity-50 inline-flex items-center gap-2"
              >
                {isDetailLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                Analizi Başlat
              </button>
              <button
                onClick={handleDownloadPdf}
                disabled={!selectedReportId || !reportDetail?.results?.length}
                className="px-4 py-2 rounded-xl bg-surface border border-border text-sm disabled:opacity-50 inline-flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                PDF İndir
              </button>
            </div>
          </div>

          {isDetailLoading ? (
            <div className="text-sm text-muted-foreground py-8">Rapor detayları yükleniyor...</div>
          ) : reportDetail ? (
            <div className="space-y-4">
              <div className="p-4 bg-surface border border-border rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Seçili rapor</p>
                  <p className="font-semibold text-foreground">{reportDetail.filename}</p>
                </div>
                <Badge className="bg-primary/10 text-primary border-primary/20">{reportDetail.status}</Badge>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-surface border border-border rounded-xl">
                  <p className="text-xs text-muted-foreground mb-1">Toplam Test</p>
                  <p className="text-2xl font-bold text-foreground">{reportDetail.total_tests}</p>
                </div>
                <div className="p-4 bg-surface border border-border rounded-xl">
                  <p className="text-xs text-muted-foreground mb-1">Öneri Sayısı</p>
                  <p className="text-2xl font-bold text-foreground">{recommendations ? Object.keys(recommendations).length : 0}</p>
                </div>
                <div className="p-4 bg-surface border border-border rounded-xl">
                  <p className="text-xs text-muted-foreground mb-1">PubMed</p>
                  <p className="text-2xl font-bold text-foreground">{pubmedArticles.length}</p>
                </div>
                <div className="p-4 bg-surface border border-border rounded-xl">
                  <p className="text-xs text-muted-foreground mb-1">Durum</p>
                  <p className="text-2xl font-bold text-foreground">{reportDetail.status}</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-3">Test Sonuçları</h4>
                <div className="space-y-3">
                  {reportDetail.results.length > 0 ? (
                    reportDetail.results.map((result) => (
                      <div key={`${result.test_name}-${result.created_at || result.value}`} className="p-4 bg-surface border border-border rounded-xl flex items-center justify-between">
                        <div>
                          <p className="font-medium text-foreground">{result.original_name || result.test_name}</p>
                          <p className="text-sm text-muted-foreground">
                            Referans: {result.ref_min ?? "-"} - {result.ref_max ?? "-"} {result.unit || ""}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-foreground">{result.value} {result.unit}</p>
                          <p className={`text-sm ${result.status === "high" ? "text-destructive" : result.status === "low" ? "text-warning" : "text-success"}`}>
                            {result.status}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">Bu rapor için henüz analiz sonucu yok. Analizi Başlat butonunu kullanın.</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-muted-foreground">
              Bir rapor seçin, detaylar burada görünecek.
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
            <h3 className="text-lg font-bold text-foreground mb-4">Öneriler</h3>
            {recommendations && Object.keys(recommendations).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(recommendations).map(([key, item]) => (
                  <div key={key} className="p-4 bg-surface border border-border rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-foreground">{item.title || key}</p>
                      <Badge className="bg-warning/10 text-warning border-warning/20">{item.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{item.message}</p>
                    <div className="text-sm text-foreground space-y-2">
                      <p><span className="font-semibold">Ye:</span> {Array.isArray(item.eat) ? item.eat.join(", ") : "-"}</p>
                      <p><span className="font-semibold">Kaçın:</span> {Array.isArray(item.avoid) ? item.avoid.join(", ") : "-"}</p>
                      <p><span className="font-semibold">Yaşam tarzı:</span> {Array.isArray(item.lifestyle) ? item.lifestyle.join(", ") : "-"}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Önerileri görmek için analiz yapılmış bir rapor seçin.</p>
            )}
          </div>

          <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
            <h3 className="text-lg font-bold text-foreground mb-4">PubMed Bağlantıları</h3>
            {pubmedArticles.length > 0 ? (
              <div className="space-y-3">
                {pubmedArticles.map((article) => (
                  <a
                    key={article.pmid}
                    href={article.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block p-4 bg-surface border border-border rounded-xl hover:border-primary/40 transition-all"
                  >
                    <p className="font-semibold text-foreground mb-1">{article.title}</p>
                    <p className="text-xs text-muted-foreground mb-2">
                      {article.authors} • {article.journal} • {article.pub_date}
                    </p>
                    <p className="text-sm text-muted-foreground line-clamp-3">{article.abstract}</p>
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">İlgili makaleleri görmek için analiz sonuçları gerekli.</p>
            )}
          </div>
        </div>
      </div>

      {/* Kişiye Özel Sağlık Asistanı Chatbot - seçili rapor bağlamıyla */}
      <HealthChatBot reportId={selectedReportId || undefined} />
    </>
  );
}
