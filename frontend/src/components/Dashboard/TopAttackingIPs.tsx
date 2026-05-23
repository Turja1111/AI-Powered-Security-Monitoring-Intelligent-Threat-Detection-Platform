import React from "react";
import { TopAttackingIP } from "../../types";

interface TopAttackingIPsProps {
  data: TopAttackingIP[];
  loading?: boolean;
}

export const TopAttackingIPs: React.FC<TopAttackingIPsProps> = ({ data, loading = false }) => {
  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL": return "text-red-500 bg-red-950/30 border-red-500/20";
      case "HIGH": return "text-orange-500 bg-orange-950/30 border-orange-500/20";
      case "MEDIUM": return "text-yellow-500 bg-yellow-950/30 border-yellow-500/20";
      default: return "text-slate-400 bg-slate-900/30 border-slate-500/20";
    }
  };

  const maxAlerts = data.length > 0 ? Math.max(...data.map(d => d.alert_count)) : 100;

  return (
    <div className="glass-card p-6 h-[340px] flex flex-col justify-between overflow-hidden">
      <div>
        <h3 className="text-md font-bold text-white">Top Attacking Source IPs</h3>
        <p className="text-xs text-[#64748b]">Highest volume incident origins in the network</p>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto mt-4 pr-1 scrollbar-thin">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="text-[#64748b] border-b border-[#1e2d4a]/50 pb-2">
                <th className="py-2">IP Address</th>
                <th className="py-2 text-right">Alarms</th>
                <th className="py-2 pl-4">Threat Level</th>
                <th className="py-2 pl-4">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2d4a]/20">
              {data.map((row, idx) => {
                const pct = (row.alert_count / maxAlerts) * 100;
                return (
                  <tr key={row.ip} className="hover:bg-[#162035]/30 transition-colors">
                    <td className="py-2.5 font-semibold text-[#e2e8f0]">
                      {row.ip} {row.country && <span className="text-[10px] text-[#64748b]">({row.country})</span>}
                    </td>
                    <td className="py-2.5 text-right font-bold text-white">{row.alert_count}</td>
                    <td className="py-2.5 pl-4 w-1/3">
                      <div className="w-full bg-[#0a0e1a] h-1.5 rounded-full overflow-hidden border border-[#1e2d4a]/50">
                        <div 
                          className="bg-gradient-to-r from-[#7c3aed] to-[#ef4444] h-full rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-2.5 pl-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadgeClass(row.severity)}`}>
                        {row.severity}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
