import { Badge } from "./ui/badge";

interface TopBarProps {
  title: string;
  subtitle?: string;
}

export function TopBar({ title, subtitle }: TopBarProps) {
  const currentDate = new Date().toLocaleDateString("tr-TR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-bold text-foreground">{title}</h1>
          <Badge className="bg-success/10 text-success border-success/20 hover:bg-success/20">
            Sistem Aktif
          </Badge>
        </div>
        {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
      </div>
      <div className="text-right">
        <p className="text-sm text-muted-foreground">{currentDate}</p>
      </div>
    </div>
  );
}
