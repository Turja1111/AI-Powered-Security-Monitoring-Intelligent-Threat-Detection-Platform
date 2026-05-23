import { Alert, LogEntry, MLModel, TimeSeriesPoint, SeverityDistribution, TopAttackingIP, ThreatHeatmapCell, EdgeDevice } from "../types";

export function generateMockAlerts(count = 20): Alert[] {
  const severities: Alert["severity"][] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  const types = ["port_scan", "brute_force", "ddos", "exfiltration", "web_attack", "bot"];
  const ips = ["192.168.1.102", "10.0.0.45", "172.16.0.9", "185.220.101.4", "94.23.22.12"];
  const descriptions = {
    port_scan: "Multiple sequential port connections detected from same source IP.",
    brute_force: "Failed SSH login attempts exceeding threshold of 10 per minute.",
    ddos: "High-volume UDP flood packet rate targeting web services.",
    exfiltration: "Abnormal outbound data transfer volume compared to historical profiles.",
    web_attack: "SQL injection payload detected in HTTP request arguments.",
    bot: "Connection to classified command & control server domain resolved."
  };

  return Array.from({ length: count }).map((_, i) => {
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const alert_type = types[Math.floor(Math.random() * types.length)];
    const source_ip = ips[Math.floor(Math.random() * ips.length)];
    
    return {
      id: `alert-${i}-${Math.random().toString(36).substr(2, 9)}`,
      created_at: new Date(Date.now() - i * 600000).toISOString(), // intervals of 10 min
      severity,
      alert_type,
      source_ip,
      destination_ip: "192.168.1.1",
      anomaly_score: parseFloat((0.4 + Math.random() * 0.6).toFixed(3)),
      model_used: i % 2 === 0 ? "xgboost_classifier" : "ensemble",
      description: descriptions[alert_type as keyof typeof descriptions] || "General anomaly identified in window features.",
      status: i < 5 ? "OPEN" : i < 12 ? "ACKNOWLEDGED" : "RESOLVED",
      acknowledged_by: i >= 5 && i < 12 ? "operator_1" : undefined,
      resolved_at: i >= 12 ? new Date().toISOString() : undefined
    };
  });
}

export function generateMockLogs(count = 100): LogEntry[] {
  const ips = ["192.168.1.50", "192.168.1.100", "10.0.0.12", "172.16.0.4", "8.8.8.8"];
  const protocols: LogEntry["protocol"][] = ["TCP", "UDP", "ICMP"];
  const labels = ["BENIGN", "PortScan", "DDoS", "BruteForce"];

  return Array.from({ length: count }).map((_, i) => {
    const isAnomaly = Math.random() < 0.15;
    return {
      id: `log-${i}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(Date.now() - i * 5000).toISOString(),
      source_ip: ips[Math.floor(Math.random() * ips.length)],
      destination_ip: "192.168.1.1",
      source_port: Math.floor(1024 + Math.random() * 60000),
      destination_port: Math.random() < 0.8 ? 80 : 443,
      protocol: protocols[Math.floor(Math.random() * protocols.length)],
      bytes_sent: Math.floor(40 + Math.random() * 5000),
      bytes_received: Math.floor(40 + Math.random() * 20000),
      duration_ms: Math.floor(1 + Math.random() * 3000),
      packet_count: Math.floor(1 + Math.random() * 100),
      label: isAnomaly ? labels[Math.floor(1 + Math.random() * (labels.length - 1))] : "BENIGN",
      anomaly_score: isAnomaly ? parseFloat((0.6 + Math.random() * 0.4).toFixed(3)) : parseFloat((Math.random() * 0.3).toFixed(3))
    };
  });
}

export function generateMockTimeSeriesData(): TimeSeriesPoint[] {
  const points: TimeSeriesPoint[] = [];
  const now = Date.now();
  for (let i = 24; i >= 0; i--) {
    const date = new Date(now - i * 3600000);
    const hourStr = `${date.getHours().toString().padStart(2, "0")}:00`;
    points.push({
      timestamp: hourStr,
      value: Math.floor(5 + Math.random() * 25),
      critical: Math.floor(Math.random() * 3),
      high: Math.floor(Math.random() * 5),
      medium: Math.floor(Math.random() * 8),
      low: Math.floor(Math.random() * 10)
    });
  }
  return points;
}

export function generateMockModels(): MLModel[] {
  return [
    {
      id: "model-1",
      model_name: "isolation_forest",
      version: "1.0.4",
      algorithm: "Isolation Forest",
      f1_score: 0.942,
      precision_score: 0.951,
      recall_score: 0.933,
      roc_auc: 0.978,
      training_date: new Date(Date.now() - 5 * 86400000).toISOString(),
      is_active: true,
      dataset_trained_on: "CICIDS2017 (Normal Traffic)"
    },
    {
      id: "model-2",
      model_name: "xgboost_classifier",
      version: "2.1.0",
      algorithm: "XGBoost Classifier",
      f1_score: 0.988,
      precision_score: 0.991,
      recall_score: 0.985,
      roc_auc: 0.997,
      training_date: new Date(Date.now() - 3 * 86400000).toISOString(),
      is_active: true,
      dataset_trained_on: "CICIDS2017 + Synthetic Boost"
    },
    {
      id: "model-3",
      model_name: "lstm_detector",
      version: "1.2.0",
      algorithm: "LSTM Autoencoder",
      f1_score: 0.915,
      precision_score: 0.924,
      recall_score: 0.906,
      roc_auc: 0.954,
      training_date: new Date(Date.now() - 1 * 86400000).toISOString(),
      is_active: true,
      dataset_trained_on: "Timeseries Windows (CICIDS2017)"
    }
  ];
}

export function generateMockSeverityDistribution(): SeverityDistribution[] {
  return [
    { severity: "CRITICAL", count: 12, percentage: 10 },
    { severity: "HIGH", count: 24, percentage: 20 },
    { severity: "MEDIUM", count: 48, percentage: 40 },
    { severity: "LOW", count: 36, percentage: 30 }
  ];
}

export function generateMockTopIPs(): TopAttackingIP[] {
  return [
    { rank: 1, ip: "185.220.101.4", alert_count: 54, severity: "CRITICAL", last_seen: "2 mins ago", country: "NL" },
    { rank: 2, ip: "94.23.22.12", alert_count: 32, severity: "HIGH", last_seen: "12 mins ago", country: "FR" },
    { rank: 3, ip: "192.168.1.102", alert_count: 28, severity: "MEDIUM", last_seen: "1 hour ago", country: "Local" },
    { rank: 4, ip: "10.0.0.45", alert_count: 14, severity: "LOW", last_seen: "3 hours ago", country: "Local" }
  ];
}

export function generateMockHeatmap(): ThreatHeatmapCell[] {
  const cells: ThreatHeatmapCell[] = [];
  for (let day = 0; day < 7; day++) {
    for (let hour = 0; hour < 24; hour += 2) {
      cells.push({
        day,
        hour,
        count: Math.floor(Math.random() * (day === 0 || day === 6 ? 5 : 20))
      });
    }
  }
  return cells;
}

export function generateMockDevices(): EdgeDevice[] {
  return [
    {
      id: "edge-dev-01",
      name: "edge-arm-router-1",
      ip: "192.168.1.254",
      status: "online",
      last_seen: new Date().toISOString(),
      event_rate: 145,
      inference_latency_ms: 1.2,
      cloud_latency_ms: 45.8,
      bandwidth_saved_pct: 94.5,
      mqtt_connected: true,
      event_history: [12, 14, 15, 12, 10, 8, 14, 16, 20, 22, 19, 15, 14]
    },
    {
      id: "edge-dev-02",
      name: "edge-arm-switch-3",
      ip: "192.168.1.253",
      status: "warning",
      last_seen: new Date(Date.now() - 45000).toISOString(),
      event_rate: 89,
      inference_latency_ms: 1.5,
      cloud_latency_ms: 50.2,
      bandwidth_saved_pct: 88.0,
      mqtt_connected: true,
      event_history: [5, 4, 3, 8, 12, 14, 9, 8, 7, 6, 8, 12, 10]
    }
  ];
}
