import { AlertCircle, CheckCircle2, FileImage, Upload } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";

const findings = [
  { label: "Akciğer Nodülü", probability: 8, severity: "low" },
  { label: "Pnömoni", probability: 2, severity: "low" },
  { label: "Kostal Kırık", probability: 15, severity: "medium" },
  { label: "Kardiyomegali", probability: 65, severity: "high" },
];

export function Radyoloji() {
  return (
    <>
      <TopBar
        title="Radyoloji Görüntü Analizi"
        subtitle="X-Ray ve görüntüleme sonuçlarınızı AI ile analiz edin."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Görüntü Yükleme</h3>

          <div className="border-2 border-dashed border-border-strong rounded-xl p-12 text-center hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer mb-6">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <p className="text-foreground font-medium mb-2">
              Radyoloji görüntüsünü yükleyin
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              X-Ray, CT veya MR görüntüleri
            </p>
            <button className="px-6 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all">
              Görüntü Seç
            </button>
          </div>

          <div className="bg-surface border border-border rounded-xl p-6">
            <h4 className="text-sm font-bold text-foreground mb-4">Önizleme</h4>
            <div className="aspect-square bg-card rounded-lg flex items-center justify-center border border-border">
              <div className="text-center">
                <FileImage className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Görüntü yüklenmedi</p>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Dosya Adı:</span>
                <span className="text-foreground font-medium">-</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Boyut:</span>
                <span className="text-foreground font-medium">-</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Format:</span>
                <span className="text-foreground font-medium">-</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-6">Analiz Bulguları</h3>

          <div className="p-5 bg-surface border border-border rounded-xl mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-success" />
              </div>
              <div>
                <h4 className="font-bold text-foreground">Analiz Tamamlandı</h4>
                <p className="text-sm text-muted-foreground">Göğüs Röntgeni - PA</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              28 Nisan 2026, 15:42 - Model: RadNet v3.2
            </p>
          </div>

          <div className="space-y-3 mb-6">
            <h4 className="text-sm font-bold text-foreground">Tespit Edilen Bulgular</h4>

            {findings.map((finding, index) => (
              <div key={index} className="p-4 bg-surface border border-border rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <AlertCircle className={`w-4 h-4 ${
                      finding.severity === "high" ? "text-destructive" :
                      finding.severity === "medium" ? "text-warning" :
                      "text-info"
                    }`} />
                    <span className="font-medium text-foreground">{finding.label}</span>
                  </div>
                  <Badge className={`${
                    finding.severity === "high" ? "bg-destructive/10 text-destructive border-destructive/20" :
                    finding.severity === "medium" ? "bg-warning/10 text-warning border-warning/20" :
                    "bg-info/10 text-info border-info/20"
                  }`}>
                    %{finding.probability}
                  </Badge>
                </div>
                <div className="w-full bg-card rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      finding.severity === "high" ? "bg-destructive" :
                      finding.severity === "medium" ? "bg-warning" :
                      "bg-info"
                    }`}
                    style={{ width: `${finding.probability}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="p-5 bg-info/10 border border-info/20 rounded-xl">
            <h4 className="font-bold text-info mb-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Klinik Notlar
            </h4>
            <p className="text-sm text-info leading-relaxed">
              Kardiyomegali bulgusu yüksek olasılıklı görünmektedir. Kardiyoloji konsültasyonu önerilir.
              Kostal kırık orta düzeyde şüpheli - lateral grafi ile doğrulanmalı.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
        <h3 className="text-lg font-bold text-foreground mb-4">Geçmiş Analizler</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-surface border border-border rounded-xl">
            <div className="aspect-square bg-card rounded-lg mb-3 flex items-center justify-center">
              <FileImage className="w-8 h-8 text-muted-foreground" />
            </div>
            <h4 className="font-medium text-foreground mb-1">Göğüs PA</h4>
            <p className="text-sm text-muted-foreground">26 Nisan 2026</p>
            <Badge className="bg-success/10 text-success border-success/20 mt-2">
              Normal
            </Badge>
          </div>

          <div className="p-4 bg-surface border border-border rounded-xl">
            <div className="aspect-square bg-card rounded-lg mb-3 flex items-center justify-center">
              <FileImage className="w-8 h-8 text-muted-foreground" />
            </div>
            <h4 className="font-medium text-foreground mb-1">El PA</h4>
            <p className="text-sm text-muted-foreground">24 Nisan 2026</p>
            <Badge className="bg-warning/10 text-warning border-warning/20 mt-2">
              Şüpheli
            </Badge>
          </div>

          <div className="p-4 bg-surface border border-border rounded-xl">
            <div className="aspect-square bg-card rounded-lg mb-3 flex items-center justify-center">
              <FileImage className="w-8 h-8 text-muted-foreground" />
            </div>
            <h4 className="font-medium text-foreground mb-1">Akciğer CT</h4>
            <p className="text-sm text-muted-foreground">20 Nisan 2026</p>
            <Badge className="bg-success/10 text-success border-success/20 mt-2">
              Normal
            </Badge>
          </div>
        </div>
      </div>
    </>
  );
}
