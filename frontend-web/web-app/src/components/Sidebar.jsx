import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, UserIcon, UsersIcon, ClipboardIcon, CalendarIcon, XMarkIcon } from '@heroicons/react/24/outline';

const Sidebar = ({ onClose }) => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
    { path: '/profile', label: 'Profile', icon: UserIcon },
    { path: '/directory', label: 'Directory', icon: UsersIcon },
    { path: '/tasks', label: 'Tasks', icon: ClipboardIcon },
    { path: '/leave', label: 'Leave', icon: CalendarIcon },
  ];

  return (
    <div className="w-64 bg-white shadow-lg flex flex-col h-full">
      {/* Header with logo and close button for mobile */}
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Workforce App</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 lg:hidden"
          >
            <XMarkIcon className="w-6 h-6" />
          </Button>
        )}
      </Card>

      {/* Navigation menu */}
      <nav className="flex-1 mt-4">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            onClick={onClose} // Close sidebar on mobile when navigating
            className={`flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 transition-colors duration-200 ${
              location.pathname === item.path
                ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600'
                : 'hover:bg-gray-50'
            }`}
          >
            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Footer section - can add user info or logout here later */}
      <div className="p-4 border-t">
        <p className="text-xs text-gray-500 text-center">
          © 2023 Workforce App
        </p>
      </Card>
    </Card>
  );
};

export default Sidebar;
