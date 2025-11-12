import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import useWebSocketNotifications from '../hooks/useWebSocketNotifications';
import { AuthProvider } from '../contexts/AuthContext';
import { test, expect, vi, beforeEach, describe } from 'vitest';

// Mock useAuth to return a user synchronously
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', email: 'test@example.com', name: 'Test User', company_id: '1', role: 'EMPLOYEE' }
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Mock WebSocket
class MockWebSocket {
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState = 1; // OPEN

  constructor(url: string) {
    // Store reference for test access
    (global as any).lastMockWebSocket = this;
  }

  close() {
    this.readyState = 3; // CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  send(data: string) {
    // Mock send
  }
}

vi.stubGlobal('WebSocket', MockWebSocket);

// WebSocket, fetch, and localStorage are mocked globally in setupTests.js

describe('useWebSocketNotifications', () => {
  const queryClient = new QueryClient();

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

    // Mock localStorage token
    (global.localStorage.getItem as any).mockReturnValue('fake-token');

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockNotifications),
    });

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.notifications).toEqual(mockNotifications);
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/notifications/', expect.any(Object));
  });

  test('handles WebSocket connection', async () => {
    // Mock localStorage token
    (global.localStorage.getItem as any).mockReturnValue('fake-token');

    // Mock /api/notifications/ to return empty array
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      ),
    });

    // Wait for fetch to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Simulate WebSocket open
    const mockWS = (global as any).lastMockWebSocket;
    if (mockWS && mockWS.onopen) {
      mockWS.onopen(new Event('open'));
    }

    // Wait for connected to be true
    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    });
  });

  test('handles mark as read', async () => {
    // Mock localStorage token
    (global.localStorage.getItem as any).mockReturnValue('fake-token');

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
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.notifications.length).toBe(1);
    });

    await result.current.markAsRead('1');

    expect(global.fetch).toHaveBeenCalledWith('/api/notifications/mark-read/1', expect.any(Object));
  });

  test('handles fetch error', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      ),
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Network error');
    });
  });

  test('handles WebSocket message', async () => {
    // Mock localStorage token
    (global.localStorage.getItem as any).mockReturnValue('fake-token');

    // Mock initial /api/notifications/ to return empty array
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    const { result } = renderHook(() => useWebSocketNotifications(), {
      wrapper: ({ children }) => (
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      ),
    });

    // Wait for fetch to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Simulate WebSocket open
    const mockWS = (global as any).lastMockWebSocket;
    if (mockWS && mockWS.onopen) {
      mockWS.onopen(new Event('open'));
    }

    // Wait for connected to be true
    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    });

    // Simulate receiving a WebSocket message
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

    // Trigger the onmessage callback on the last mocked WebSocket instance
    if (mockWS && mockWS.onmessage) {
      mockWS.onmessage({ data: JSON.stringify(newNotification) } as MessageEvent);
    }

    // Wait for the notification to be added
    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].id).toBe('2');
    });
  });
});
