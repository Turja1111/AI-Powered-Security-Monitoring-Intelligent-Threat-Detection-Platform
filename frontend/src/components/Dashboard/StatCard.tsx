import React from "react";
import { ArrowUpRight, ArrowDownRight, LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  color: "cyan" | "purple" | "red" | "green" | "yellow";
  loading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  color,
  loading = false,
}) => {
  const colorMap = {
    cyan: "border-l-[#00d4ff] text-[#00d4ff] bg-[#00d4ff]/5 shadow-[0_0_15px_rgba(0,212,255,0.05)]",
    purple: "border-l-[#7c3aed] text-[#7c3aed] bg-[#7c3aed]/5 shadow-[0_0_15px_rgba(124,58,237,0.05)]",
    red: "border-l-[#ef4444] text-[#ef4444] bg-[#ef4444]/5 shadow-[0_0_15px_rgba(239,68,68,0.05)]",
    green: "border-l-[#10b981] text-[#10b981] bg-[#10b981]/5 shadow-[0_0_15px_rgba(16,185,129,0.05)]",
    yellow: "border-l-[#f59e0b] text-[#f59e0b] bg-[#f59e0b]/5 shadow-[0_0_15px_rgba(245,158,11,0.05)]"
  };

  return (
    <div className={`glass-card border-l-4 p-6 flex items-center justify-between transition-all duration-300 hover:scale-[1.02] ${colorMap[color]}`}>
      {loading ? (
        <div className="w-full flex justify-between items-center animate-pulse">
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-[#1e2d4a]/50 rounded w-2/3"></div>
            <div className="h-8 bg-[#1e2d4a]/85 rounded w-1/3"></div>
          </div>
          <div className="w-12 h-12 bg-[#1e2d4a]/50 rounded-lg"></div>
        </div>
      ) : (
        <>
          <div className="space-y-1">
            <span className="text-xs font-semibold text-[#64748b] tracking-wider uppercase">{title}</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold font-mono text-white">{value}</span>
              {change !== undefined && (
                <span className={`text-xs flex items-center font-semibold ${change >= 0 ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                  {change >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                  {Math.abs(change)}%
                </span>
              )}
            </div>
          </div>
          <div className="p-3 bg-[#0a0e1a]/60 rounded-xl border border-[#1e2d4a]/40">
            <Icon className="w-6 h-6" />
          </div>
        </>
      )}
    </div>
  );
};
