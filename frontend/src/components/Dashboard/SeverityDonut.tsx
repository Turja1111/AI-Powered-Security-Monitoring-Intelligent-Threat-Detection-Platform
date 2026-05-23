import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { SeverityDistribution } from "../../types";

interface SeverityDonutProps {
  data: SeverityDistribution[];
  loading?: boolean;
}

export const SeverityDonut: React.FC<SeverityDonutProps> = ({ data, loading = false }) => {
  const COLORS = {
    CRITICAL: "#ef4444",
    HIGH: "#f97316",
    MEDIUM: "#eab308",
    LOW: "#64748b"
  };

  const total = data.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <div className="glass-card p-6 h-[340px] flex flex-col justify-between">
      <div>
        <h3 className="text-md font-bold text-white">Severity Distribution</h3>
        <p className="text-xs text-[#64748b]">Overall breakdown of active security incidents</p>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-[#7c3aed] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-between gap-2">
          {/* Chart Wrapper */}
          <div className="relative w-1/2 h-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="80%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="severity"
                >
                  {data.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[entry.severity.toUpperCase() as keyof typeof COLORS] || "#64748b"} 
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f1629",
                    borderColor: "#1e2d4a",
                    color: "#e2e8f0"
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Label */}
            <div className="absolute text-center">
              <div className="text-2xl font-bold font-mono text-white">{total}</div>
              <div className="text-[10px] text-[#64748b] tracking-wider uppercase font-semibold">Alerts</div>
            </div>
          </div>

          {/* Custom Legend */}
          <div className="w-1/2 space-y-3 font-mono text-xs">
            {data.map((entry) => {
              const color = COLORS[entry.severity.toUpperCase() as keyof typeof COLORS] || "#64748b";
              return (
                <div key={entry.severity} className="flex items-center justify-between border-b border-[#1e2d4a]/30 pb-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                    <span className="text-[#94a3b8]">{entry.severity}</span>
                  </div>
                  <span className="font-bold text-white">{entry.count} ({entry.percentage}%)</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
