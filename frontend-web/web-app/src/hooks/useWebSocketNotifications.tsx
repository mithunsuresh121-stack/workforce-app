import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  status: 'READ' | 'UNREAD';
  created_at: string;
}

interface UseWebSocketNotificationsReturn {
  notifications: Notification[];
  loading: boolean;
  error: string | null;
  markAsRead: (id: string) => Promise<void>;
  connected: boolean;
}

export default function useWebSocketNotifications(): UseWebSocketNotificationsReturn {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnects = 5;
  const reconnectDelay = useRef(1000);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/notifications/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch notifications');
      const data = await response.json();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (id: string) => {
    try {
      const response = await fetch(`/api/notifications/mark-read/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to mark as read');
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, status: 'READ' } : n)
      );
    } catch (err) {
      console.error('Failed to mark as read:', err);
      throw err;
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (!user) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

    ws.onopen = () => {
      setConnected(true);
      reconnectAttempts.current = 0;
      reconnectDelay.current = 1000;
      wsRef.current = ws;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          // Add new notification to the list
          setNotifications(prev => [data.notification, ...prev]);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;

      if (reconnectAttempts.current < maxReconnects) {
        setTimeout(() => {
          reconnectAttempts.current += 1;
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000);
          connectWebSocket();
        }, reconnectDelay.current);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [user]);

  useEffect(() => {
    fetchNotifications();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchNotifications, connectWebSocket]);

  return {
    notifications,
    loading,
    error,
    markAsRead,
    connected,
  };
}
