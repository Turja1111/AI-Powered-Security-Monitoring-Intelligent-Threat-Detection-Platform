import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Alert } from "../../types";
import { AlertBadge } from "./AlertBadge";
import { formatTimeAgo } from "../../utils/formatters";
import { ShieldAlert, Info } from "lucide-react";

interface AlertFeedProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts, onAlertClick }) => {
  const displayAlerts = alerts.slice(0, 15); // Show last 15 alerts

  return (
    <div className="glass-card p-6 h-full flex flex-col justify-between overflow-hidden border border-[#1e2d4a]/60">
      <div className="flex items-center gap-2 mb-4">
        <ShieldAlert className="w-5 h-5 text-[#ef4444]" />
        <div>
          <h3 className="text-md font-bold text-white">Live Threat Stream</h3>
          <p className="text-xs text-[#64748b]">Real-time detection events feed</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-1 scrollbar-thin space-y-3">
        <AnimatePresence initial={false}>
          {displayAlerts.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-[#64748b] gap-2 border border-dashed border-[#1e2d4a]/50 rounded-xl p-4">
              <Info className="w-8 h-8 text-[#1e2d4a]" />
              <span className="text-xs font-mono">No active threats detected</span>
            </div>
          ) : (
            displayAlerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.2 }}
                onClick={() => onAlertClick && onAlertClick(alert)}
                className={`p-3 rounded-lg border border-[#1e2d4a]/40 bg-[#0f1629]/60 hover:bg-[#162035]/80 hover:border-[#00d4ff]/40 cursor-pointer transition-all duration-200 flex items-center justify-between gap-3 ${
                  alert.severity === "CRITICAL" ? "border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.05)]" : ""
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-[#e2e8f0]">
                      {alert.source_ip}
                    </span>
                    <span className="text-[10px] text-[#64748b]">→</span>
                    <span className="text-[10px] font-mono text-[#64748b]">
                      {alert.alert_type}
                    </span>
                  </div>
                  <p className="text-[10px] text-[#94a3b8] truncate max-w-[170px]">
                    {alert.description}
                  </p>
                </div>
                <div className="text-right flex flex-col items-end gap-1.5 font-mono">
                  <AlertBadge severity={alert.severity} />
                  <span className="text-[9px] text-[#64748b]">
                    {formatTimeAgo(alert.created_at)}
                  </span>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
