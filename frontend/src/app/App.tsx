import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { AppSidebar } from "./components/AppSidebar";
import { Dashboard } from "./pages/Dashboard";
import { Makaleler } from "./pages/Makaleler";
import { PDFAnaliz } from "./pages/PDFAnaliz";
import { Radyoloji } from "./pages/Radyoloji";
import { Trendler } from "./pages/Trendler";
import { LoginPage } from "./pages/LoginPage";
import { Anamnez } from "./pages/Anamnez";
import { NeyimVar } from "./pages/NeyimVar";
import { SusAnketi } from "./pages/SusAnketi";

export default function App() {
  const { isAuthenticated, isLoading } = useAuth();
  const [currentRoute, setCurrentRoute] = useState("/dashboard");

  if (isLoading) {
    return (
      <div className="dark min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Yükleniyor...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentRoute) {
      case "/dashboard":
        return <Dashboard onNavigate={setCurrentRoute} />;
      case "/upload":
        return <PDFAnaliz />;
      case "/trends":
        return <Trendler />;
      case "/radiology":
        return <Radyoloji />;
      case "/articles":
        return <Makaleler />;
      case "/anamnez":
        return <Anamnez />;
      case "/neyim-var":
        return <NeyimVar />;
      case "/sus-anketi":
        return <SusAnketi />;
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