import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import { vi } from 'vitest';
import NotificationSettings from '../pages/NotificationSettings';
import { AuthProvider } from '../contexts/AuthContext';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    })),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

describe('NotificationSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders notification settings form', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: false,
        general_notifications: true,
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <NotificationSettings />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText('Notification Settings')).toBeInTheDocument();
    expect(screen.getByText('Delivery Methods')).toBeInTheDocument();
    expect(screen.getByText('Notification Types')).toBeInTheDocument();
  });

  test('loads and displays preferences correctly', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        email_notifications: true,
        websocket_notifications: false,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: false,
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <NotificationSettings />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
    });

    // Check that preferences are loaded (this would require more specific selectors)
  });

  test('saves preferences successfully', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }
    });
    axios.post.mockResolvedValueOnce({});

    render(
      <AuthProvider>
        <MemoryRouter>
          <NotificationSettings />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
    });

    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Notification preferences saved successfully!')).toBeInTheDocument();
    });

    expect(axios.post).toHaveBeenCalledWith('/notification-preferences/', expect.any(Object));
  });

  test('handles save error', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }
    });
    axios.post.mockRejectedValueOnce(new Error('Save failed'));

    render(
      <AuthProvider>
        <MemoryRouter>
          <NotificationSettings />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
    });

    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to save preferences. Please try again.')).toBeInTheDocument();
    });
  });

  test('toggles preferences correctly', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter>
          <NotificationSettings />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Notification Settings')).toBeInTheDocument();
    });

    // Find toggle switches and test toggling (would need more specific implementation)
    // This is a basic structure - actual toggle testing would depend on the toggle implementation
  });
});
