import { formatDistanceToNow, parseISO } from "date-fns";

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatTimeAgo(isoString: string): string {
  try {
    const date = typeof isoString === "string" ? parseISO(isoString) : new Date(isoString);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (e) {
    return isoString;
  }
}

export function getSeverityColor(severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"): string {
  switch (severity?.toUpperCase()) {
    case "CRITICAL":
      return "text-red-500 bg-red-950/40 border-red-500/30";
    case "HIGH":
      return "text-orange-500 bg-orange-950/40 border-orange-500/30";
    case "MEDIUM":
      return "text-yellow-500 bg-yellow-950/40 border-yellow-500/30";
    case "LOW":
      return "text-slate-400 bg-slate-900/40 border-slate-500/20";
    default:
      return "text-slate-400 bg-slate-900/40 border-slate-500/20";
  }
}

export function formatIP(ip: string): string {
  return ip || "0.0.0.0";
}

export function formatNumber(n: number): string {
  if (n === undefined || n === null) return "0";
  return n.toLocaleString();
}
