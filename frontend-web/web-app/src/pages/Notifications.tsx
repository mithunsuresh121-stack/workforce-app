import React, { useState, useEffect } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import { Link } from 'react-router-dom';
import { BellIcon, CheckIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import useWebSocketNotifications from '../hooks/useWebSocketNotifications';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  status: 'READ' | 'UNREAD';
  created_at: string;
}

const Notifications: React.FC = () => {
  const { notifications, loading, error, markAsRead, connected } = useWebSocketNotifications();
  const [activeTab, setActiveTab] = useState('all');
  const [displayedNotifications, setDisplayedNotifications] = useState<Notification[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    // Reset pagination when notifications change
    setDisplayedNotifications(notifications.slice(0, itemsPerPage));
    setPage(1);
    setHasMore(notifications.length > itemsPerPage);
  }, [notifications]);

  const loadMore = () => {
    const nextPage = page + 1;
    const startIndex = (nextPage - 1) * itemsPerPage;
    const endIndex = nextPage * itemsPerPage;
    const newItems = notifications.slice(startIndex, endIndex);

    if (newItems.length > 0) {
      setDisplayedNotifications(prev => [...prev, ...newItems]);
      setPage(nextPage);
      setHasMore(endIndex < notifications.length);
    } else {
      setHasMore(false);
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead(notificationId);
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const filteredNotifications = displayedNotifications.filter(notification => {
    if (activeTab === 'all') return true;
    if (activeTab === 'tasks') return notification.type.startsWith('TASK_');
    if (activeTab === 'shifts') return notification.type.startsWith('SHIFT_');
    if (activeTab === 'general') return !notification.type.startsWith('TASK_') && !notification.type.startsWith('SHIFT_');
    return true;
  });

  const unreadCount = notifications.filter(n => n.status === 'UNREAD').length;

  if (loading) return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-500"></div></div>;
  if (error) return <div className="text-center py-12 text-red-600">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-semibold text-neutral-900">Notifications</h1>
          <div className="flex items-center space-x-2">
            {connected ? (
              <span className="flex items-center text-green-600 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                Live
              </span>
            ) : (
              <span className="flex items-center text-neutral-400 text-sm">
                <div className="w-2 h-2 bg-neutral-400 rounded-full mr-1"></div>
                Offline
              </span>
            )}
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm">
                {unreadCount} unread
              </span>
            )}
          </div>
        </div>
        <Link
          to="/notification-settings"
          className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-lg hover:bg-neutral-50 transition-colors"
        >
          <Cog6ToothIcon className="w-4 h-4 mr-2" />
          Settings
        </Link>
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
      <InfiniteScroll
        dataLength={filteredNotifications.length}
        next={loadMore}
        hasMore={hasMore}
        loader={<div className="text-center py-4">Loading more notifications...</div>}
        endMessage={
          <div className="text-center py-8 text-neutral-500">
            {filteredNotifications.length === 0 ? (
              <>
                <BellIcon className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                <p>No notifications found.</p>
              </>
            ) : (
              <p>You've seen all notifications.</p>
            )}
          </div>
        }
      >
        <div className="space-y-4">
          {filteredNotifications.map(notification => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border transition-all ${
                notification.status === 'UNREAD'
                  ? 'bg-blue-50 border-blue-200 shadow-sm'
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
                      onClick={() => handleMarkAsRead(notification.id)}
                      className="p-1 text-blue-600 hover:bg-blue-100 rounded transition-colors"
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
          ))}
        </div>
      </InfiniteScroll>
    </div>
  );
};

export default Notifications;
