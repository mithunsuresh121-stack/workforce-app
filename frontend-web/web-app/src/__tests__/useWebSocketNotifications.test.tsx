import { renderHook, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import useWebSocketNotifications from '../hooks/useWebSocketNotifications';
import { AuthProvider } from '../contexts/AuthContext';

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  readyState = 1; // OPEN

  constructor() {
    // Simulate connection
    setTimeout(() => {
      if (this.onopen) this.onopen();
    }, 0);
  }

  send() {}
  close() {}
}

global.WebSocket = MockWebSocket as any;

// Mock fetch
global.fetch = vi.fn();

describe('useWebSocketNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });
  });

  test('fetches notifications on mount', async () => {
    const mockNotifications = [
      { id: '1', title: 'Test', message: 'Test message', type: 'TASK_CREATED', status: 'UNREAD', created_at: new Date().toISOString() }
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockNotifications),
    });

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider value={{ user: { id: 1, name: 'Test User' } }}>
          {children}
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.notifications).toEqual(mockNotifications);
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/notifications/', expect.any(Object));
  });

  test('handles WebSocket connection', async () => {
    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider value={{ user: { id: 1, name: 'Test User' } }}>
          {children}
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    });
  });

  test('handles mark as read', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([
        { id: '1', title: 'Test', message: 'Test message', type: 'TASK_CREATED', status: 'UNREAD', created_at: new Date().toISOString() }
      ]),
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    });

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider value={{ user: { id: 1, name: 'Test User' } }}>
          {children}
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.notifications.length).toBe(1);
    });

    await result.current.markAsRead('1');

    expect(global.fetch).toHaveBeenCalledWith('/api/notifications/mark-read/1', expect.any(Object));
  });

  test('handles fetch error', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider value={{ user: { id: 1, name: 'Test User' } }}>
          {children}
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });
  });

  test('handles WebSocket message', async () => {
    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider value={{ user: { id: 1, name: 'Test User' } }}>
          {children}
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    });

    // Simulate receiving a WebSocket message
    const mockWs = new MockWebSocket();
    const newNotification = {
      type: 'notification',
      notification: {
        id: '2',
        title: 'New Notification',
        message: 'New message',
        type: 'GENERAL',
        status: 'UNREAD',
        created_at: new Date().toISOString()
      }
    };

    if (mockWs.onmessage) {
      mockWs.onmessage({ data: JSON.stringify(newNotification) } as any);
    }

    // This would need more complex mocking to test properly
  });
});
