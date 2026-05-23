import { useEffect, useRef, useState, useCallback } from "react";

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<Event | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectDelayRef = useRef(1000); // 1 sec initial reconnect delay

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = url.startsWith("ws") ? url : `${protocol}//${host}${url}`;

    console.log("WebSocket connecting to:", wsUrl);
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected.");
      setIsConnected(true);
      setError(null);
      reconnectDelayRef.current = 1000; // Reset delay
    };

    socket.onmessage = (event) => {
      try {
        const data = jsonParseSafe(event.data);
        setLastMessage(data);
        setMessages((prev) => [data, ...prev].slice(0, 100)); // Cap history
      } catch (err) {
        console.error("WebSocket message parsing error:", err);
      }
    };

    socket.onclose = (event) => {
      console.log("WebSocket disconnected. Close code:", event.code);
      setIsConnected(false);
      
      // Auto reconnect unless closed intentionally
      if (event.code !== 1000) {
        scheduleReconnect();
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket encountered error:", err);
      setError(err);
    };
  }, [url]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) return;

    const delay = reconnectDelayRef.current;
    console.log(`Scheduling WebSocket reconnect in ${delay}ms`);

    reconnectTimeoutRef.current = window.setTimeout(() => {
      reconnectTimeoutRef.current = null;
      // Exponential backoff
      reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 30000); // Max 30 seconds
      connect();
    }, delay);
  }, [connect]);

  const sendMessage = useCallback((msg: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msg));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000); // Intentional close
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    messages,
    isConnected,
    lastMessage,
    error,
    sendMessage,
  };
}

function jsonParseSafe(str: string) {
  try {
    return JSON.parse(str);
  } catch (e) {
    return str;
  }
}
