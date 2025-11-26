import { useState, useEffect, useRef } from 'react';

export default function useWebSocket(url, token, onMessage) {
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const reconnectAttempts = useRef(0);
  const maxReconnects = 5;
  const reconnectDelay = useRef(1000);

  useEffect(() => {
    const connect = () => {
      const websocket = new WebSocket(`${url}?token=${token}`);

      websocket.onopen = () => {
        setConnected(true);
        reconnectAttempts.current = 0;
        reconnectDelay.current = 1000;
        setWs(websocket);
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      websocket.onclose = (event) => {
        setConnected(false);
        setWs(null);

        if (reconnectAttempts.current < maxReconnects) {
          setTimeout(() => {
            reconnectAttempts.current += 1;
            reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000);
            connect();
          }, reconnectDelay.current);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [url, token]);

  const send = (message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  };

  return { send, connected };
}
