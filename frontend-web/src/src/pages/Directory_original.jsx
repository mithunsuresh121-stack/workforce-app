import React, { useEffect, useState, useMemo } from 'react';
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
        const response = await api.get('/users');
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
      const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user.department?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = !roleFilter || user.role === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [users, searchTerm, roleFilter]);

  const uniqueRoles = [...new Set(users.map(user => user.role))];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h3 className="text-3xl font-bold text-gray-800 mb-6">
        Employee Directory
      </h3>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md border mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search employees..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Roles</option>
              {uniqueRoles.map(role => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setRoleFilter('');
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <p className="text-sm text-gray-600 mb-4">
        Showing {filteredUsers.length} of {users.length} employees
      </p>

      {/* Employee Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredUsers.map((user) => (
          <div key={user.id} className="bg-white p-6 rounded-lg shadow-md border hover:shadow-lg transition-shadow">
            <div className="text-center">
              <img
                src={user.avatar}
                alt={user.name}
                className="w-20 h-20 rounded-full mx-auto mb-4"
              />
              <h6 className="text-lg font-semibold text-gray-800 mb-2">
                {user.name}
              </h6>
              <p className="text-sm text-gray-600 mb-2">
                {user.email}
              </p>
              <div className="flex justify-center gap-2 mb-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  user.role === 'Super Admin' ? 'bg-purple-100 text-purple-800' :
                  user.role === 'Company Admin' ? 'bg-blue-100 text-blue-800' :
                  user.role === 'Manager' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {user.role}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                  user.status === 'Active' ? 'bg-green-100 text-green-800 border-green-200' :
                  'bg-red-100 text-red-800 border-red-200'
                }`}>
                  {user.status}
                </span>
              </div>
              {user.department && (
                <p className="text-sm text-gray-600">
                  Department: {user.department}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <div className="bg-white p-12 rounded-lg shadow-md border text-center">
          <h6 className="text-lg font-semibold text-gray-600">
            No employees found matching your criteria.
          </h6>
        </div>
      )}
    </div>
  );
};

export default Directory;
