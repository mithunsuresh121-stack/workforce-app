import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, UserIcon, UsersIcon, ClipboardIcon, CalendarIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { List, ListItem, ListItemPrefix, Typography } from '@material-tailwind/react';

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
    <div className="w-full max-w-xs bg-white shadow-lg flex flex-col h-full">
      {/* Header with close button for mobile */}
      <div className="flex items-center justify-between p-4 border-b">
        <Typography variant="h5" color="blue-gray">
          Workforce App
        </Typography>
        {onClose && (
          <button onClick={onClose} className="p-1 rounded-md text-gray-400 hover:text-gray-600 md:hidden">
            <XMarkIcon className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 mt-4">
        <List>
          {menuItems.map((item) => (
            <Link key={item.path} to={item.path} onClick={onClose}>
              <ListItem className={location.pathname === item.path ? 'bg-blue-50 text-blue-600' : ''}>
                <ListItemPrefix>
                  <item.icon className="w-5 h-5" />
                </ListItemPrefix>
                <Typography variant="small" className="font-medium">
                  {item.label}
                </Typography>
              </ListItem>
            </Link>
          ))}
        </List>
      </nav>
    </div>
  );
};

export default Sidebar;
