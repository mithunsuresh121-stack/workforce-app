import React, { useState, useEffect, ChangeEvent } from 'react';
import {
  Container,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Box,
  Alert,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import { getNotificationPreferences, updateNotificationPreferences } from '../lib/api';

interface NotificationPreferences {
  mute_all: boolean;
  digest_mode: string;
  push_enabled: boolean;
  notification_types: {
    TASK_ASSIGNED: boolean;
    SHIFT_SCHEDULED: boolean;
    SYSTEM_MESSAGE: boolean;
    ADMIN_MESSAGE: boolean;
  };
}

const NotificationPreferencesScreen: React.FC = () => {
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    mute_all: false,
    digest_mode: 'immediate',
    push_enabled: true,
    notification_types: {
      TASK_ASSIGNED: true,
      SHIFT_SCHEDULED: true,
      SYSTEM_MESSAGE: true,
      ADMIN_MESSAGE: true,
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await getNotificationPreferences();
      if (response && response.preferences) {
        setPreferences(response.preferences);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      setMessage({ type: 'error', text: 'Failed to load preferences' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const response = await updateNotificationPreferences(preferences);
      if (response) {
        setMessage({ type: 'success', text: 'Preferences saved successfully!' });
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage({ type: 'error', text: 'Failed to save preferences' });
    } finally {
      setSaving(false);
    }
  };

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleNotificationTypeChange = (type: keyof NotificationPreferences['notification_types'], value: boolean) => {
    setPreferences(prev => ({
      ...prev,
      notification_types: {
        ...prev.notification_types,
        [type]: value,
      },
    }));
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Notification Preferences
        </Typography>
        <Paper sx={{ p: 3 }}>
          <Typography>Loading preferences...</Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Notification Preferences
      </Typography>

      {message && (
        <Alert severity={message.type} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* General Settings */}
          <Box>
            <Typography variant="h6" gutterBottom>
              General Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Box>

          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.mute_all}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => handlePreferenceChange('mute_all', e.target.checked)}
                  color="primary"
                />
              }
              label="Mute All Notifications"
            />
            <Typography variant="body2" color="text.secondary">
              Disable all notifications when enabled
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
            <Box sx={{ flex: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.push_enabled}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handlePreferenceChange('push_enabled', e.target.checked)}
                    color="primary"
                    disabled={preferences.mute_all}
                  />
                }
                label="Push Notifications"
              />
              <Typography variant="body2" color="text.secondary">
                Receive push notifications on your device
              </Typography>
            </Box>

            <Box sx={{ flex: 1 }}>
              <FormControl fullWidth disabled={preferences.mute_all}>
                <InputLabel>Digest Mode</InputLabel>
                <Select
                  value={preferences.digest_mode}
                  label="Digest Mode"
                  onChange={(e) => handlePreferenceChange('digest_mode', e.target.value as string)}
                >
                  <MenuItem value="immediate">Immediate</MenuItem>
                  <MenuItem value="daily">Daily Digest</MenuItem>
                  <MenuItem value="weekly">Weekly Digest</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>

          {/* Notification Types */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Notification Types
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            <Card variant="outlined">
              <CardContent>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.notification_types.TASK_ASSIGNED}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleNotificationTypeChange('TASK_ASSIGNED', e.target.checked)}
                      color="primary"
                      disabled={preferences.mute_all}
                    />
                  }
                  label="Task Assignments"
                />
                <Typography variant="body2" color="text.secondary">
                  When tasks are assigned to you
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.notification_types.SHIFT_SCHEDULED}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleNotificationTypeChange('SHIFT_SCHEDULED', e.target.checked)}
                      color="primary"
                      disabled={preferences.mute_all}
                    />
                  }
                  label="Shift Schedules"
                />
                <Typography variant="body2" color="text.secondary">
                  When shifts are scheduled for you
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.notification_types.SYSTEM_MESSAGE}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleNotificationTypeChange('SYSTEM_MESSAGE', e.target.checked)}
                      color="primary"
                      disabled={preferences.mute_all}
                    />
                  }
                  label="System Messages"
                />
                <Typography variant="body2" color="text.secondary">
                  Important system announcements
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.notification_types.ADMIN_MESSAGE}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => handleNotificationTypeChange('ADMIN_MESSAGE', e.target.checked)}
                      color="primary"
                      disabled={preferences.mute_all}
                    />
                  }
                  label="Admin Messages"
                />
                <Typography variant="body2" color="text.secondary">
                  Messages from administrators
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Save Button */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              disabled={saving}
              size="large"
            >
              {saving ? 'Saving...' : 'Save Preferences'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotificationPreferencesScreen;
