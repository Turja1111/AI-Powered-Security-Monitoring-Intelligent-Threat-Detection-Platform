import React from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { TimeSeriesPoint } from "../../types";

interface AlertTimelineProps {
  data: TimeSeriesPoint[];
  loading?: boolean;
}

export const AlertTimeline: React.FC<AlertTimelineProps> = ({ data, loading = false }) => {
  return (
    <div className="glass-card p-6 h-[340px] flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-md font-bold text-white">Alert Rate Timeline (24h)</h3>
          <p className="text-xs text-[#64748b]">Hourly aggregate of detected security threats</p>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorMedium" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#eab308" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#eab308" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" opacity={0.2} />
              <XAxis 
                dataKey="timestamp" 
                stroke="#64748b" 
                fontSize={10} 
                tickLine={false} 
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f1629",
                  borderColor: "#1e2d4a",
                  borderRadius: "8px",
                  color: "#e2e8f0",
                  fontFamily: "monospace"
                }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Area 
                type="monotone" 
                dataKey="critical" 
                name="Critical" 
                stroke="#ef4444" 
                fillOpacity={1} 
                fill="url(#colorCritical)" 
                strokeWidth={2}
              />
              <Area 
                type="monotone" 
                dataKey="high" 
                name="High" 
                stroke="#f97316" 
                fillOpacity={1} 
                fill="url(#colorHigh)" 
                strokeWidth={2}
              />
              <Area 
                type="monotone" 
                dataKey="medium" 
                name="Medium" 
                stroke="#eab308" 
                fillOpacity={1} 
                fill="url(#colorMedium)" 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
