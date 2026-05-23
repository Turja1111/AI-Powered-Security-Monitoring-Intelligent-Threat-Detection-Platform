import React, { createContext, useContext, useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { Alert } from "../types";

interface WebSocketContextType {
  isConnected: boolean;
  lastAlert: Alert | null;
  alertHistory: Alert[];
  sendMessage: (msg: any) => boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const wsUrl = "/ws/alerts/";
  const { isConnected, lastMessage, sendMessage } = useWebSocket(wsUrl);
  const [lastAlert, setLastAlert] = useState<Alert | null>(null);
  const [alertHistory, setAlertHistory] = useState<Alert[]>([]);

  useEffect(() => {
    if (lastMessage) {
      try {
        // Validate if it is a security alert object
        if (lastMessage.id && lastMessage.severity) {
          const alert = lastMessage as Alert;
          setLastAlert(alert);
          setAlertHistory((prev) => [alert, ...prev].slice(0, 100)); // Keep last 100 alerts
        }
      } catch (err) {
        console.error("Error processing websocket message as alert:", err);
      }
    }
  }, [lastMessage]);

  return (
    <WebSocketContext.Provider value={{ isConnected, lastAlert, alertHistory, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocketContext must be used within a WebSocketProvider");
  }
  return context;
};
