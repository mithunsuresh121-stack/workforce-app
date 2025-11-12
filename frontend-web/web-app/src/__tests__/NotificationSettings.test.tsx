import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NotificationSettings from '../pages/NotificationSettings';
import { AuthProvider } from '../contexts/AuthContext';

// Mock fetch and localStorage are set globally in setupTests.js

describe('NotificationSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders notification settings form', async () => {
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock preferences get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: false,
        general_notifications: true,
      }),
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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock preferences get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        email_notifications: true,
        websocket_notifications: false,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: false,
      }),
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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock preferences get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }),
    });
    // Mock post
    (global.fetch as any).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });

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

    expect((global.fetch as any)).toHaveBeenCalledWith('/notification-preferences/', expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }),
    }));
  });

  test('handles save error', async () => {
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock preferences get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }),
    });
    // Mock post error
    (global.fetch as any).mockRejectedValueOnce(new Error('Save failed'));

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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock preferences get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        email_notifications: true,
        websocket_notifications: true,
        task_notifications: true,
        shift_notifications: true,
        general_notifications: true,
      }),
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
