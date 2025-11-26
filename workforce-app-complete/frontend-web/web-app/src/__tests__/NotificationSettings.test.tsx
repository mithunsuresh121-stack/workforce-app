import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NotificationSettings from '../pages/NotificationSettings';
import { AuthProvider } from '../contexts/AuthContext';
import { server } from '../setupTests';
import { http, HttpResponse } from 'msw';

describe('NotificationSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders notification settings form', async () => {
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
  });

  test('handles save error', async () => {
    // Override POST to return error
    server.use(
      http.post('/notification-preferences/', () => {
        return HttpResponse.json({}, { status: 500 });
      })
    );

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

    const emailToggle = screen.getByTestId('toggle-email_notifications');
    fireEvent.click(emailToggle);
    expect(emailToggle).toHaveProperty('checked', false);

    const websocketToggle = screen.getByTestId('toggle-websocket_notifications');
    fireEvent.click(websocketToggle);
    expect(websocketToggle).toHaveProperty('checked', false);
  });
});
