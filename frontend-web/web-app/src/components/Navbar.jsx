import React from 'react';
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Navbar = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Hamburger menu for mobile */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Toggle sidebar"
        >
          <svg
            className="w-6 h-6"
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

        <h1 className="text-2xl font-semibold text-gray-800">Dashboard</h1>

        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <BellIcon className="w-6 h-6" />
          </button>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/profile')}
              className="flex items-center space-x-2 p-1 rounded-md hover:bg-gray-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Go to profile"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  navigate('/profile');
                }
              }}
            >
              <UserCircleIcon className="w-8 h-8 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">{user?.name || 'User'}</span>
            </button>
            <button
              onClick={logout}
              className="ml-4 px-3 py-1 text-sm text-red-600 border border-red-600 rounded hover:bg-red-600 hover:text-white transition"
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
