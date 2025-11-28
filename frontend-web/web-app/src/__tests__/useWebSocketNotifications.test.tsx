import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import useWebSocketNotifications from '../hooks/useWebSocketNotifications';
import { AuthProvider } from '../contexts/AuthContext';
import { test, expect, vi, beforeEach, afterEach, describe } from 'vitest';
import { server } from '../setupTests';
import { http, HttpResponse } from 'msw';

// Mock useAuth to return a user with token synchronously
const mockUser = { id: '1', token: 'mock-token' };
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    loading: false
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Simplified WebSocket mock
class MockWebSocket {
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState = 0; // CONNECTING
  url: string;
  close = vi.fn();
  send = vi.fn();
  addEventListener = vi.fn();
  removeEventListener = vi.fn();

  dispatchEvent(event: Event): boolean {
    switch (event.type) {
      case 'open':
        this.readyState = 1; // OPEN
        if (this.onopen) this.onopen(event);
        break;
      case 'message':
        if (this.onmessage) this.onmessage(event as MessageEvent);
        break;
      case 'close':
        this.readyState = 3; // CLOSED
        if (this.onclose) this.onclose(event as CloseEvent);
        break;
      case 'error':
        if (this.onerror) this.onerror(event);
        break;
    }
    return true;
  }

  constructor(url: string) {
    this.url = url;
    // Store reference for testing
    (global as any).lastMockWebSocket = this;
    // Auto-dispatch open event after a short delay to simulate connection (fixes timing issue in Vitest 3+)
    setTimeout(() => {
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }
}

vi.stubGlobal('WebSocket', MockWebSocket);

// WebSocket, fetch, and localStorage are mocked globally in setupTests.js

describe('useWebSocketNotifications', () => {
  const queryClient = new QueryClient();

  beforeEach(() => {
    vi.clearAllMocks();
    server.resetHandlers();
    (global.localStorage.getItem as any).mockReturnValue('mock-token');
  });

  afterEach(() => {
    server.listen({ onUnhandledRequest: 'bypass' });
  });

  test('fetches notifications on mount', async () => {
    server.use(
      http.get('http://localhost:3000/api/notifications/', () => {
        return HttpResponse.json([]);
      })
    );

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
      expect(result.current.notifications).toHaveLength(0);
    });
  });

  test('handles WebSocket connection', async () => {
    // Override MSW handler to return empty array for notifications
    server.use(
      http.get('http://localhost:3000/api/notifications/', () => {
        return HttpResponse.json([]);
      })
    );

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
      expect(result.current.notifications).toHaveLength(0);
    });

    // Wait for WebSocket to be instantiated
    await waitFor(() => {
      expect((global as any).lastMockWebSocket).toBeDefined();
    });

    const mockWS = (global as any).lastMockWebSocket;

    // Wait for onopen handler to be assigned
    await waitFor(() => {
      expect(mockWS.onopen).toBeDefined();
    });

    // The auto-dispatch in constructor should have triggered; but add explicit act for React state update
    await act(async () => {
      // Flush any pending updates
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Wait for connected to be true with increased timeout for async state
    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    }, { timeout: 3000 });
  });

  test('handles mark as read', async () => {
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
    });

    // Override POST to return success
    server.use(
      http.post('http://localhost:3000/api/notifications/mark-read/:id', () => {
        return HttpResponse.json({});
      })
    );

    await expect(result.current.markAsRead('1')).resolves.toBeUndefined();
  });

  test('handles fetch error', async () => {
    // Override GET to return error
    server.use(
      http.get('http://localhost:3000/api/notifications/', () => {
        return HttpResponse.json({}, { status: 500 });
      })
    );

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
      expect(result.current.error).toBe('Failed to load notifications');
    });
  });

  test('handles mark as read error', async () => {
    // Override POST to return error
    server.use(
      http.post('http://localhost:3000/api/notifications/mark-read/:id', () => {
        return HttpResponse.json({}, { status: 500 });
      })
    );

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
    });

    await expect(result.current.markAsRead('1')).rejects.toThrow('Failed to mark as read');
  });

  test('handles WebSocket message', async () => {
    // Override MSW handler to return empty array for notifications
    server.use(
      http.get('http://localhost:3000/api/notifications/', () => {
        return HttpResponse.json([]);
      })
    );

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
      expect(result.current.notifications).toHaveLength(0);
    });

    // Wait for WebSocket to be instantiated
    await waitFor(() => {
      expect((global as any).lastMockWebSocket).toBeDefined();
    });

    const mockWS = (global as any).lastMockWebSocket;

    // Wait for handlers to be set
    await waitFor(() => {
      expect(mockWS.onopen).toBeDefined();
      expect(mockWS.onmessage).toBeDefined();
    });

    // The auto-dispatch should have set connected; add explicit for safety
    await act(async () => {
      if (mockWS && mockWS.onopen) {
        mockWS.onopen(new Event('open'));
      }
    });

    // Wait for connected to be true
    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    }, { timeout: 3000 });

    // Simulate receiving a WebSocket message
    const newNotification = {
      type: 'notification',
      notification: {
        id: '2',
        title: 'New Notification',
        message: 'New message',
        type: 'GENERAL',
        status: 'UNREAD',
        created_at: '2023-01-01T00:00:00.000Z'
      }
    };

    // Trigger the onmessage callback directly
    await act(async () => {
      if (mockWS && mockWS.onmessage) {
        mockWS.onmessage({ data: JSON.stringify(newNotification) } as MessageEvent);
      }
    });

    // Force a re-render to ensure state updates are reflected
    await act(async () => {
      // Small delay to allow state update
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Wait for the notification to be added
    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].id).toBe('2');
    }, { timeout: 3000 });
  });
});
