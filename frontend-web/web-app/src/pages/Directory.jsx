import React, { useEffect, useState, useMemo } from 'react';
import {
  MagnifyingGlassIcon,
  UserIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  XMarkIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { api } from '../contexts/AuthContext';

const Directory = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await api.get('/employees');
        setUsers(response.data);
      } catch (error) {
        console.error('Error fetching users:', error);
        setError('Failed to load directory. Using sample data.');
        // Fallback sample data
        setUsers([
          {
            id: 1,
            name: 'John Doe',
            email: 'john@example.com',
            role: 'Employee',
            avatar: 'https://via.placeholder.com/40',
            department: 'Engineering',
            status: 'Active'
          },
          {
            id: 2,
            name: 'Jane Smith',
            email: 'jane@example.com',
            role: 'Manager',
            avatar: 'https://via.placeholder.com/40',
            department: 'HR',
            status: 'Active'
          },
          {
            id: 3,
            name: 'Bob Johnson',
            email: 'bob@example.com',
            role: 'Employee',
            avatar: 'https://via.placeholder.com/40',
            department: 'Marketing',
            status: 'Inactive'
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      const matchesSearch = (user.name?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
                           (user.email?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
                           (user.department?.toLowerCase().includes(searchTerm.toLowerCase()) || false);
      const matchesRole = !roleFilter || user.role === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [users, searchTerm, roleFilter]);

  const uniqueRoles = [...new Set(users.map(user => user.role))];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-accent-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-neutral-600">Loading directory...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div>
            <h1 className="text-2xl font-semibold text-neutral-900">Employee Directory</h1>
            <p className="text-neutral-600 mt-1">Find and connect with your team members</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6">
        {error && (
          <div className="mb-6 p-4 bg-danger-50 border border-danger-200 text-danger-800 rounded-lg">
            <div className="flex items-start gap-3">
              <XMarkIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <p>{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-current hover:opacity-70"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-surface border border-border rounded-lg p-6 mb-6">
          <div className="space-y-4">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, email, or department..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="relative">
                <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent appearance-none bg-white"
                >
                  <option value="">All Roles</option>
                  {uniqueRoles.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setRoleFilter('');
                }}
                className="px-4 py-3 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-neutral-600">
            Showing <span className="font-medium text-neutral-900">{filteredUsers.length}</span> of <span className="font-medium text-neutral-900">{users.length}</span> employees
          </p>
        </div>

        {/* Employee List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredUsers.map((user) => (
            <div key={user.id} className="bg-surface border border-border rounded-lg p-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <UserIcon className="w-6 h-6 text-neutral-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-neutral-900 truncate">{user.name || 'Unknown'}</h3>
                  <div className="space-y-2 mt-2">
                    <div className="flex items-center gap-2 text-sm text-neutral-600">
                      <EnvelopeIcon className="w-4 h-4" />
                      <span className="truncate">{user.email || 'No email'}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-neutral-600">
                      <BuildingOfficeIcon className="w-4 h-4" />
                      <span>{user.department || 'No department'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-800">
                        {user.role || 'Employee'}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.status === 'Active' ? 'bg-success-100 text-success-700' : 'bg-neutral-100 text-neutral-700'
                      }`}>
                        {user.status || 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredUsers.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserIcon className="w-8 h-8 text-neutral-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              No employees found
            </h3>
            <p className="text-neutral-600">
              {searchTerm || roleFilter
                ? "No employees match your current search criteria. Try adjusting your filters."
                : "No employees are currently in the directory."
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Directory;
