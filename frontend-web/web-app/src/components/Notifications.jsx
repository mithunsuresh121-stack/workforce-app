import React, { useState, useEffect } from 'react';
import {
  Box,
  IconButton,
  Badge,
  List,
  ListItem,
  ListItemText,
  Typography,
  Divider,
  CircularProgress,
  Tooltip
} from '@mui/material';
import { BellIcon, CheckIcon } from '@heroicons/react/24/outline';
import { api, useAuth } from '../contexts/AuthContext';

const Notifications = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data);
      const unread = response.data.filter(n => n.status === 'UNREAD').length;
      setUnreadCount(unread);
    } catch (err) {
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/mark-read/${notificationId}`);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId ? { ...n, status: 'READ' } : n
        )
      );
      setUnreadCount((count) => Math.max(count - 1, 0));
    } catch (err) {
      setError('Failed to mark notification as read');
    }
  };

  return (
    <Box sx={{ position: 'relative' }}>
      <Tooltip title="Notifications">
        <IconButton
          color="inherit"
          onClick={() => setOpen(!open)}
          aria-label="show notifications"
          size="large"
        >
          <Badge badgeContent={unreadCount} color="error">
            <BellIcon style={{ width: 24, height: 24 }} />
          </Badge>
        </IconButton>
      </Tooltip>
      {open && (
        <Box
          sx={{
            position: 'absolute',
            right: 0,
            mt: 1,
            width: 320,
            maxHeight: 400,
            bgcolor: 'background.paper',
            boxShadow: 3,
            borderRadius: 1,
            overflowY: 'auto',
            zIndex: 1300,
          }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : error ? (
            <Typography sx={{ p: 2, color: 'error.main' }}>{error}</Typography>
          ) : notifications.length === 0 ? (
            <Typography sx={{ p: 2 }}>No notifications</Typography>
          ) : (
            <List>
              {notifications.map((notification) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    button
                    onClick={() => markAsRead(notification.id)}
                    sx={{
                      bgcolor:
                        notification.status === 'UNREAD'
                          ? 'action.selected'
                          : 'inherit',
                    }}
                  >
                    <ListItemText
                      primary={notification.title}
                      secondary={notification.message}
                      primaryTypographyProps={{
                        fontWeight:
                          notification.status === 'UNREAD' ? 'bold' : 'normal',
                      }}
                    />
                    {notification.status === 'UNREAD' && (
                      <CheckIcon style={{ width: 20, height: 20, color: 'green' }} />
                    )}
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>
      )}
    </Box>
  );
};

export default Notifications;
