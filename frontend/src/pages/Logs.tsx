import React, { useState, useEffect } from "react";
import { LogEntry } from "../types";
import { logsApi } from "../services/api";
import { Search, Upload, Download, RefreshCw, AlertTriangle } from "lucide-react";
import { format } from "date-fns";

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchIP, setSearchIP] = useState("");
  const [protocol, setProtocol] = useState("");
  const [label, setLabel] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await logsApi.list({
        source_ip: searchIP || undefined,
        protocol: protocol || undefined,
        label: label || undefined,
      });
      setLogs(response.data);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [searchIP, protocol, label]);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploadStatus("Uploading & queueing batch job...");
    try {
      await logsApi.uploadBatch(uploadFile);
      setUploadStatus("Successfully ingested batch logs! Refreshing...");
      setUploadFile(null);
      fetchLogs();
    } catch (err: any) {
      console.error(err);
      setUploadStatus(`Error: ${err?.message || "Ingestion failed"}`);
    }
  };

  const handleExportCSV = () => {
    // Generate simple local client-side CSV download
    const headers = ["Timestamp", "Source IP", "Destination IP", "Protocol", "Bytes Sent", "Bytes Recv", "Label"];
    const rows = logs.map(l => [
      l.timestamp,
      l.source_ip,
      l.destination_ip,
      l.protocol,
      l.bytes_sent,
      l.bytes_received,
      l.label
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `securewatch_logs_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* ─────────────────────────── CONTROL BAR ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search & Filter */}
        <div className="glass-card p-4 lg:col-span-2 flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px] relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Source IP..."
              value={searchIP}
              onChange={(e) => setSearchIP(e.target.value)}
              className="w-full bg-[#162035] border border-[#1e2d4a] rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <select
              value={protocol}
              onChange={(e) => setProtocol(e.target.value)}
              className="bg-[#162035] border border-[#1e2d4a] rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500"
            >
              <option value="">All Protocols</option>
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
            </select>
          </div>
          <div>
            <select
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="bg-[#162035] border border-[#1e2d4a] rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500"
            >
              <option value="">All Labels</option>
              <option value="BENIGN">Benign</option>
              <option value="PortScan">PortScan</option>
              <option value="DDoS">DDoS</option>
              <option value="BruteForce">BruteForce</option>
              <option value="Exfiltration">Exfiltration</option>
            </select>
          </div>
          <button
            onClick={fetchLogs}
            className="p-2 rounded-lg bg-[#162035] border border-[#1e2d4a] hover:border-cyan-500 text-cyan-400 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Ingest and Export Buttons */}
        <div className="glass-card p-4 flex gap-3 items-center justify-between">
          <form onSubmit={handleFileUpload} className="flex gap-2 items-center flex-1">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              className="hidden"
              id="csv-file-picker"
            />
            <label
              htmlFor="csv-file-picker"
              className="flex-1 btn-ghost flex items-center justify-center gap-1.5 cursor-pointer text-xs py-2"
            >
              <Upload className="w-3.5 h-3.5" />
              {uploadFile ? uploadFile.name.substring(0, 12) + "..." : "Select CSV"}
            </label>
            {uploadFile && (
              <button type="submit" className="btn-primary text-xs py-2">
                Ingest
              </button>
            )}
          </form>

          <button
            onClick={handleExportCSV}
            className="btn-ghost flex items-center gap-1.5 text-xs py-2 hover:text-cyan-400 hover:border-cyan-500"
          >
            <Download className="w-3.5 h-3.5" />
            Export
          </button>
        </div>
      </div>

      {uploadStatus && (
        <div className="text-xs text-cyan-400 font-mono bg-cyan-950/20 border border-cyan-500/20 p-2.5 rounded-lg flex items-center gap-2">
          <ActivityIndicator />
          {uploadStatus}
        </div>
      )}

      {/* ─────────────────────────── LOG ENTRIES TABLE ─────────────────── */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#1e2d4a] text-slate-500 uppercase tracking-wider">
                <th className="py-3.5 pl-4">Timestamp</th>
                <th className="py-3.5 font-mono">Source IP</th>
                <th className="py-3.5">Destination IP</th>
                <th className="py-3.5">Protocol</th>
                <th className="py-3.5 text-right">Bytes Sent</th>
                <th className="py-3.5 text-right">Bytes Recv</th>
                <th className="py-3.5">Label</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    Querying raw data hypertable...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No network log matches found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="table-row-hover border-b border-[#1e2d4a]/30">
                    <td className="py-3 pl-4 font-mono text-slate-400">
                      {format(new Date(log.timestamp), "yyyy-MM-dd HH:mm:ss")}
                    </td>
                    <td className="py-3 font-mono text-cyan-400">{log.source_ip}</td>
                    <td className="py-3 font-mono text-slate-300">{log.destination_ip}</td>
                    <td className="py-3 font-semibold text-slate-400">{log.protocol}</td>
                    <td className="py-3 text-right font-mono text-slate-400">{log.bytes_sent.toLocaleString()}</td>
                    <td className="py-3 text-right font-mono text-slate-400">{log.bytes_received.toLocaleString()}</td>
                    <td className="py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                          log.label === "BENIGN"
                            ? "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                            : "bg-red-500/15 text-red-400 border border-red-500/20 font-bold"
                        }`}
                      >
                        {log.label}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ActivityIndicator() {
  return <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />;
}
