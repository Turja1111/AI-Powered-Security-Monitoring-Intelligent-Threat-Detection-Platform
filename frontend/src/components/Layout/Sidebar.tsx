import React from "react";
import { NavLink } from "react-router-dom";
import { LayoutDashboard, Bell, Database, Brain, Cpu, ShieldAlert } from "lucide-react";
import { useWebSocketContext } from "../../context/WebSocketContext";

export const Sidebar: React.FC = () => {
  const { isConnected } = useWebSocketContext();

  const navItems = [
    { name: "Overview", path: "/", icon: LayoutDashboard },
    { name: "Alerts", path: "/alerts", icon: Bell },
    { name: "Log Explorer", path: "/logs", icon: Database },
    { name: "ML Models", path: "/models", icon: Brain },
    { name: "Edge Devices", path: "/edge", icon: Cpu }
  ];

  return (
    <div className="w-60 bg-[#0f1629] border-r border-[#1e2d4a] flex flex-col justify-between h-screen text-[#e2e8f0]">
      {/* Top Section */}
      <div>
        {/* Brand Logo */}
        <div className="p-6 border-b border-[#1e2d4a] flex items-center gap-3">
          <ShieldAlert className="text-[#00d4ff] w-8 h-8 drop-shadow-[0_0_8px_rgba(0,212,255,0.8)]" />
          <span className="font-bold text-lg tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-[#00d4ff] to-[#7c3aed]">
            SECUREWATCH
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-4 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-[#162035] to-[#1e2d4a] text-[#00d4ff] border-l-4 border-[#00d4ff] pl-3"
                    : "text-[#64748b] hover:text-[#e2e8f0] hover:bg-[#162035]/50"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom Status Section */}
      <div className="p-4 border-t border-[#1e2d4a] bg-[#0a0e1a]/40">
        <div className="flex items-center justify-between">
          <span className="text-xs text-[#64748b]">Engine Stream</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isConnected
                  ? "bg-[#10b981] animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"
                  : "bg-[#ef4444]"
              }`}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
