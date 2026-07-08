import { Activity, FileCheck, FileText, ImageIcon } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { ReportRow } from "../components/ReportRow";
import { TopBar } from "../components/TopBar";
import { TrendChart } from "../components/TrendChart";

export function Dashboard() {
  return (
    <>
      <TopBar
        title="Sağlık Analiz Paneli"
        subtitle="PDF tahliller, grafikler ve radyoloji sonuçları tek ekranda."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={FileText}
          label="Analiz Edilen PDF"
          value="142"
          trend={{ value: "12%", positive: true }}
          iconColor="text-primary"
        />
        <MetricCard
          icon={Activity}
          label="Anormal Bulgu"
          value="23"
          trend={{ value: "3%", positive: false }}
          iconColor="text-warning"
        />
        <MetricCard
          icon={FileCheck}
          label="Normal Sonuç"
          value="119"
          trend={{ value: "8%", positive: true }}
          iconColor="text-success"
        />
        <MetricCard
          icon={ImageIcon}
          label="X-Ray Analizi"
          value="34"
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
          </div>
        </div>

        <TrendChart />
      </div>
    </>
  );
}
