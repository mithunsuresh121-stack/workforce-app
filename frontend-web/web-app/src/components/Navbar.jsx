import React, { useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { BellIcon, Bars3Icon } from '@heroicons/react/24/outline';
import { Button, Avatar, Typography, Menu, MenuHandler, MenuList, MenuItem } from '@material-tailwind/react';
import { AuthContext } from '../context/AuthContext';

const Navbar = ({ onMenuClick }) => {
  const location = useLocation();
  const { user, logout } = useContext(AuthContext);

  // Get page title based on current path
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/' || path === '/dashboard') return 'Dashboard';
    if (path === '/profile') return 'Profile';
    if (path === '/directory') return 'Directory';
    if (path === '/tasks') return 'Tasks';
    if (path === '/leave') return 'Leave';
    return 'Workforce App';
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="flex items-center justify-between px-4 py-4 md:px-6">
        <div className="flex items-center">
          {/* Mobile menu button */}
          <Button
            variant="text"
            size="sm"
            className="mr-4 md:hidden"
            onClick={onMenuClick}
          >
            <Bars3Icon className="w-6 h-6" />
          </Button>
          <Typography variant="h4" color="blue-gray" className="font-semibold">
            {getPageTitle()}
          </Typography>
        </div>

        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <Button variant="text" size="sm" className="p-2">
            <BellIcon className="w-6 h-6 text-gray-600" />
          </Button>

          {/* User menu */}
          <Menu>
            <MenuHandler>
              <Button variant="text" className="flex items-center space-x-2 p-2">
                <Avatar
                  src={user?.avatar || 'https://via.placeholder.com/40'}
                  alt={user?.name || 'User'}
                  size="sm"
                  className="w-8 h-8"
                />
                <Typography variant="small" className="font-medium text-gray-700 hidden sm:block">
                  {user?.name || 'User'}
                </Typography>
              </Button>
            </MenuHandler>
            <MenuList>
              <MenuItem onClick={logout}>
                <Typography variant="small" color="red">
                  Logout
                </Typography>
              </MenuItem>
            </MenuList>
          </Menu>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
