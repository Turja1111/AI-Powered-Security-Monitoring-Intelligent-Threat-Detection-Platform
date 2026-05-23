import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Bell, HeartPulse } from "lucide-react";
import { useWebSocketContext } from "../../context/WebSocketContext";

export const Header: React.FC = () => {
  const location = useLocation();
  const { alertHistory } = useWebSocketContext();
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getPageTitle = () => {
    switch (location.pathname) {
      case "/":
        return "Overview Dashboard";
      case "/alerts":
        return "Threat Alerts Manager";
      case "/logs":
        return "Ingested Log Explorer";
      case "/models":
        return "Ensemble Model Registry";
      case "/edge":
        return "Edge AI Device Monitor";
      default:
        return "SecureWatch Platform";
    }
  };

  const openAlertsCount = alertHistory.filter(a => a.status === "OPEN").length;

  return (
    <header className="h-16 border-b border-[#1e2d4a] bg-[#0f1629]/80 backdrop-blur-md px-8 flex items-center justify-between text-[#e2e8f0]">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white">{getPageTitle()}</h1>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-6">
        {/* Clock */}
        <div className="text-sm font-mono text-[#64748b] bg-[#0a0e1a]/60 px-3 py-1.5 rounded border border-[#1e2d4a]/50">
          {time.toLocaleTimeString()}
        </div>

        {/* System Health Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-[#10b981]/20 bg-[#10b981]/5 text-xs text-[#10b981]">
          <HeartPulse className="w-3.5 h-3.5" />
          <span>System Healthy</span>
        </div>

        {/* Alerts Bell */}
        <div className="relative cursor-pointer p-1.5 rounded-full hover:bg-[#162035] transition-all">
          <Bell className="w-5 h-5 text-[#94a3b8] hover:text-[#e2e8f0]" />
          {openAlertsCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 bg-[#ef4444] text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full border-2 border-[#0f1629]">
              {openAlertsCount}
            </span>
          )}
        </div>
      </div>
    </header>
  );
};
