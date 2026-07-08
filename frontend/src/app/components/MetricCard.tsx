import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: {
    value: string;
    positive: boolean;
  };
  iconColor?: string;
}

const iconBgMap: Record<string, string> = {
  "text-primary": "bg-primary/10",
  "text-warning": "bg-warning/10",
  "text-success": "bg-success/10",
  "text-info": "bg-info/10",
};

export function MetricCard({ icon: Icon, label, value, trend, iconColor = "text-primary" }: MetricCardProps) {
  const bgClass = iconBgMap[iconColor] || "bg-primary/10";

  return (
    <div className="bg-card border border-border rounded-[18px] p-6 hover:bg-card-hover hover:border-border-strong transition-all duration-300 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl ${bgClass} flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
        {trend && (
          <div className={`text-xs font-medium px-2 py-1 rounded-full ${trend.positive ? "bg-success/10 text-success" : "bg-warning/10 text-warning"}`}>
            {trend.positive ? "+" : ""}{trend.value}
          </div>
        )}
      </div>

      <div>
        <p className="text-sm text-muted-foreground mb-1">{label}</p>
        <p className="text-3xl font-bold text-foreground">{value}</p>
      </div>
    </div>
  );
}
