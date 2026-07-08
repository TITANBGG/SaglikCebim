import { FileText, Image } from "lucide-react";
import { Badge } from "./ui/badge";

interface ReportRowProps {
  fileName: string;
  status: "analyzed" | "parsed" | "reviewed";
  date: string;
  type: "pdf" | "image";
}

const statusConfig = {
  analyzed: { label: "Analiz Edildi", color: "success" },
  parsed: { label: "Parse Edildi", color: "info" },
  reviewed: { label: "İncelendi", color: "warning" },
};

export function ReportRow({ fileName, status, date, type }: ReportRowProps) {
  const statusInfo = statusConfig[status];
  const Icon = type === "pdf" ? FileText : Image;

  return (
    <div className="flex items-center gap-4 p-4 rounded-xl bg-card border border-border hover:bg-card-hover hover:border-border-strong transition-all">
      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground truncate">{fileName}</p>
        <p className="text-sm text-muted-foreground">{date}</p>
      </div>

      <Badge
        className={`
          ${statusInfo.color === "success" ? "bg-success/10 text-success border-success/20" : ""}
          ${statusInfo.color === "info" ? "bg-info/10 text-info border-info/20" : ""}
          ${statusInfo.color === "warning" ? "bg-warning/10 text-warning border-warning/20" : ""}
        `}
      >
        {statusInfo.label}
      </Badge>
    </div>
  );
}
