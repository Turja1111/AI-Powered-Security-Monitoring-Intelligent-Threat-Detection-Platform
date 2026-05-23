import React, { useState } from "react";
import { Alert } from "../../types";
import { AlertBadge } from "../AlertFeed/AlertBadge";
import { formatTimeAgo } from "../../utils/formatters";
import { Check, ShieldAlert, ArrowUpDown } from "lucide-react";

interface AlertTableProps {
  alerts: Alert[];
  onAlertClick: (alert: Alert) => void;
  onAcknowledge: (id: string) => void;
  onResolve: (id: string) => void;
}

export const AlertTable: React.FC<AlertTableProps> = ({
  alerts,
  onAlertClick,
  onAcknowledge,
  onResolve,
}) => {
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [sortBy, setSortBy] = useState<"created_at" | "anomaly_score">("created_at");
  const [sortDesc, setSortDesc] = useState<boolean>(true);

  // Filter alerts
  const filteredAlerts = alerts
    .filter((a) => filterSeverity === "ALL" || a.severity === filterSeverity)
    .filter((a) => filterStatus === "ALL" || a.status === filterStatus);

  // Sort alerts
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    
    if (sortBy === "created_at") {
      aVal = new Date(a.created_at).getTime();
      bVal = new Date(b.created_at).getTime();
    }
    
    if (aVal < bVal) return sortDesc ? 1 : -1;
    if (aVal > bVal) return sortDesc ? -1 : 1;
    return 0;
  });

  const handleSort = (field: "created_at" | "anomaly_score") => {
    if (sortBy === field) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(field);
      setSortDesc(true);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "OPEN": return "text-red-400 bg-red-950/20 border-red-500/20";
      case "ACKNOWLEDGED": return "text-yellow-400 bg-yellow-950/20 border-yellow-500/20";
      case "RESOLVED": return "text-green-400 bg-green-950/20 border-green-500/20";
      default: return "text-slate-400 bg-slate-900/20 border-slate-500/20";
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter and Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#0f1629] p-4 rounded-xl border border-[#1e2d4a]/50 font-mono text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Severity:</span>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-[#0a0e1a] border border-[#1e2d4a] text-white px-2.5 py-1.5 rounded-lg focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="ALL">ALL SEVERITIES</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-[#0a0e1a] border border-[#1e2d4a] text-white px-2.5 py-1.5 rounded-lg focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="ALL">ALL STATUSES</option>
              <option value="OPEN">OPEN</option>
              <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </div>
        </div>

        <div className="text-[#64748b]">
          Showing {sortedAlerts.length} threat alerts
        </div>
      </div>

      {/* Main Table */}
      <div className="glass-card overflow-x-auto border border-[#1e2d4a]/40 rounded-xl">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead>
            <tr className="bg-[#162035]/50 text-[#64748b] border-b border-[#1e2d4a] uppercase text-[10px] tracking-wider">
              <th className="py-4 px-6">Severity</th>
              <th className="py-4 px-6">Alert Type</th>
              <th className="py-4 px-6">Source IP</th>
              <th className="py-4 px-6">Destination IP</th>
              <th className="py-4 px-6 cursor-pointer hover:text-white" onClick={() => handleSort("anomaly_score")}>
                Score <ArrowUpDown className="w-3 h-3 inline ml-1" />
              </th>
              <th className="py-4 px-6 cursor-pointer hover:text-white" onClick={() => handleSort("created_at")}>
                Created <ArrowUpDown className="w-3 h-3 inline ml-1" />
              </th>
              <th className="py-4 px-6">Status</th>
              <th className="py-4 px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1e2d4a]/20">
            {sortedAlerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-[#64748b]">
                  <ShieldAlert className="w-8 h-8 text-[#1e2d4a] mx-auto mb-2" />
                  No security incidents match the current filters.
                </td>
              </tr>
            ) : (
              sortedAlerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="hover:bg-[#162035]/30 cursor-pointer transition-colors"
                  onClick={() => onAlertClick(alert)}
                >
                  <td className="py-4 px-6">
                    <AlertBadge severity={alert.severity} />
                  </td>
                  <td className="py-4 px-6 font-semibold text-white uppercase">{alert.alert_type}</td>
                  <td className="py-4 px-6 text-[#00d4ff]">{alert.source_ip}</td>
                  <td className="py-4 px-6 text-[#94a3b8]">{alert.destination_ip || "—"}</td>
                  <td className="py-4 px-6 font-bold">{alert.anomaly_score}</td>
                  <td className="py-4 px-6 text-[#64748b]">{formatTimeAgo(alert.created_at)}</td>
                  <td className="py-4 px-6">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${getStatusBadgeClass(alert.status)}`}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-center gap-2">
                      {alert.status === "OPEN" && (
                        <button
                          onClick={() => onAcknowledge(alert.id)}
                          className="px-2 py-1 bg-yellow-600/20 border border-yellow-500/30 text-yellow-400 rounded hover:bg-yellow-500 hover:text-black font-semibold transition-all"
                        >
                          Ack
                        </button>
                      )}
                      {alert.status !== "RESOLVED" && (
                        <button
                          onClick={() => onResolve(alert.id)}
                          className="p-1 bg-green-600/20 border border-green-500/30 text-green-400 rounded hover:bg-green-500 hover:text-black transition-all"
                          title="Mark Resolved"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {alert.status === "RESOLVED" && (
                        <span className="text-[#64748b] text-[10px]">Closed</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
