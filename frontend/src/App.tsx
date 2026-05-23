import React, { useState, useEffect } from "react";
import { Shield, LayoutDashboard, Bell, Database, Brain, Cpu, Clock, AlertTriangle, CheckCircle, Wifi, WifiOff } from "lucide-react";
import { format } from "date-fns";

// Pages
import OverviewPage from "./pages/Overview";
import AlertsPage from "./pages/Alerts";
import LogsPage from "./pages/Logs";
import ModelsPage from "./pages/Models";
import EdgePage from "./pages/Edge";

import { useWebSocket } from "./hooks/useWebSocket";
import { dashboardApi } from "./services/api";

type ActiveTab = "overview" | "alerts" | "logs" | "models" | "edge";

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [alertCount, setAlertCount] = useState(0);
  
  // Custom WebSocket connection tracker
  const { isConnected } = useWebSocket("/ws/alerts/");

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch initial summary counts
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const stats = await dashboardApi.getSystemHealth();
        // Set alert count dynamically or fetch from alert counts
        setAlertCount(3); // Mocking active alert notification count
      } catch (err) {
        console.error("Health summary counts retrieval failed:", err);
      }
    };
    fetchCounts();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case "overview":
        return <OverviewPage />;
      case "alerts":
        return <AlertsPage />;
      case "logs":
        return <LogsPage />;
      case "models":
        return <ModelsPage />;
      case "edge":
        return <EdgePage />;
      default:
        return <OverviewPage />;
    }
  };

  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "alerts", label: "Alerts", icon: Bell, badge: alertCount },
    { id: "logs", label: "Log Explorer", icon: Database },
    { id: "models", label: "ML Models", icon: Brain },
    { id: "edge", label: "Edge Devices", icon: Cpu },
  ];

  return (
    <div className="flex h-screen bg-[#0a0e1a] text-slate-200 overflow-hidden font-sans">
      {/* ─────────────────────────── SIDEBAR ───────────────────────────── */}
      <aside className="w-60 bg-[#0f1629] border-r border-[#1e2d4a] flex flex-col justify-between p-4 shrink-0">
        <div>
          {/* Logo / Title */}
          <div className="flex items-center gap-3 px-2 py-4 mb-6 select-none">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 glow-cyan">
              <Shield className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
                SecureWatch
              </span>
              <div className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mt-0.5">
                AI threat platform
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as ActiveTab)}
                  className={`w-full nav-link flex items-center justify-between ${
                    isActive ? "active" : ""
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5 shrink-0" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && item.badge > 0 ? (
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse">
                      {item.badge}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Connection Status */}
        <div className="border-t border-[#1e2d4a] pt-4 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Server Stream</span>
            {isConnected ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <Wifi className="w-3.5 h-3.5" />
                Live
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-rose-400 font-semibold animate-pulse">
                <WifiOff className="w-3.5 h-3.5" />
                Disconnected
              </span>
            )}
          </div>
          <div className="text-[10px] text-slate-600 font-mono text-center">
            v1.0.0 (Cap. Release)
          </div>
        </div>
      </aside>

      {/* ─────────────────────────── MAIN WRAPPER ───────────────────────── */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-[#0f1629]/50 backdrop-blur-md border-b border-[#1e2d4a] flex items-center justify-between px-6 shrink-0">
          <div>
            <h1 className="text-lg font-bold tracking-wide capitalize text-slate-100">
              {activeTab} Panel
            </h1>
          </div>

          <div className="flex items-center gap-6">
            {/* Live Clock */}
            <div className="flex items-center gap-2 text-sm text-slate-400 font-mono bg-[#162035]/50 px-3 py-1 rounded-md border border-[#1e2d4a]">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span>{format(currentTime, "HH:mm:ss")}</span>
            </div>

            {/* Platform Status */}
            <div className="flex items-center gap-2 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle className="w-3.5 h-3.5" />
              System nominal
            </div>
          </div>
        </header>

        {/* Page Content Panel */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#0a0e1a]">
          <div className="max-w-[1600px] mx-auto page-transition">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}
