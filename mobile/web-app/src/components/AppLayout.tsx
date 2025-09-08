import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import { getNotifications } from '../lib/api';

const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
      const unread = data.filter((n: any) => n.status === 'UNREAD').length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Failed to fetch notifications in AppLayout:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleUnreadCountChange = (count: number) => {
    setUnreadCount(count);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transition-transform duration-300 ease-in-out lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        dark:bg-gray-900
      `}>
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="flex flex-col flex-1 lg:ml-64">
        {/* Navbar */}
        <Navbar
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          unreadCount={unreadCount}
          onUnreadCountChange={handleUnreadCountChange}
        />
        
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50 dark:bg-gray-900">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default AppLayout;
