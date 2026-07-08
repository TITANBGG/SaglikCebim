import { useState } from "react";
import { AppSidebar } from "./components/AppSidebar";
import { Dashboard } from "./pages/Dashboard";
import { Makaleler } from "./pages/Makaleler";
import { PDFAnaliz } from "./pages/PDFAnaliz";
import { Radyoloji } from "./pages/Radyoloji";
import { Trendler } from "./pages/Trendler";

export default function App() {
  const [currentRoute, setCurrentRoute] = useState("/dashboard");

  const renderPage = () => {
    switch (currentRoute) {
      case "/dashboard":
        return <Dashboard />;
      case "/upload":
        return <PDFAnaliz />;
      case "/trends":
        return <Trendler />;
      case "/radiology":
        return <Radyoloji />;
      case "/articles":
        return <Makaleler />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="dark min-h-screen bg-background">
      <AppSidebar activeRoute={currentRoute} onNavigate={setCurrentRoute} />

      <main className="ml-[250px] p-8">
        {renderPage()}
      </main>
    </div>
  );
}