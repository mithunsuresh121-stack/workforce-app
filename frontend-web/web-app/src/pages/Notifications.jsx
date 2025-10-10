import React, { useEffect, useState } from 'react';
import { api, useAuth } from '../contexts/AuthContext';
import { BellIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

const Notifications = () => {
  const { user: currentUser } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await api.get('/notifications/');
        setNotifications(response.data);
      } catch (err) {
        setError('Failed to load notifications.');
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();

    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/mark-read/${notificationId}`);
      setNotifications(notifications.map(n =>
        n.id === notificationId ? { ...n, status: 'READ' } : n
      ));
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (activeTab === 'all') return true;
    if (activeTab === 'tasks') return notification.type.startsWith('TASK_');
    if (activeTab === 'shifts') return notification.type.startsWith('SHIFT_');
    if (activeTab === 'general') return !notification.type.startsWith('TASK_') && !notification.type.startsWith('SHIFT_');
    return true;
  });

  const unreadCount = notifications.filter(n => n.status === 'UNREAD').length;

  if (loading) return <div>Loading notifications...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Notifications</h1>
        {unreadCount > 0 && (
          <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm">
            {unreadCount} unread
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6">
        {[
          { key: 'all', label: 'All' },
          { key: 'tasks', label: 'Tasks' },
          { key: 'shifts', label: 'Shifts' },
          { key: 'general', label: 'General' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-accent-500 text-white'
                : 'text-neutral-600 hover:bg-neutral-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12">
            <BellIcon className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
            <p className="text-neutral-500">No notifications found.</p>
          </div>
        ) : (
          filteredNotifications.map(notification => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border ${
                notification.status === 'UNREAD'
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-white border-neutral-200'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-neutral-900">{notification.title}</h3>
                  <p className="text-neutral-600 mt-1">{notification.message}</p>
                  <p className="text-sm text-neutral-400 mt-2">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {notification.status === 'UNREAD' && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                      title="Mark as read"
                    >
                      <CheckIcon className="w-4 h-4" />
                    </button>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    notification.type.startsWith('TASK_') ? 'bg-green-100 text-green-700' :
                    notification.type.startsWith('SHIFT_') ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {notification.type.replace('_', ' ').toLowerCase()}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;
