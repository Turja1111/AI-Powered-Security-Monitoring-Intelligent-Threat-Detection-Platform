import axios from "axios";
import {
  Alert,
  LogEntry,
  MLModel,
  DashboardStats,
  TimeSeriesPoint,
  SeverityDistribution,
  TopAttackingIP,
  ThreatHeatmapCell,
  PaginatedResponse,
  AlertFilters,
  LogFilters,
} from "../types";

const API_BASE_URL = "/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const alertsApi = {
  list: async (filters: AlertFilters = {}): Promise<PaginatedResponse<Alert>> => {
    const response = await apiClient.get("/alerts/", { params: filters });
    // Handle mock formatting or database wrappers
    const data = response.data.results || response.data;
    return {
      data: Array.isArray(data) ? data : [],
      total: response.data.count || (Array.isArray(data) ? data.length : 0),
      page: filters.page || 1,
      page_size: filters.page_size || 50,
      total_pages: Math.ceil((response.data.count || 1) / (filters.page_size || 50)),
    };
  },

  get: async (id: string): Promise<Alert> => {
    const response = await apiClient.get(`/alerts/${id}/`);
    return response.data;
  },

  update: async (id: string, data: Partial<Alert>): Promise<Alert> => {
    const response = await apiClient.patch(`/alerts/${id}/`, data);
    return response.data;
  },

  getSummary: async (): Promise<any> => {
    const response = await apiClient.get("/alerts/summary/");
    return response.data;
  },
};

export const logsApi = {
  list: async (filters: LogFilters = {}): Promise<PaginatedResponse<LogEntry>> => {
    const response = await apiClient.get("/logs/", { params: filters });
    const data = response.data.results || response.data;
    return {
      data: Array.isArray(data) ? data : [],
      total: response.data.count || (Array.isArray(data) ? data.length : 0),
      page: filters.page || 1,
      page_size: filters.page_size || 50,
      total_pages: Math.ceil((response.data.count || 1) / (filters.page_size || 50)),
    };
  },

  get: async (id: string): Promise<LogEntry> => {
    const response = await apiClient.get(`/logs/${id}/`);
    return response.data;
  },

  uploadBatch: async (file: File, source = "csv-upload"): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source", source);
    const response = await apiClient.post("/logs/batch/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getStats: async (): Promise<any> => {
    const response = await apiClient.get("/logs/stats/");
    return response.data;
  },
};

export const modelsApi = {
  list: async (): Promise<MLModel[]> => {
    const response = await apiClient.get("/models/");
    return Array.isArray(response.data) ? response.data : (response.data.results || []);
  },

  activate: async (id: string): Promise<MLModel> => {
    const response = await apiClient.post(`/models/${id}/activate/`);
    return response.data;
  },
};

export const dashboardApi = {
  getAlertTimeSeries: async (): Promise<TimeSeriesPoint[]> => {
    const response = await apiClient.get("/alerts/timeseries/");
    return response.data;
  },

  getSeverityDistribution: async (): Promise<SeverityDistribution[]> => {
    const response = await apiClient.get("/alerts/severity/");
    return response.data;
  },

  getTopAttackingIPs: async (): Promise<TopAttackingIP[]> => {
    const response = await apiClient.get("/alerts/top-ips/");
    return response.data;
  },

  getThreatHeatmap: async (): Promise<ThreatHeatmapCell[]> => {
    const response = await apiClient.get("/threats/heatmap/");
    return response.data;
  },

  getSystemHealth: async (): Promise<any> => {
    const response = await apiClient.get("/system/health/");
    return response.data;
  },

  getIngestionRate: async (): Promise<any[]> => {
    const response = await apiClient.get("/logs/rate/");
    return response.data;
  },
};
