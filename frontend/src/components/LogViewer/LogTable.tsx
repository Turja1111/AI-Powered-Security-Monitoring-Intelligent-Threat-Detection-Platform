import React, { useState } from "react";
import { TableVirtuoso } from "react-virtuoso";
import { LogEntry } from "../../types";
import { formatBytes, formatDuration } from "../../utils/formatters";
import { Search, Download, Filter } from "lucide-react";

interface LogTableProps {
  logs: LogEntry[];
  loading?: boolean;
  onUploadClick?: () => void;
}

export const LogTable: React.FC<LogTableProps> = ({ logs, loading = false, onUploadClick }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterProto, setFilterProto] = useState("ALL");
  const [filterLabel, setFilterLabel] = useState("ALL");

  // Filter logs locally for search/filter inputs
  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.source_ip.includes(searchTerm) || 
      log.destination_ip.includes(searchTerm) || 
      log.label.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesProto = filterProto === "ALL" || log.protocol === filterProto;
    const matchesLabel = filterLabel === "ALL" || 
      (filterLabel === "ANOMALOUS" && log.label !== "BENIGN") || 
      (filterLabel === "BENIGN" && log.label === "BENIGN");

    return matchesSearch && matchesProto && matchesLabel;
  });

  const getProtocolBadge = (proto: string) => {
    switch (proto.toUpperCase()) {
      case "TCP": return "text-blue-400 bg-blue-950/30 border-blue-500/20";
      case "UDP": return "text-purple-400 bg-purple-950/30 border-purple-500/20";
      default: return "text-orange-400 bg-orange-950/30 border-orange-500/20";
    }
  };

  const getLabelColor = (label: string) => {
    if (label === "BENIGN") return "text-green-500 bg-green-950/30 border-green-500/20";
    return "text-red-500 bg-red-950/30 border-red-500/20 animate-pulse";
  };

  const handleExportCSV = () => {
    const headers = "timestamp,source_ip,destination_ip,source_port,destination_port,protocol,bytes_sent,bytes_received,duration_ms,packet_count,label,anomaly_score\n";
    const rows = filteredLogs.map(l => 
      `"${l.timestamp}","${l.source_ip}","${l.destination_ip}",${l.source_port},${l.destination_port},"${l.protocol}",${l.bytes_sent},${l.bytes_received},${l.duration_ms},${l.packet_count},"${l.label}",${l.anomaly_score || 0}`
    ).join("\n");

    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `securewatch_logs_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4 h-full flex flex-col">
      {/* Search and Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#0f1629] p-4 rounded-xl border border-[#1e2d4a]/50 font-mono text-xs">
        <div className="flex items-center gap-4 flex-wrap">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#64748b] absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="SEARCH BY IP / SIGNATURE..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#0a0e1a] border border-[#1e2d4a] text-white pl-9 pr-4 py-2 rounded-lg focus:outline-none focus:border-[#00d4ff] placeholder-[#64748b] w-64"
            />
          </div>

          {/* Protocol dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Protocol:</span>
            <select
              value={filterProto}
              onChange={(e) => setFilterProto(e.target.value)}
              className="bg-[#0a0e1a] border border-[#1e2d4a] text-white px-2.5 py-2 rounded-lg focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="ALL">ALL</option>
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
            </select>
          </div>

          {/* Classification dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Label:</span>
            <select
              value={filterLabel}
              onChange={(e) => setFilterLabel(e.target.value)}
              className="bg-[#0a0e1a] border border-[#1e2d4a] text-white px-2.5 py-2 rounded-lg focus:outline-none focus:border-[#00d4ff]"
            >
              <option value="ALL">ALL TRAFFIC</option>
              <option value="BENIGN">BENIGN ONLY</option>
              <option value="ANOMALOUS">ANOMALOUS ONLY</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {onUploadClick && (
            <button
              onClick={onUploadClick}
              className="px-4 py-2 bg-[#7c3aed] border border-[#7c3aed]/50 text-white rounded-lg hover:bg-opacity-80 transition-all font-semibold"
            >
              Upload CSV
            </button>
          )}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-[#0a0e1a] border border-[#1e2d4a] text-white rounded-lg hover:border-[#00d4ff] hover:text-[#00d4ff] transition-all font-semibold"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Virtualized Table Container */}
      <div className="flex-1 min-h-[460px] glass-card border border-[#1e2d4a]/40 rounded-xl overflow-hidden bg-[#0f1629]/60">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-[#00d4ff] border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <TableVirtuoso
            data={filteredLogs}
            fixedHeaderContent={() => (
              <tr className="bg-[#162035] text-[#64748b] font-mono text-[10px] tracking-wider uppercase border-b border-[#1e2d4a]">
                <th className="py-3 px-4 w-[16%]">Timestamp</th>
                <th className="py-3 px-4 w-[18%]">Source Address</th>
                <th className="py-3 px-4 w-[18%]">Dest Address</th>
                <th className="py-3 px-4 w-[8%] text-center">Proto</th>
                <th className="py-3 px-4 w-[10%] text-right">Bytes In/Out</th>
                <th className="py-3 px-4 w-[8%] text-right">Duration</th>
                <th className="py-3 px-4 w-[14%] text-center">Classification</th>
                <th className="py-3 px-4 w-[8%] text-right">Score</th>
              </tr>
            )}
            itemContent={(index, log) => (
              <>
                <td className="py-2.5 px-4 font-mono text-[#64748b]">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-2.5 px-4 font-mono text-[#00d4ff] font-semibold">
                  {log.source_ip}:{log.source_port}
                </td>
                <td className="py-2.5 px-4 font-mono text-[#94a3b8]">
                  {log.destination_ip}:{log.destination_port}
                </td>
                <td className="py-2.5 px-4 text-center">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${getProtocolBadge(log.protocol)}`}>
                    {log.protocol}
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-mono">
                  {formatBytes(log.bytes_sent)} / {formatBytes(log.bytes_received)}
                </td>
                <td className="py-2.5 px-4 text-right font-mono">
                  {formatDuration(log.duration_ms)}
                </td>
                <td className="py-2.5 px-4 text-center">
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold border uppercase ${getLabelColor(log.label)}`}>
                    {log.label}
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-mono font-bold text-white">
                  {log.anomaly_score !== undefined ? log.anomaly_score.toFixed(3) : "—"}
                </td>
              </>
            )}
          />
        )}
      </div>
    </div>
  );
};
