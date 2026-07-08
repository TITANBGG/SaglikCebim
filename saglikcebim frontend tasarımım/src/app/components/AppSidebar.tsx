import { Activity, FileText, Image, LayoutDashboard, TrendingUp } from "lucide-react";

interface SidebarProps {
  activeRoute?: string;
  onNavigate?: (route: string) => void;
}

export function AppSidebar({ activeRoute = "/dashboard", onNavigate }: SidebarProps) {
  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", route: "/dashboard" },
    { icon: FileText, label: "PDF Analiz", route: "/upload" },
    { icon: TrendingUp, label: "Trendler", route: "/trends" },
    { icon: Image, label: "Radyoloji", route: "/radiology" },
    { icon: Activity, label: "Makaleler", route: "/articles" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-[250px] bg-surface border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          SaglikCebim
        </h1>
        <p className="text-xs text-muted-foreground mt-1">Saglik Analiz Platformu</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeRoute === item.route;

          return (
            <button
              key={item.route}
              onClick={() => onNavigate?.(item.route)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                ${
                  isActive
                    ? "bg-primary/10 text-primary shadow-[0_0_20px_rgba(45,212,255,0.15)]"
                    : "text-muted-foreground hover:bg-card hover:text-foreground"
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm font-bold text-primary-foreground">
            SC
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">Sistem Kullanicisi</p>
            <p className="text-xs text-muted-foreground">Premium</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
