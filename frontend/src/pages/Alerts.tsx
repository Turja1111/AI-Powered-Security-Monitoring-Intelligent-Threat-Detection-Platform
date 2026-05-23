import React, { useState } from "react";
import { useAlerts } from "../hooks/useAlerts";
import { Alert, Severity, AlertStatus } from "../types";
import { Eye, CheckCircle2, ShieldAlert, X, ShieldCheck } from "lucide-react";
import { format } from "date-fns";

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const { alerts, loading, error, acknowledge, resolve } = useAlerts({
    severity: severityFilter || undefined,
    status: statusFilter || undefined,
  });

  const getRecommendedAction = (type: string) => {
    switch (type) {
      case "ddos":
        return "Isolate target machine, apply cloud DDoS scrubbing filters, block source IP range at primary firewall.";
      case "port_scan":
        return "Log scanning activity. If scanning continues from identical IP range, dynamically drop incoming packets at edge router.";
      case "brute_force":
        return "Temporarily block SSH/RDP ingress ports for source IP. Verify lockouts and advise password rotations.";
      case "exfiltration":
        return "IMMEDIATE RESPONSE: Suspend target IP sessions, isolate compromised host, examine network flows for data payloads.";
      default:
        return "Investigate event logs, perform vulnerability scan on target host, monitor network connection spikes.";
    }
  };

  return (
    <div className="space-y-6">
      {/* ─────────────────────────── FILTER BAR ─────────────────────────── */}
      <div className="glass-card p-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-4 items-center flex-wrap">
          <div>
            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-[#162035] border border-[#1e2d4a] rounded px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#162035] border border-[#1e2d4a] rounded px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500"
            >
              <option value="">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>
        <div className="text-xs text-slate-500 font-mono">
          Loaded {alerts.length} security events
        </div>
      </div>

      {/* ─────────────────────────── ALERTS LIST TABLE ──────────────────── */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#1e2d4a] text-slate-500 uppercase tracking-wider">
                <th className="py-3.5 pl-4">Occurred At</th>
                <th className="py-3.5">Severity</th>
                <th className="py-3.5">Threat Class</th>
                <th className="py-3.5 font-mono">Source IP</th>
                <th className="py-3.5 text-center">Score</th>
                <th className="py-3.5">Status</th>
                <th className="py-3.5 pr-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    Scanning database for active threats...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-emerald-400 font-semibold">
                    No active threat signatures found in the environment.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="table-row-hover border-b border-[#1e2d4a]/50">
                    <td className="py-4 pl-4 font-mono text-slate-400">
                      {format(new Date(alert.created_at), "yyyy-MM-dd HH:mm:ss")}
                    </td>
                    <td className="py-4">
                      <span className={`severity-${alert.severity.toLowerCase()}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="py-4 font-bold tracking-wide uppercase text-slate-200">
                      {alert.alert_type.replace("_", " ")}
                    </td>
                    <td className="py-4 font-mono text-cyan-400">{alert.source_ip}</td>
                    <td className="py-4 text-center font-semibold text-rose-400 font-mono">
                      {alert.anomaly_score.toFixed(3)}
                    </td>
                    <td className="py-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          alert.status === "OPEN"
                            ? "bg-red-500/10 text-red-400 border-red-500/20"
                            : alert.status === "ACKNOWLEDGED"
                            ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
                            : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        }`}
                      >
                        {alert.status}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-right">
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="p-1 rounded bg-[#162035] border border-[#1e2d4a] hover:border-cyan-500 text-cyan-400 transition"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ─────────────────────────── DETAILED INVESTIGATION DRAWER ──────── */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-[500px] h-full bg-[#0f1629] border-l border-[#1e2d4a] p-6 shadow-2xl flex flex-col justify-between overflow-y-auto page-transition">
            <div>
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-[#1e2d4a] pb-4 mb-6">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-rose-400" />
                  <span className="font-bold text-sm uppercase tracking-wider text-slate-100">
                    Incident Details
                  </span>
                </div>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="p-1 rounded hover:bg-[#162035] text-slate-500 hover:text-slate-200 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Alert Content */}
              <div className="space-y-5 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-500 block">Incident ID</span>
                    <span className="font-mono text-slate-300 select-all">{selectedAlert.id}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Occurred At</span>
                    <span className="text-slate-300">
                      {format(new Date(selectedAlert.created_at), "yyyy-MM-dd HH:mm:ss")}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-500 block">Threat Class</span>
                    <span className="font-bold uppercase tracking-wide text-slate-200">
                      {selectedAlert.alert_type.replace("_", " ")}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Severity</span>
                    <span className={`severity-${selectedAlert.severity.toLowerCase()}`}>
                      {selectedAlert.severity}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-500 block">Source IP</span>
                    <span className="font-mono text-cyan-400 font-semibold">{selectedAlert.source_ip}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Anomaly Score</span>
                    <span className="font-mono text-rose-400 font-bold">{selectedAlert.anomaly_score.toFixed(3)}</span>
                  </div>
                </div>

                <div>
                  <span className="text-slate-500 block mb-1">Description</span>
                  <p className="bg-[#162035] p-3 rounded border border-[#1e2d4a] text-slate-300 leading-relaxed font-mono">
                    {selectedAlert.description}
                  </p>
                </div>

                <div>
                  <span className="text-slate-500 block mb-1">Recommended Action Protocol (SOP)</span>
                  <p className="bg-cyan-950/20 text-cyan-300 p-3 rounded border border-cyan-500/20 leading-relaxed font-semibold">
                    {getRecommendedAction(selectedAlert.alert_type)}
                  </p>
                </div>
              </div>
            </div>

            {/* Lifecycle Updates Trigger Buttons */}
            <div className="border-t border-[#1e2d4a] pt-4 mt-6 flex gap-3">
              {selectedAlert.status === "OPEN" && (
                <button
                  onClick={async () => {
                    const res = await acknowledge(selectedAlert.id);
                    setSelectedAlert(res);
                  }}
                  className="flex-1 btn-ghost flex items-center justify-center gap-2 text-yellow-400 hover:text-yellow-300 border-yellow-500/20 hover:border-yellow-500/40"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Acknowledge
                </button>
              )}
              {selectedAlert.status !== "RESOLVED" && (
                <button
                  onClick={async () => {
                    const res = await resolve(selectedAlert.id);
                    setSelectedAlert(res);
                  }}
                  className="flex-1 btn-primary flex items-center justify-center gap-2"
                >
                  <ShieldCheck className="w-4 h-4" />
                  Resolve Threat
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
