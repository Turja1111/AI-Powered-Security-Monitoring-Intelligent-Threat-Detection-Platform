import React, { useState } from "react";
import { Cpu, Wifi, WifiOff, Zap, Shield, HelpCircle, Activity } from "lucide-react";

interface Device {
  id: string;
  name: string;
  ip: string;
  status: "online" | "offline" | "warning";
  event_rate: number;
  latency_edge_ms: number;
  latency_cloud_ms: number;
  bandwidth_saved: string;
  mqtt_connected: boolean;
}

export default function EdgePage() {
  const [devices] = useState<Device[]>([
    {
      id: "edge-node-01",
      name: "RasPi Primary Gateway",
      ip: "192.168.1.55",
      status: "online",
      event_rate: 1205,
      latency_edge_ms: 1.4,
      latency_cloud_ms: 45.2,
      bandwidth_saved: "92.4%",
      mqtt_connected: true,
    },
    {
      id: "edge-node-02",
      name: "IDF Switch Sensor",
      ip: "192.168.1.56",
      status: "online",
      event_rate: 450,
      latency_edge_ms: 2.1,
      latency_cloud_ms: 48.0,
      bandwidth_saved: "95.1%",
      mqtt_connected: true,
    },
    {
      id: "edge-node-03",
      name: "Lab Testing Node",
      ip: "192.168.1.102",
      status: "offline",
      event_rate: 0,
      latency_edge_ms: 0,
      latency_cloud_ms: 0,
      bandwidth_saved: "0%",
      mqtt_connected: false,
    },
  ]);

  return (
    <div className="space-y-6">
      {/* ─────────────────────────── EDGE METRIC CARDS ─────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card border-l-4 border-l-cyan-400 p-5 shadow-cyan-500/5 text-cyan-400 flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Active Edge Nodes</span>
            <span className="text-2xl font-bold text-slate-100 font-mono">2 / 3</span>
          </div>
        </div>

        <div className="glass-card border-l-4 border-l-purple-400 p-5 shadow-purple-500/5 text-purple-400 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Edge Latency Savings</span>
            <span className="text-2xl font-bold text-slate-100 font-mono">43.8ms</span>
          </div>
        </div>

        <div className="glass-card border-l-4 border-l-emerald-400 p-5 shadow-emerald-500/5 text-emerald-400 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Bandwidth Saved</span>
            <span className="text-2xl font-bold text-slate-100 font-mono">93.7% avg</span>
          </div>
        </div>
      </div>

      {/* ─────────────────────────── DEVICES LIST ───────────────────────── */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4 border-b border-[#1e2d4a] pb-3">
          Edge Broker Sensor Devices
        </h3>

        <div className="space-y-4">
          {devices.map((dev) => (
            <div
              key={dev.id}
              className="p-4 rounded-xl border border-[#1e2d4a] bg-[#0f1629]/50 flex flex-wrap gap-6 items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-lg ${
                    dev.status === "online"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/25"
                      : "bg-slate-500/10 text-slate-500 border border-slate-500/20"
                  }`}
                >
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <span className="font-bold text-slate-200 block">{dev.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    ID: {dev.id} | IP: {dev.ip}
                  </span>
                </div>
              </div>

              {/* Stats benchmarks */}
              {dev.status === "online" ? (
                <div className="flex gap-6 items-center flex-wrap text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] block uppercase tracking-wider mb-0.5">Events Rate</span>
                    <span className="font-semibold text-slate-300 font-mono">{dev.event_rate}/min</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block uppercase tracking-wider mb-0.5">Edge vs Cloud Latency</span>
                    <span className="font-mono text-cyan-400 font-bold">
                      {dev.latency_edge_ms}ms <span className="text-slate-600 font-normal">vs {dev.latency_cloud_ms}ms</span>
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block uppercase tracking-wider mb-0.5">Bandwidth Reduced</span>
                    <span className="font-mono text-emerald-400 font-bold">{dev.bandwidth_saved}</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-semibold text-[10px]">
                    <Wifi className="w-3.5 h-3.5" />
                    MQTT Connected
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 bg-slate-500/10 border border-slate-500/20 text-slate-500 px-2 py-0.5 rounded font-semibold text-[10px]">
                  <WifiOff className="w-3.5 h-3.5" />
                  MQTT Offline
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
