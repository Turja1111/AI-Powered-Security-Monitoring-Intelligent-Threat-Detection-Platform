import React from "react";

interface AlertBadgeProps {
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
}

export const AlertBadge: React.FC<AlertBadgeProps> = ({ severity }) => {
  const getBadgeStyle = () => {
    switch (severity?.toUpperCase()) {
      case "CRITICAL":
        return "text-[#ef4444] bg-[#ef4444]/10 border-[#ef4444]/30 shadow-[0_0_12px_rgba(239,68,68,0.25)] relative overflow-hidden";
      case "HIGH":
        return "text-[#f97316] bg-[#f97316]/10 border-[#f97316]/30";
      case "MEDIUM":
        return "text-[#eab308] bg-[#eab308]/10 border-[#eab308]/30";
      default:
        return "text-[#64748b] bg-[#64748b]/10 border-[#64748b]/30";
    }
  };

  return (
    <div className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${getBadgeStyle()}`}>
      <span className="relative z-10 flex items-center gap-1.5 justify-center">
        {severity?.toUpperCase() === "CRITICAL" && (
          <span className="w-1.5 h-1.5 rounded-full bg-[#ef4444] animate-ping" />
        )}
        {severity}
      </span>
    </div>
  );
};
