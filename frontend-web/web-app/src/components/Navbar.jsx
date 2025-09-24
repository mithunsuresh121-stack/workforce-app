import React from 'react';
import { BellIcon, UserCircleIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get page title based on current route
  const getPageTitle = () => {
    const path = location.pathname;
    switch (path) {
      case '/dashboard':
        return 'Dashboard';
      case '/profile':
        return 'Profile';
      case '/profile-professional':
        return 'Professional Profile';
      case '/directory':
        return 'Directory';
      case '/tasks':
        return 'Tasks';
      case '/leave':
        return 'Leave';
      case '/company':
        return 'Company';
      case '/approvals':
        return 'Approvals';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="bg-surface border-b border-border">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left section - Hamburger menu and page title */}
        <div className="flex items-center space-x-4">
          {/* Hamburger menu for mobile */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-accent-500 transition-colors duration-200"
            aria-label="Toggle sidebar"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <div>
            <h1 className="text-xl font-semibold text-neutral-900">{getPageTitle()}</h1>
            <p className="text-sm text-neutral-500">
              Welcome back, {user?.name || 'User'}
            </p>
          </div>
        </div>

        {/* Right section - Search, notifications, user menu */}
        <div className="flex items-center space-x-3">
          {/* Search button */}
          <button className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors duration-200">
            <MagnifyingGlassIcon className="w-5 h-5" />
          </button>

          {/* Notifications */}
          <button className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors duration-200 relative">
            <BellIcon className="w-5 h-5" />
            {/* Notification dot */}
            <div className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></div>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3 pl-3 border-l border-border">
            <button
              onClick={() => navigate('/profile')}
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-neutral-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-500"
              aria-label="Go to profile"
            >
              <div className="w-8 h-8 bg-accent-100 rounded-lg flex items-center justify-center">
                <UserCircleIcon className="w-5 h-5 text-accent-600" />
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-neutral-900">{user?.name || 'User'}</p>
                <p className="text-xs text-neutral-500 capitalize">{user?.role || 'User'}</p>
              </div>
            </button>

            <button
              onClick={logout}
              className="px-3 py-2 text-sm font-medium text-danger-600 hover:text-danger-700 hover:bg-danger-50 rounded-lg transition-colors duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
