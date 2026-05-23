import { useEffect, useState, useCallback } from "react";
import { Alert, AlertFilters } from "../types";
import { alertsApi } from "../services/api";
import { useWebSocket } from "./useWebSocket";

export function useAlerts(filters: AlertFilters = {}) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hook up WebSocket
  const { lastMessage, isConnected } = useWebSocket("/ws/alerts/");

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await alertsApi.list(filters);
      setAlerts(response.data);
    } catch (err: any) {
      console.error("Failed to load alerts:", err);
      setError(err?.message || "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const acknowledge = useCallback(async (id: string, user = "admin") => {
    try {
      const updated = await alertsApi.update(id, {
        status: "ACKNOWLEDGED",
        acknowledged_by: user,
      });
      // Update local state
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
      return updated;
    } catch (err) {
      console.error("Failed to acknowledge alert:", err);
      throw err;
    }
  }, []);

  const resolve = useCallback(async (id: string) => {
    try {
      const updated = await alertsApi.update(id, {
        status: "RESOLVED",
        resolved_at: new Date().toISOString(),
      });
      // Update local state
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
      return updated;
    } catch (err) {
      console.error("Failed to resolve alert:", err);
      throw err;
    }
  }, []);

  // Fetch initial alerts
  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Process WebSocket stream notifications
  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === "new_alert") {
      const newAlert = lastMessage.data as Alert;
      
      // Prepend the new alert, avoiding duplicates
      setAlerts((prev) => {
        if (prev.some((a) => a.id === newAlert.id)) {
          return prev;
        }
        return [newAlert, ...prev];
      });
    } else if (lastMessage.type === "initial_alerts") {
      const initial = lastMessage.data as Alert[];
      setAlerts((prev) => {
        // Merge without duplicates
        const existingIds = new Set(prev.map((a) => a.id));
        const filteredInitial = initial.filter((a) => !existingIds.has(a.id));
        return [...prev, ...filteredInitial].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      });
    }
  }, [lastMessage]);

  return {
    alerts,
    loading,
    error,
    acknowledge,
    resolve,
    refetch: fetchAlerts,
    isWebSocketConnected: isConnected,
  };
}
