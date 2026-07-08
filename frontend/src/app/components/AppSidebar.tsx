import { Activity, FileText, Image, LayoutDashboard, TrendingUp, LogOut, User, Star } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

interface SidebarProps {
  activeRoute?: string;
  onNavigate?: (route: string) => void;
}

export function AppSidebar({ activeRoute = "/dashboard", onNavigate }: SidebarProps) {
  const { logout, user } = useAuth();

  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", route: "/dashboard" },
    { icon: User, label: "Anamnez (Öykü)", route: "/anamnez" },
    { icon: Activity, label: "Neyim Var?", route: "/neyim-var" },
    { icon: FileText, label: "PDF Analiz", route: "/upload" },
    { icon: TrendingUp, label: "Trendler", route: "/trends" },
    { icon: Image, label: "Radyoloji", route: "/radiology" },
    { icon: Activity, label: "Makaleler", route: "/articles" },
    { icon: Star, label: "Memnuniyet Anketi", route: "/sus-anketi" },
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

      <div className="p-4 border-t border-border space-y-3">
        <div className="px-4 py-3 bg-card rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <User className="w-4 h-4 text-primary" />
            <p className="text-xs text-muted-foreground">Hesap</p>
          </div>
          <p className="text-sm font-medium text-foreground truncate">{user?.email || "Kullanıcı"}</p>
        </div>

        <button
          onClick={() => {
            logout();
            window.location.href = "/";
          }}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-destructive/10 text-destructive hover:bg-destructive/20 rounded-lg font-medium transition-all"
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm">Çıkış Yap</span>
        </button>
      </div>
    </aside>
  );
}
