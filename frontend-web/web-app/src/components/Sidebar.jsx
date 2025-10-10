import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  UserIcon,
  UsersIcon,
  ClipboardIcon,
  CalendarIcon,
  XMarkIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  ClockIcon,
  BellIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = ({ onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  // Filter menu items based on user role
  const allMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
    { path: '/profile', label: 'Profile', icon: UserIcon },
    { path: '/directory', label: 'Directory', icon: UsersIcon },
    { path: '/tasks', label: 'Tasks', icon: ClipboardIcon },
    { path: '/shifts', label: 'Shifts', icon: ClockIcon },
    { path: '/notifications', label: 'Notifications', icon: BellIcon },
    { path: '/leave', label: 'Leave', icon: CalendarIcon },
    { path: '/manager-approvals', label: 'Manager Approvals', icon: CheckCircleIcon },
  ];

  // Only show Directory and Manager Approvals for non-Employee roles
  const menuItems = allMenuItems.filter(item => {
    if (item.path === '/directory' || item.path === '/manager-approvals') {
      return user?.role !== 'Employee';
    }
    return true;
  });

  return (
    <div className="w-64 bg-surface flex flex-col h-full border-r border-border">
      {/* Header with logo and close button for mobile */}
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-accent-500 rounded-lg flex items-center justify-center">
            <ChartBarIcon className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-lg font-semibold text-neutral-900">Workforce</h2>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 lg:hidden transition-colors duration-200"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation menu */}
      <nav className="flex-1 px-3 py-6">
        <div className="space-y-1">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose} // Close sidebar on mobile when navigating
                className={`flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 group ${
                  isActive
                    ? 'bg-accent-50 text-accent-700 border border-accent-200'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                }`}
              >
                <item.icon className={`w-5 h-5 mr-3 flex-shrink-0 transition-colors duration-200 ${
                  isActive ? 'text-accent-600' : 'text-neutral-400 group-hover:text-neutral-500'
                }`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Company info section - only for Employees */}
      {user?.role === 'Employee' && user?.company && (
        <div className="p-4 border-t border-border">
          <Link
            to="/company-info"
            onClick={onClose}
            className="flex items-center p-3 rounded-lg hover:bg-neutral-50 transition-colors duration-200 group"
          >
            {user.company.logo_url ? (
              <img
                src={user.company.logo_url}
                alt={user.company.name}
                className="w-8 h-8 rounded-lg object-cover mr-3"
              />
            ) : (
              <div className="w-8 h-8 rounded-lg bg-neutral-100 flex items-center justify-center mr-3">
                <BuildingOfficeIcon className="w-4 h-4 text-neutral-500" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 truncate group-hover:text-neutral-700">
                {user.company.name}
              </p>
              <p className="text-xs text-neutral-500">
                {user.role}
              </p>
            </div>
          </Link>
        </div>
      )}

      {/* Footer section */}
      <div className="p-4 border-t border-border">
        <p className="text-xs text-neutral-400 text-center">
          © 2024 Workforce App
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
