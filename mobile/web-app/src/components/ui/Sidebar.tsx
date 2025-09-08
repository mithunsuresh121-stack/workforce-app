import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Home,
  Users,
  Calendar,
  BarChart3,
  MessageSquare,
  Settings,
  Building,
  Users2,
  User,
  LayoutDashboard,
  LogOut
} from 'lucide-react';
import { getCurrentUserProfile } from '../../lib/api';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [role, setRole] = useState<string | null>(null);
  const [navigation, setNavigation] = useState<NavItem[]>([]);

  useEffect(() => {
    const fetchUserRole = async () => {
      try {
        const profile = await getCurrentUserProfile();
        if (profile && profile.role) {
          setRole(profile.role);
        } else {
          setRole(null);
        }
      } catch (error) {
        setRole(null);
      }
    };
    fetchUserRole();
  }, []);

  useEffect(() => {
    if (!role) {
      setNavigation([]);
      return;
    }

    let navItems: NavItem[] = [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    ];

    if (role === 'SuperAdmin') {
      navItems = [
        ...navItems,
        { name: 'Tasks & Shifts', href: '/tasks', icon: Calendar },
        { name: 'System Settings', href: '/settings', icon: Settings },
      ];
    }

    if (role === 'CompanyAdmin') {
      navItems = [
        ...navItems,
        { name: 'Teams', href: '/teams', icon: Users2 },
        { name: 'Company', href: '/company', icon: Building },
      ];
    }

    if (role === 'Manager') {
      navItems = [
        ...navItems,
        { name: 'My Team', href: '/my-team', icon: Users },
        { name: 'Directory', href: '/directory', icon: Users2 },
        { name: 'Tasks & Shifts', href: '/tasks', icon: Calendar },
        { name: 'Reports', href: '/reports', icon: BarChart3 },
        { name: 'Chat Assistant', href: '/chat', icon: MessageSquare },
      ];
    }

    if (role === 'Employee') {
      navItems = [
        ...navItems,
        { name: 'Directory', href: '/directory', icon: Users2 },
        { name: 'Profile', href: '/profile', icon: User },
        { name: 'Tasks & Shifts', href: '/tasks', icon: Calendar },
        { name: 'Chat Assistant', href: '/chat', icon: MessageSquare },
      ];
    }

    // Common items for all roles except SuperAdmin
    if (role !== 'SuperAdmin') {
      navItems = [
        ...navItems,
        { name: 'Employees', href: '/employees', icon: Users },
      ];
    }

    setNavigation(navItems);
  }, [role]);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/login');
  };

  return (
    <div className={`flex flex-col h-full bg-gray-900 text-gray-100 border-r border-gray-800 transition-all duration-300 ${open ? 'w-64' : 'w-20'} overflow-hidden`}>
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <Building className="h-8 w-8 text-blue-400" />
          {open && (
            <span className="text-xl font-bold text-gray-100">
              Workforce
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;

          return (
            <Link
              key={item.name}
              to={item.href}
              className={`
                group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                ${isActive
                  ? 'bg-gray-700 text-gray-100'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-gray-100'
                }
              `}
              onClick={onClose}
            >
              <Icon className="mr-3 h-5 w-5" />
              {open && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-300 rounded-lg hover:bg-gray-700 hover:text-gray-100"
        >
          <LogOut className="mr-3 h-5 w-5" />
          {open && <span>Logout</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
