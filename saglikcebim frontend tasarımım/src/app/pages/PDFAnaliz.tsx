import { CheckCircle2, Clock, FileText, Upload, XCircle } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";

export function PDFAnaliz() {
  return (
    <>
      <TopBar
        title="PDF Tahlil Analizi"
        subtitle="Sağlık raporlarınızı yükleyin, otomatik analiz yapın."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Dosya Yükleme</h3>

          <div className="border-2 border-dashed border-border-strong rounded-xl p-12 text-center hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <p className="text-foreground font-medium mb-2">
              PDF dosyanızı sürükleyip bırakın
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              veya bilgisayarınızdan seçin
            </p>
            <button className="px-6 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all">
              Dosya Seç
            </button>
          </div>

          <div className="mt-6 p-4 bg-info/10 border border-info/20 rounded-xl">
            <p className="text-sm text-info">
              <strong>Desteklenen formatlar:</strong> PDF, JPG, PNG
            </p>
            <p className="text-sm text-info mt-1">
              <strong>Maksimum boyut:</strong> 10 MB
            </p>
          </div>

          <div className="mt-6">
            <h4 className="text-sm font-bold text-foreground mb-3">Son Yüklenenler</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                <span className="text-sm text-foreground flex-1 truncate">kan_tahlili_2026.pdf</span>
                <Clock className="w-4 h-4 text-warning" />
              </div>
              <div className="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                <span className="text-sm text-foreground flex-1 truncate">checkup_raporu.pdf</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Analiz Sonuçları</h3>

          <div className="space-y-4">
            <div className="p-5 bg-surface border border-border rounded-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-bold text-foreground mb-1">e-Nabız Kan Tahlili</h4>
                  <p className="text-sm text-muted-foreground">28 Nisan 2026, 14:23</p>
                </div>
                <Badge className="bg-success/10 text-success border-success/20">
                  Tamamlandı
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4">
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Toplam Test</p>
                  <p className="text-lg font-bold text-foreground">24</p>
                </div>
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Normal</p>
                  <p className="text-lg font-bold text-success">22</p>
                </div>
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Düşük</p>
                  <p className="text-lg font-bold text-warning">1</p>
                </div>
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Yüksek</p>
                  <p className="text-lg font-bold text-destructive">1</p>
                </div>
              </div>
            </div>

            <div className="p-5 bg-surface border border-border rounded-xl">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-bold text-foreground mb-1">Hormon Panel Raporu</h4>
                  <p className="text-sm text-muted-foreground">25 Nisan 2026, 09:15</p>
                </div>
                <Badge className="bg-success/10 text-success border-success/20">
                  Tamamlandı
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4">
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Toplam Test</p>
                  <p className="text-lg font-bold text-foreground">8</p>
                </div>
                <div className="p-3 bg-card rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Normal</p>
                  <p className="text-lg font-bold text-success">8</p>
                </div>
              </div>
            </div>

            <div className="p-5 bg-surface border border-border rounded-xl opacity-60">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-bold text-foreground mb-1">Lipid Profili</h4>
                  <p className="text-sm text-muted-foreground">22 Nisan 2026, 16:40</p>
                </div>
                <Badge className="bg-destructive/10 text-destructive border-destructive/20">
                  <XCircle className="w-3 h-3 mr-1" />
                  Hata
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                PDF formatı tanınamadı. Lütfen tekrar yükleyin.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
