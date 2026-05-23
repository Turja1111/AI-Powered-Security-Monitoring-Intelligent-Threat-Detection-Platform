import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Alert } from "../../types";
import { AlertBadge } from "../AlertFeed/AlertBadge";
import { formatTimeAgo } from "../../utils/formatters";
import { X, ShieldAlert, Terminal, Eye, CheckCircle } from "lucide-react";

interface AlertDetailDrawerProps {
  alert: Alert | null;
  onClose: () => void;
  onAcknowledge: (id: string) => void;
  onResolve: (id: string) => void;
}

export const AlertDetailDrawer: React.FC<AlertDetailDrawerProps> = ({
  alert,
  onClose,
  onAcknowledge,
  onResolve,
}) => {
  const getContainmentAdvice = (type: string) => {
    switch (type.toLowerCase()) {
      case "ddos":
        return "Apply rate limiting limits on downstream ingress ports. Initiate cloud scrubbing center redirection if volume persists.";
      case "port_scan":
        return "Temporarily quarantine source IP on perimeter firewalls. Check destination logs for any completed handshakes.";
      case "brute_force":
        return "Enforce IP backoff lockouts. Force credential re-authentication and verify if active user initiated connection.";
      case "exfiltration":
        return "Terminate the socket connection. Inspect network payload hashes. Check if data includes sensitive indices.";
      default:
        return "Quarantine IP, review historical connection vectors, and analyze raw log signatures.";
    }
  };

  return (
    <AnimatePresence>
      {alert && (
        <>
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-40"
          />

          {/* Drawer body */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 w-[460px] bg-[#0f1629] border-l border-[#1e2d4a] shadow-[0_0_50px_rgba(0,0,0,0.8)] z-50 p-6 flex flex-col justify-between text-[#e2e8f0]"
          >
            {/* Header */}
            <div>
              <div className="flex items-center justify-between border-b border-[#1e2d4a] pb-4 mb-6">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-[#ef4444]" />
                  <span className="font-bold text-md uppercase font-mono tracking-wider">Threat Investigation</span>
                </div>
                <button onClick={onClose} className="p-1 rounded hover:bg-[#162035] transition-colors">
                  <X className="w-5 h-5 text-[#64748b] hover:text-white" />
                </button>
              </div>

              {/* Alert Meta Grid */}
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <span className="text-xl font-bold font-mono text-white uppercase">{alert.alert_type}</span>
                  <AlertBadge severity={alert.severity} />
                </div>

                <div className="bg-[#0a0e1a] border border-[#1e2d4a]/50 rounded-xl p-4 space-y-3 font-mono text-xs">
                  <div className="flex justify-between border-b border-[#1e2d4a]/30 pb-2">
                    <span className="text-[#64748b]">Source Host:</span>
                    <span className="text-[#00d4ff] font-bold">{alert.source_ip}</span>
                  </div>
                  <div className="flex justify-between border-b border-[#1e2d4a]/30 pb-2">
                    <span className="text-[#64748b]">Target Host:</span>
                    <span className="text-[#94a3b8]">{alert.destination_ip || "192.168.1.1"}</span>
                  </div>
                  <div className="flex justify-between border-b border-[#1e2d4a]/30 pb-2">
                    <span className="text-[#64748b]">Anomaly Score:</span>
                    <span className="text-white font-bold">{alert.anomaly_score}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#64748b]">Identified:</span>
                    <span className="text-[#64748b]">{formatTimeAgo(alert.created_at)}</span>
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Analysis Description</span>
                  <p className="text-xs text-[#94a3b8] leading-relaxed bg-[#162035]/30 p-3 rounded-lg border border-[#1e2d4a]/20">
                    {alert.description}
                  </p>
                </div>

                {/* Recommended Containment */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Containment Playbook</span>
                  <div className="p-3 bg-red-950/20 border border-red-500/20 rounded-lg text-xs text-[#ef4444] leading-relaxed">
                    {getContainmentAdvice(alert.alert_type)}
                  </div>
                </div>

                {/* Raw Logs Context placeholder */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Log Context References</span>
                  <div className="bg-[#0a0e1a] p-3 rounded-lg border border-[#1e2d4a]/30 font-mono text-[10px] space-y-1.5 max-h-[120px] overflow-y-auto scrollbar-thin">
                    <div className="flex items-center gap-2 text-[#64748b]">
                      <Terminal className="w-3.5 h-3.5" />
                      <span>Linked Logs ({alert.raw_log_ids.length || 1} records)</span>
                    </div>
                    {alert.raw_log_ids.map((id, index) => (
                      <div key={id} className="text-[#94a3b8] truncate">
                        UUID: {id}
                      </div>
                    ))}
                    {alert.raw_log_ids.length === 0 && (
                      <div className="text-[#94a3b8] truncate">
                        UUID: log_event_rec_{alert.id.substring(6, 14)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Actions Block */}
            <div className="border-t border-[#1e2d4a] pt-4 mt-4 flex gap-3">
              {alert.status === "OPEN" && (
                <button
                  onClick={() => {
                    onAcknowledge(alert.id);
                    onClose();
                  }}
                  className="flex-1 py-3 bg-yellow-600 border border-yellow-500 text-black hover:bg-yellow-500 font-bold rounded-lg transition-all text-xs flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  Acknowledge Threat
                </button>
              )}
              {alert.status !== "RESOLVED" && (
                <button
                  onClick={() => {
                    onResolve(alert.id);
                    onClose();
                  }}
                  className="flex-1 py-3 bg-green-600 border border-green-500 text-white hover:bg-green-500 hover:text-black font-bold rounded-lg transition-all text-xs flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Resolve Threat
                </button>
              )}
              {alert.status === "RESOLVED" && (
                <div className="w-full text-center py-3 bg-[#162035] text-[#64748b] font-mono text-xs rounded-lg border border-[#1e2d4a]/50">
                  Incident Resolved & Closed
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
