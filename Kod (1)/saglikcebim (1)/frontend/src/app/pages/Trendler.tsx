import { useId } from "react";
import { Activity, TrendingDown, TrendingUp } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TopBar } from "../components/TopBar";

const monthlyData = [
  { month: "Oca", normal: 45, anormal: 12, toplam: 57 },
  { month: "Şub", normal: 52, anormal: 8, toplam: 60 },
  { month: "Mar", normal: 61, anormal: 15, toplam: 76 },
  { month: "Nis", normal: 58, anormal: 10, toplam: 68 },
  { month: "May", normal: 67, anormal: 7, toplam: 74 },
  { month: "Haz", normal: 74, anormal: 9, toplam: 83 },
];

const testTypeData = [
  { name: "Kan Tahlili", value: 45 },
  { name: "Hormon", value: 28 },
  { name: "Lipid", value: 22 },
  { name: "Tiroid", value: 18 },
  { name: "Vitamin", value: 15 },
  { name: "Diğer", value: 14 },
];

const weeklyActivity = [
  { day: "Pzt", count: 12 },
  { day: "Sal", count: 19 },
  { day: "Çar", count: 8 },
  { day: "Per", count: 15 },
  { day: "Cum", count: 22 },
  { day: "Cmt", count: 5 },
  { day: "Paz", count: 3 },
];

export function Trendler() {
  const chartId1 = useId();
  const chartId2 = useId();

  return (
    <>
      <TopBar
        title="Sağlık Trendleri"
        subtitle="Tahlil sonuçlarınızın zaman içindeki değişimini inceleyin."
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <TrendingUp className="w-5 h-5 text-success" />
          </div>
          <p className="text-sm text-muted-foreground mb-1">Toplam Analiz</p>
          <p className="text-3xl font-bold text-foreground mb-2">418</p>
          <p className="text-xs text-success">+18% bu ay</p>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-success" />
            </div>
            <TrendingUp className="w-5 h-5 text-success" />
          </div>
          <p className="text-sm text-muted-foreground mb-1">Normal Oran</p>
          <p className="text-3xl font-bold text-foreground mb-2">84.2%</p>
          <p className="text-xs text-success">+2.3% bu ay</p>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-warning/10 flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-warning" />
            </div>
            <TrendingDown className="w-5 h-5 text-success" />
          </div>
          <p className="text-sm text-muted-foreground mb-1">Anormal Oran</p>
          <p className="text-3xl font-bold text-foreground mb-2">15.8%</p>
          <p className="text-xs text-success">-2.3% bu ay</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-1">Aylık Trend Analizi</h3>
          <p className="text-sm text-muted-foreground mb-6">Son 6 aylık normal ve anormal sonuç dağılımı</p>

          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={monthlyData}>
              <defs>
                <linearGradient id={`gradient-normal-${chartId1}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id={`gradient-anormal-${chartId1}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(149, 184, 224, 0.1)" />
              <XAxis dataKey="month" stroke="#7f93ad" style={{ fontSize: "12px" }} />
              <YAxis stroke="#7f93ad" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#13233d",
                  border: "1px solid rgba(149, 184, 224, 0.18)",
                  borderRadius: "12px",
                  color: "#f4f7fb",
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="normal"
                stroke="#22c55e"
                strokeWidth={2}
                fillOpacity={1}
                fill={`url(#gradient-normal-${chartId1})`}
                name="Normal"
              />
              <Area
                type="monotone"
                dataKey="anormal"
                stroke="#f59e0b"
                strokeWidth={2}
                fillOpacity={1}
                fill={`url(#gradient-anormal-${chartId1})`}
                name="Anormal"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <h3 className="text-lg font-bold text-foreground mb-1">Test Türü Dağılımı</h3>
          <p className="text-sm text-muted-foreground mb-6">En çok yapılan test türleri</p>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={testTypeData}>
              <defs>
                <linearGradient id={`gradient-bar-${chartId2}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2dd4ff" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#2dd4ff" stopOpacity={0.3} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(149, 184, 224, 0.1)" />
              <XAxis dataKey="name" stroke="#7f93ad" style={{ fontSize: "11px" }} />
              <YAxis stroke="#7f93ad" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#13233d",
                  border: "1px solid rgba(149, 184, 224, 0.18)",
                  borderRadius: "12px",
                  color: "#f4f7fb",
                }}
              />
              <Bar dataKey="value" fill={`url(#gradient-bar-${chartId2})`} radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
        <h3 className="text-lg font-bold text-foreground mb-1">Haftalık Aktivite</h3>
        <p className="text-sm text-muted-foreground mb-6">Bu haftaki analiz yoğunluğu</p>

        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={weeklyActivity}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(149, 184, 224, 0.1)" />
            <XAxis dataKey="day" stroke="#7f93ad" style={{ fontSize: "12px" }} />
            <YAxis stroke="#7f93ad" style={{ fontSize: "12px" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#13233d",
                border: "1px solid rgba(149, 184, 224, 0.18)",
                borderRadius: "12px",
                color: "#f4f7fb",
              }}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#4f7cff"
              strokeWidth={3}
              dot={{ fill: "#4f7cff", r: 5 }}
              activeDot={{ r: 7 }}
              name="Analiz Sayısı"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
