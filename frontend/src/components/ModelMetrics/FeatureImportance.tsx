import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";

export const FeatureImportance: React.FC = () => {
  const data = [
    { name: "total_packets", importance: 0.185 },
    { name: "port_entropy", importance: 0.154 },
    { name: "unique_dest_ports", importance: 0.128 },
    { name: "syn_flag_ratio", importance: 0.102 },
    { name: "total_bytes_sent", importance: 0.088 },
    { name: "connections_per_sec", importance: 0.076 },
    { name: "failed_connection_ratio", importance: 0.062 },
    { name: "avg_duration_ms", importance: 0.054 },
    { name: "byte_asymmetry_ratio", importance: 0.045 },
    { name: "total_bytes_received", importance: 0.038 },
    { name: "avg_packet_size", importance: 0.025 },
    { name: "rst_flag_ratio", importance: 0.021 },
    { name: "inter_arrival_mean", importance: 0.012 },
    { name: "night_time_flag", importance: 0.007 },
    { name: "icmp_ratio", importance: 0.003 }
  ];

  return (
    <div className="glass-card p-6 h-[400px] flex flex-col justify-between">
      <div>
        <h3 className="text-md font-bold text-white font-mono uppercase tracking-wider">Feature Importance (SHAP)</h3>
        <p className="text-xs text-[#64748b]">Top 15 attributes driving ensemble classification decisions</p>
      </div>

      <div className="flex-1 w-full mt-6">
        <ResponsiveContainer width="100%" height="95%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 10, left: 30, bottom: 5 }}>
            <XAxis type="number" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis 
              dataKey="name" 
              type="category" 
              stroke="#94a3b8" 
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
              formatter={(value: any) => [value, "SHAP Importance"]}
            />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  // color gradient from cyan to purple
                  fill={index % 2 === 0 ? "#00d4ff" : "#7c3aed"} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
