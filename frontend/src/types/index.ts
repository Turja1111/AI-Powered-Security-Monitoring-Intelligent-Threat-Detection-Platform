export interface Alert {
  id: string
  created_at: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  alert_type: string
  source_ip: string
  destination_ip: string
  anomaly_score: number
  model_used: string
  description: string
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED'
  acknowledged_by?: string
  resolved_at?: string
}

export interface LogEntry {
  id: string
  timestamp: string
  source_ip: string
  destination_ip: string
  source_port: number
  destination_port: number
  protocol: 'TCP' | 'UDP' | 'ICMP'
  bytes_sent: number
  bytes_received: number
  duration_ms: number
  packet_count: number
  label: string
  anomaly_score?: number
}

export interface MLModel {
  id: string
  model_name: string
  version: string
  algorithm: string
  f1_score: number
  precision_score: number
  recall_score: number
  roc_auc: number
  training_date: string
  is_active: boolean
  dataset_trained_on: string
}

export interface DashboardStats {
  total_alerts_today: number
  critical_count: number
  logs_ingested: number
  active_model_accuracy: number
  alerts_change_percent: number
  logs_per_minute: number
}

export interface TimeSeriesPoint {
  timestamp: string
  value: number
  label?: string
  critical?: number
  high?: number
  medium?: number
  low?: number
}

export interface SeverityDistribution {
  severity: string
  count: number
  percentage: number
}

export interface TopAttackingIP {
  rank: number
  ip: string
  alert_count: number
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  last_seen: string
  country?: string
}

export interface ThreatHeatmapCell {
  day: number
  hour: number
  count: number
}

export interface EdgeDevice {
  id: string
  name: string
  ip: string
  status: 'online' | 'offline' | 'warning'
  last_seen: string
  event_rate: number
  inference_latency_ms: number
  cloud_latency_ms: number
  bandwidth_saved_pct: number
  mqtt_connected: boolean
  event_history: number[]
}

export interface AlertStatusChange {
  timestamp: string
  from_status: string
  to_status: string
  changed_by: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AlertFilters {
  severity?: string
  status?: string
  alert_type?: string
  source_ip?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export interface LogFilters {
  source_ip?: string
  destination_ip?: string
  protocol?: string
  label?: string
  port?: number
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export interface ConfusionMatrixData {
  labels: string[]
  matrix: number[][]
}

export interface ROCCurvePoint {
  fpr: number
  tpr: number
}

export interface FeatureImportanceItem {
  feature: string
  importance: number
}

export interface ModelMetrics {
  confusion_matrix: ConfusionMatrixData
  roc_curves: Record<string, ROCCurvePoint[]>
  feature_importance: FeatureImportanceItem[]
}

export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type AlertStatus = 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED'
export type Protocol = 'TCP' | 'UDP' | 'ICMP'
