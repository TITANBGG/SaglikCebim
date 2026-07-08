import { useEffect, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, FileImage, History, Loader2, Upload, Clock, BarChart2, Brain } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";
import { apiClient } from "../../api/client";

export function Radyoloji() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [modelInfo, setModelInfo] = useState<any | null>(null);
  const [showMetrics, setShowMetrics] = useState(false);

  useEffect(() => {
    fetchHistory();
    fetchModelInfo();
  }, []);

  const fetchModelInfo = async () => {
    try {
      const res = await apiClient.get("/radiology/model-info");
      setModelInfo(res.data);
    } catch {
      // Model bilgisi yoksa sessizce geç
    }
  };

  const fetchHistory = async () => {
    try {
      const data = await apiClient.listRadiology();
      setHistory(data);
    } catch (e) {
      console.error("Geçmiş yüklenemedi", e);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setAnalysisResult(null);
    setError("");
    setShowHeatmap(false);

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    // DICOM dosyaları tarayıcıda görüntülenemez — önizleme atlanıyor
    if (file.name.toLowerCase().endsWith(".dcm")) {
      setPreviewUrl(null);
    } else {
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Lütfen bir görüntü seçin.");
      return;
    }

    try {
      setIsUploading(true);
      setError("");
      const formData = new FormData();
      formData.append("file", selectedFile);
      const response = await apiClient.uploadRadiology(formData);
      setAnalysisResult(response);
      fetchHistory(); // Listeyi güncelle
    } catch (err: any) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      if (status === 401) {
        setError("Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.");
      } else if (status === 400) {
        setError(detail || "Geçersiz dosya formatı veya boyut limiti aşıldı.");
      } else if (status === 0 || !err.response) {
        setError("Sunucuya bağlanılamıyor. Backend çalışıyor mu?");
      } else {
        setError(detail || "Görüntü yüklenemedi");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const loadFromHistory = async (imageId: number) => {
    try {
      setIsUploading(true);
      const data = await apiClient.getRadiologyDetails(imageId);
      setAnalysisResult(data);
      setPreviewUrl(null); // Orijinal dosyaya erişimimiz yok, heatmap veya placeholder gösterilecek
      setShowHeatmap(true);
    } catch (e) {
      setError("Analiz detayı yüklenemedi.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <>
      <TopBar
        title="Radyoloji Görüntü Analizi"
        subtitle="X-Ray ve diğer görüntüler için hızlı otomatik analiz."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Görüntü Yükleme</h3>

          <div
            className="border-2 border-dashed border-border-strong rounded-xl p-12 text-center hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer mb-6"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <p className="text-foreground font-medium mb-2">Radyoloji görüntüsünü seçin</p>
            <p className="text-sm text-muted-foreground mb-4">JPG, PNG, BMP, GIF veya DICOM</p>
            <button className="px-6 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all inline-flex items-center gap-2">
              {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileImage className="w-4 h-4" />}
              {isUploading ? "Yükleniyor..." : "Görüntü Seç"}
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept=".dcm,.png,.jpg,.jpeg,.bmp,.gif"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {selectedFile && (
            <div className="bg-surface border border-border rounded-xl p-4 mb-4">
              <p className="text-sm text-muted-foreground mb-1">Seçili dosya</p>
              <p className="font-medium text-foreground">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          <div className="bg-surface border border-border rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-sm font-bold text-foreground">Önizleme</h4>
              {analysisResult?.heatmap_url && (
                <button
                  onClick={() => setShowHeatmap(!showHeatmap)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${showHeatmap ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary hover:bg-primary/20'}`}
                >
                  {showHeatmap ? "Orijinal Görüntü" : "Isı Haritasını Göster"}
                </button>
              )}
            </div>
            <div className="aspect-square bg-card rounded-lg flex items-center justify-center border border-border overflow-hidden">
              {showHeatmap && analysisResult?.heatmap_url ? (
                <img src={`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}${analysisResult.heatmap_url}`} alt="AI Isı Haritası" className="w-full h-full object-contain" />
              ) : previewUrl ? (
                <img src={previewUrl} alt="Radyoloji önizleme" className="w-full h-full object-contain" />
              ) : (
                <div className="text-center">
                  <FileImage className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Görüntü yüklenmedi</p>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <div className="mt-4">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all disabled:opacity-50 inline-flex items-center justify-center gap-2"
            >
              {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Analizi Başlat
            </button>
          </div>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Analiz Bulguları</h3>

          {analysisResult ? (
            <>
              <div className="p-5 bg-surface border border-border rounded-xl mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center">
                    <CheckCircle2 className="w-5 h-5 text-success" />
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground">Analiz Tamamlandı</h4>
                    <p className="text-sm text-muted-foreground">
                      {analysisResult.body_part?.toUpperCase?.() || analysisResult.body_part || "Görüntü"} - {analysisResult.modality}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">Durum: {analysisResult.status}</p>
              </div>

              <div className="space-y-3 mb-6">
                <h4 className="text-sm font-bold text-foreground">Tespit Edilen Bulgular</h4>
                {(analysisResult.findings || []).map((finding: any, index: number) => (
                  <div key={`${finding.tr_name}-${index}`} className="p-4 bg-surface border border-border rounded-xl">
                    <div className="flex items-center justify-between mb-3 gap-3">
                      <div>
                        <span className="font-medium text-foreground">{finding.tr_name}</span>
                        <p className="text-xs text-muted-foreground mt-1">{finding.description}</p>
                      </div>
                      <Badge className="bg-primary/10 text-primary border-primary/20">
                        %{Math.round((finding.confidence || 0) * 100)}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground flex flex-wrap gap-2">
                      <span>Şiddet: {finding.severity || "-"}</span>
                      <span>Konum: {finding.location || "-"}</span>
                    </div>
                    <div className="mt-3 text-sm text-foreground">
                      <span className="font-semibold">Öneriler:</span>{" "}
                      {Array.isArray(finding.suggested_actions) ? finding.suggested_actions.join(", ") : "-"}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="p-5 bg-surface border border-border rounded-xl mb-6 text-sm text-muted-foreground">
              Görüntü yükledikten sonra analiz çıktısı burada görünecek.
            </div>
          )}

          <div className="p-5 bg-info/10 border border-info/20 rounded-xl">
            <h4 className="font-bold text-info mb-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Klinik Notlar
            </h4>
            <p className="text-sm text-info leading-relaxed">
              Bu modül temel klinik yönlendirme sağlar. Kesin yorum için uzman hekim değerlendirmesi gerekir.
            </p>
          </div>
        </div>
      </div>

      {/* Geçmiş Analizler Listesi */}
      <div className="mt-8 bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
        <div className="flex items-center gap-3 mb-6">
          <History className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-bold text-foreground">Geçmiş Analizler</h3>
        </div>

        {history.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.map((item) => (
              <div 
                key={item.id} 
                onClick={() => loadFromHistory(item.id)}
                className="group p-4 bg-surface border border-border rounded-xl hover:border-primary/50 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <FileImage className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground truncate max-w-[150px]">
                      {item.original_filename}
                    </p>
                    <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                      <Clock className="w-3 h-3" />
                      {new Date(item.created_at).toLocaleDateString('tr-TR')}
                    </div>
                  </div>
                </div>
                <Badge className="bg-primary/5 text-primary border-primary/10 group-hover:bg-primary group-hover:text-white transition-all">
                  {item.modality}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border-2 border-dashed border-border rounded-2xl bg-surface/30">
            <Clock className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
            <p className="text-muted-foreground">Henüz kaydedilmiş bir radyoloji görüntüsü bulunmuyor.</p>
          </div>
        )}
      </div>

      {/* Model Performans Paneli */}
      {modelInfo && (
        <div className="mt-8 bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-primary" />
              <div>
                <h3 className="text-xl font-bold text-foreground">AI Model Performansı</h3>
                <p className="text-sm text-muted-foreground">{modelInfo.model_name} · {modelInfo.dataset} · {modelInfo.num_classes} sınıf</p>
              </div>
            </div>
            <button
              onClick={() => setShowMetrics(!showMetrics)}
              className="px-4 py-2 text-sm bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors flex items-center gap-2"
            >
              <BarChart2 className="w-4 h-4" />
              {showMetrics ? "Gizle" : "Sınıf Detayları"}
            </button>
          </div>

          {/* Genel Metrikler */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-surface border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-primary">{(modelInfo.overall.mean_auc * 100).toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground mt-1">Ortalama AUC-ROC</p>
            </div>
            <div className="bg-surface border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-emerald-500">{(modelInfo.overall.weighted_f1 * 100).toFixed(0)}%</p>
              <p className="text-xs text-muted-foreground mt-1">Ağırlıklı F1</p>
            </div>
            <div className="bg-surface border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-amber-500">{modelInfo.num_classes}</p>
              <p className="text-xs text-muted-foreground mt-1">Patoloji Sınıfı</p>
            </div>
          </div>

          {/* Sınıf Bazlı Metrikler */}
          {showMetrics && (
            <div>
              <p className="text-sm font-semibold text-foreground mb-3">Sınıf Bazında AUC-ROC</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(modelInfo.per_class as Record<string, any>)
                  .sort((a, b) => b[1].auc - a[1].auc)
                  .map(([cls, metrics]) => (
                    <div key={cls} className="flex items-center gap-3 p-3 bg-surface border border-border rounded-lg">
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-foreground truncate">
                            {modelInfo.tr_names?.[cls] || cls}
                          </span>
                          <span className={`text-sm font-bold ml-2 ${metrics.auc >= 0.85 ? 'text-emerald-500' : metrics.auc >= 0.75 ? 'text-amber-500' : 'text-red-400'}`}>
                            {(metrics.auc * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-border rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${metrics.auc >= 0.85 ? 'bg-emerald-500' : metrics.auc >= 0.75 ? 'bg-amber-500' : 'bg-red-400'}`}
                            style={{ width: `${metrics.auc * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
              <p className="text-xs text-muted-foreground mt-4 text-center">
                {modelInfo.overall.notes}
              </p>
            </div>
          )}
        </div>
      )}
    </>
  );
}
