import React from "react";
import { ThreatHeatmapCell } from "../../types";

interface ThreatHeatmapProps {
  data: ThreatHeatmapCell[];
  loading?: boolean;
}

export const ThreatHeatmap: React.FC<ThreatHeatmapProps> = ({ data, loading = false }) => {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];

  // Helper to find count
  const getCellCount = (dayIdx: number, hour: number) => {
    // Find matching cell
    const cell = data.find(c => c.day === dayIdx && (c.hour === hour || c.hour === hour + 1));
    return cell ? cell.count : 0;
  };

  // Helper for color mapping (cool to hot)
  const getCellColor = (count: number) => {
    if (count === 0) return "bg-[#0f1629]/40 border-[#1e2d4a]/20";
    if (count < 5) return "bg-blue-950/60 border-blue-800/20 text-blue-300";
    if (count < 12) return "bg-purple-900/50 border-purple-700/20 text-purple-200";
    if (count < 25) return "bg-orange-900/60 border-orange-700/30 text-orange-200";
    return "bg-red-950 border-red-500/40 text-red-100 shadow-[0_0_8px_rgba(239,68,68,0.2)]";
  };

  return (
    <div className="glass-card p-6 flex flex-col justify-between">
      <div>
        <h3 className="text-md font-bold text-white">Threat Activity Heatmap</h3>
        <p className="text-xs text-[#64748b]">Correlation of security events by day of week and time of day</p>
      </div>

      {loading ? (
        <div className="h-[220px] flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto pr-1">
          <div className="min-w-[640px] font-mono text-[10px]">
            {/* Hours Header Row */}
            <div className="grid grid-cols-[50px_repeat(12,1fr)] gap-2 mb-2 text-center text-[#64748b]">
              <div className="text-left font-semibold">Day</div>
              {hours.map(h => (
                <div key={h}>{h.toString().padStart(2, "0")}:00</div>
              ))}
            </div>

            {/* Grid rows */}
            <div className="space-y-2">
              {days.map((day, dayIdx) => (
                <div key={day} className="grid grid-cols-[50px_repeat(12,1fr)] gap-2 items-center">
                  {/* Day label */}
                  <div className="text-[#94a3b8] font-semibold text-left">{day}</div>
                  
                  {/* Hour cells */}
                  {hours.map(hour => {
                    const count = getCellCount(dayIdx, hour);
                    return (
                      <div
                        key={`${dayIdx}-${hour}`}
                        className={`h-8 flex items-center justify-center rounded border transition-all duration-200 hover:scale-[1.08] relative group cursor-pointer ${getCellColor(count)}`}
                      >
                        <span className="font-semibold text-xs opacity-75">{count > 0 ? count : ""}</span>
                        {/* Hover Tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-[#0a0e1a] text-white border border-[#1e2d4a] py-1 px-2.5 rounded text-[10px] font-semibold opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-xl whitespace-nowrap">
                          {day} @ {hour}:00: {count} alerts
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
            
            {/* Heatmap Legend */}
            <div className="flex items-center justify-end gap-3 mt-4 text-[9px] text-[#64748b]">
              <span>Benign</span>
              <div className="w-4 h-4 rounded border bg-[#0f1629]/40 border-[#1e2d4a]/20" />
              <div className="w-4 h-4 rounded border bg-blue-950/60 border-blue-800/20" />
              <div className="w-4 h-4 rounded border bg-purple-900/50 border-purple-700/20" />
              <div className="w-4 h-4 rounded border bg-orange-900/60 border-orange-700/30" />
              <div className="w-4 h-4 rounded border bg-red-950 border-red-500/40" />
              <span>Critical</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
