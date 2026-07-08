import { useId } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const mockData = [
  { month: "Oca", normal: 45, anormal: 12 },
  { month: "Şub", normal: 52, anormal: 8 },
  { month: "Mar", normal: 61, anormal: 15 },
  { month: "Nis", normal: 58, anormal: 10 },
  { month: "May", normal: 67, anormal: 7 },
  { month: "Haz", normal: 74, anormal: 9 },
];

export function TrendChart() {
  const chartId = useId();

  return (
    <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-foreground mb-1">Tahlil Trendleri</h3>
        <p className="text-sm text-muted-foreground">Son 6 aylık analiz özeti</p>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={mockData}>
          <defs>
            <linearGradient id={`gradient-normal-${chartId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id={`gradient-anormal-${chartId}`} x1="0" y1="0" x2="0" y2="1">
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
          <Area
            type="monotone"
            dataKey="normal"
            stroke="#22c55e"
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#gradient-normal-${chartId})`}
            name="Normal"
          />
          <Area
            type="monotone"
            dataKey="anormal"
            stroke="#f59e0b"
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#gradient-anormal-${chartId})`}
            name="Anormal"
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-success"></div>
          <span className="text-xs text-muted-foreground">Normal Sonuçlar</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-warning"></div>
          <span className="text-xs text-muted-foreground">Anormal Bulgular</span>
        </div>
      </div>
    </div>
  );
}
