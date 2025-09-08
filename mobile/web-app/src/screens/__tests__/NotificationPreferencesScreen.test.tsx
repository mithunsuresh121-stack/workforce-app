import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import NotificationPreferencesScreen from '../NotificationPreferencesScreen';
import { getNotificationPreferences, updateNotificationPreferences } from '../../lib/api';

// Mock the API functions
jest.mock('../../lib/api', () => ({
  getNotificationPreferences: jest.fn(),
  updateNotificationPreferences: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock Material-UI ThemeProvider
jest.mock('@mui/material/styles', () => ({
  ...jest.requireActual('@mui/material/styles'),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('NotificationPreferencesScreen', () => {
  const mockPreferences = {
    mute_all: false,
    digest_mode: 'immediate',
    push_enabled: true,
    notification_types: {
      TASK_ASSIGNED: true,
      SHIFT_SCHEDULED: true,
      SYSTEM_MESSAGE: true,
      ADMIN_MESSAGE: true,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue('mock-token');
    (getNotificationPreferences as jest.Mock).mockResolvedValue({
      preferences: mockPreferences,
    });
  });

  test('renders loading state initially', () => {
    render(<NotificationPreferencesScreen />);
    expect(screen.getByText('Loading preferences...')).toBeInTheDocument();
  });

  test('renders screen title correctly', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
    });
  });

  test('renders general settings section', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      expect(screen.getByText('General Settings')).toBeInTheDocument();
      expect(screen.getByText('Mute All Notifications')).toBeInTheDocument();
      expect(screen.getByText('Push Notifications')).toBeInTheDocument();
      expect(screen.getAllByText('Digest Mode')).toHaveLength(2); // Label and span
    });
  });

  test('renders notification types section', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      expect(screen.getByText('Notification Types')).toBeInTheDocument();
      expect(screen.getByText('Task Assignments')).toBeInTheDocument();
      expect(screen.getByText('Shift Schedules')).toBeInTheDocument();
      expect(screen.getByText('System Messages')).toBeInTheDocument();
      expect(screen.getByText('Admin Messages')).toBeInTheDocument();
    });
  });

  test('renders save button', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Save Preferences' })).toBeInTheDocument();
    });
  });

  test('mute all toggle updates state correctly', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const muteAllSwitch = screen.getByRole('switch', { name: /mute all notifications/i });
      expect(muteAllSwitch).not.toBeChecked();
    });

    const muteAllSwitch = screen.getByRole('switch', { name: /mute all notifications/i });

    await act(async () => {
      fireEvent.click(muteAllSwitch);
    });

    await waitFor(() => {
      expect(muteAllSwitch).toBeChecked();
    });
  });

  test('push notifications toggle updates state correctly', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const pushSwitch = screen.getByRole('switch', { name: /push notifications/i });
      expect(pushSwitch).toBeChecked();
    });

    const pushSwitch = screen.getByRole('switch', { name: /push notifications/i });

    await act(async () => {
      fireEvent.click(pushSwitch);
    });

    await waitFor(() => {
      expect(pushSwitch).not.toBeChecked();
    });
  });

  test('digest mode select updates state correctly', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const selectElement = screen.getByRole('combobox');
      expect(selectElement).toHaveTextContent('Immediate');
    });

    const selectElement = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.mouseDown(selectElement);
    });

    const dailyOption = screen.getByText('Daily Digest');

    await act(async () => {
      fireEvent.click(dailyOption);
    });

    await waitFor(() => {
      expect(selectElement).toHaveTextContent('Daily Digest');
    });
  });

  test('notification type toggles update state correctly', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const taskSwitch = screen.getByRole('switch', { name: /task assignments/i });
      expect(taskSwitch).toBeChecked();
    });

    const taskSwitch = screen.getByRole('switch', { name: /task assignments/i });

    await act(async () => {
      fireEvent.click(taskSwitch);
    });

    await waitFor(() => {
      expect(taskSwitch).not.toBeChecked();
    });
  });

  test('save button shows loading state during save', async () => {
    (updateNotificationPreferences as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
    );

    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const saveButton = screen.getByRole('button', { name: 'Save Preferences' });
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Saving...' })).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Save Preferences' })).toBeInTheDocument();
    });
  });

  test('shows success message after successful save', async () => {
    (updateNotificationPreferences as jest.Mock).mockResolvedValue({ success: true });

    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const saveButton = screen.getByRole('button', { name: 'Save Preferences' });
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Preferences saved successfully!')).toBeInTheDocument();
    });
  });

  test('shows error message when save fails', async () => {
    (updateNotificationPreferences as jest.Mock).mockRejectedValue(new Error('Save failed'));

    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const saveButton = screen.getByRole('button', { name: 'Save Preferences' });
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to save preferences')).toBeInTheDocument();
    });
  });

  test('disables notification toggles when mute all is enabled', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const muteAllSwitch = screen.getByRole('switch', { name: /mute all notifications/i });

      act(() => {
        fireEvent.click(muteAllSwitch);
      });
    });

    await waitFor(() => {
      const pushSwitch = screen.getByRole('switch', { name: /push notifications/i });
      const taskSwitch = screen.getByRole('switch', { name: /task assignments/i });
      expect(pushSwitch).toBeDisabled();
      expect(taskSwitch).toBeDisabled();
    });
  });

  test('digest mode select is disabled when mute all is enabled', async () => {
    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const muteAllSwitch = screen.getByRole('switch', { name: /mute all notifications/i });

      act(() => {
        fireEvent.click(muteAllSwitch);
      });
    });

    await waitFor(() => {
      const selectElement = screen.getByRole('combobox');
      expect(selectElement).toHaveAttribute('aria-disabled', 'true');
    });
  });

  test('handles API error during load', async () => {
    (getNotificationPreferences as jest.Mock).mockRejectedValue(new Error('Load failed'));

    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load preferences')).toBeInTheDocument();
    });
  });

  test('calls API functions with correct parameters', async () => {
    (updateNotificationPreferences as jest.Mock).mockResolvedValue({ success: true });

    render(<NotificationPreferencesScreen />);

    await waitFor(() => {
      const saveButton = screen.getByRole('button', { name: 'Save Preferences' });
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(updateNotificationPreferences).toHaveBeenCalledWith(mockPreferences);
    });
  });
});
