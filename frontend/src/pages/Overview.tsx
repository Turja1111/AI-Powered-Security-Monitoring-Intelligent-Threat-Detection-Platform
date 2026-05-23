import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { AlertCircle, Activity, Brain, Server, ShieldAlert, TrendingUp } from "lucide-react";
import { dashboardApi } from "../services/api";
import { TimeSeriesPoint, SeverityDistribution, TopAttackingIP } from "../types";

export default function OverviewPage() {
  const [stats, setStats] = useState({
    total_alerts: 154,
    critical_count: 3,
    logs_ingested: 14205,
    active_accuracy: 98.4,
  });

  const [timeSeries, setTimeSeries] = useState<TimeSeriesPoint[]>([]);
  const [severities, setSeverities] = useState<SeverityDistribution[]>([]);
  const [topIps, setTopIps] = useState<TopAttackingIP[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Call all aggregated metrics endpoints
        const ts = await dashboardApi.getAlertTimeSeries();
        setTimeSeries(ts);

        const sev = await dashboardApi.getSeverityDistribution();
        setSeverities(sev);

        const ips = await dashboardApi.getTopAttackingIPs();
        setTopIps(ips);
      } catch (err) {
        console.error("Failed to load overview data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const COLORS = {
    CRITICAL: "#ef4444",
    HIGH: "#f97316",
    MEDIUM: "#eab308",
    LOW: "#6b7280",
  };

  const statCards = [
    { title: "Total Alerts (Today)", value: stats.total_alerts, change: "+12.4%", icon: ShieldAlert, color: "border-l-cyan-500 shadow-cyan-500/5 text-cyan-400" },
    { title: "Critical Intrusions", value: stats.critical_count, change: "0%", icon: AlertCircle, color: "border-l-rose-500 shadow-rose-500/5 text-rose-400 critical-pulse" },
    { title: "Raw Logs Ingested", value: stats.logs_ingested, change: "+85.2k", icon: Activity, color: "border-l-purple-500 shadow-purple-500/5 text-purple-400" },
    { title: "Ensemble Classifier Accuracy", value: `${stats.active_accuracy}%`, change: "Stable", icon: Brain, color: "border-l-emerald-500 shadow-emerald-500/5 text-emerald-400" },
  ];

  return (
    <div className="space-y-6">
      {/* ─────────────────────────── STAT CARDS ─────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className={`glass-card border-l-4 p-5 hover:translate-y-[-2px] transition-all duration-300 ${card.color}`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{card.title}</span>
                <Icon className="w-5 h-5 opacity-80" />
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-3xl font-bold text-slate-100">{card.value}</span>
                <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                  <TrendingUp className="w-3 h-3" />
                  {card.change}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ─────────────────────────── CHARTS SECTION ─────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart Alert Timeline */}
        <div className="glass-card p-6 lg:col-span-2 flex flex-col justify-between h-[360px]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Intrusion Alert Timeline (24h)</h2>
          </div>
          <div className="flex-1 w-full min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" stroke="#475569" tickFormatter={(t) => t.substring(11, 16)} />
                <YAxis stroke="#475569" />
                <Tooltip />
                <Line type="monotone" dataKey="critical" stroke={COLORS.CRITICAL} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="high" stroke={COLORS.HIGH} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="medium" stroke={COLORS.MEDIUM} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="low" stroke={COLORS.LOW} strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart Severity Distribution */}
        <div className="glass-card p-6 flex flex-col justify-between h-[360px]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Threat Severities (7d)</h2>
          </div>
          <div className="flex-1 w-full min-h-0 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severities}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {severities.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.severity as keyof typeof COLORS]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Summary Text */}
            <div className="absolute text-center">
              <span className="text-2xl font-bold text-slate-100">100%</span>
              <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Aggregated</div>
            </div>
          </div>
        </div>
      </div>

      {/* ─────────────────────────── TOP ATTACKING IPS ─────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">Top 10 Active Attacking Source IPs</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#1e2d4a] text-slate-500 uppercase tracking-wider">
                <th className="pb-3 pl-2">Rank</th>
                <th className="pb-3">Source IP</th>
                <th className="pb-3">Origin Country</th>
                <th className="pb-3 text-center">Alerts Triggered</th>
                <th className="pb-3">Peak Severity</th>
                <th className="pb-3 pr-2">Last Incident</th>
              </tr>
            </thead>
            <tbody>
              {topIps.map((item, idx) => (
                <tr key={idx} className="table-row-hover border-b border-[#1e2d4a]/50">
                  <td className="py-3 pl-2 font-semibold text-slate-400">#{item.rank}</td>
                  <td className="py-3 font-mono text-cyan-400">{item.ip}</td>
                  <td className="py-3">{item.country || "Unknown"}</td>
                  <td className="py-3 text-center font-bold">{item.alert_count}</td>
                  <td className="py-3">
                    <span className={`severity-${item.severity.toLowerCase()}`}>
                      {item.severity}
                    </span>
                  </td>
                  <td className="py-3 pr-2 text-slate-500 font-mono">
                    {item.last_seen.substring(11, 19)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
