import React, { useEffect, useState } from 'react';
import { getCompanyUsers, getCompanyDepartments, getCompanyPositions } from '../api/companyApi.js';

interface User {
  id: number;
  full_name?: string;
  email?: string;
  role: string;
  employee_profile?: {
    department?: string;
    position?: string;
  };
  is_active: boolean;
}

const DirectoryScreen: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<string[]>([]);
  const [positions, setPositions] = useState<string[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<string>('full_name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const companyId = 1; // TODO: Replace with actual company ID from auth or context

  useEffect(() => {
    fetchFilters();
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [selectedDepartment, selectedPosition, sortBy, sortOrder]);

  const fetchFilters = async () => {
    try {
      const deps = await getCompanyDepartments(companyId);
      setDepartments(deps);
      const pos = await getCompanyPositions(companyId);
      setPositions(pos);
    } catch (err) {
      // Ignore filter fetch errors
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters: { department?: string; position?: string } = {};
      if (selectedDepartment) filters.department = selectedDepartment;
      if (selectedPosition) filters.position = selectedPosition;

      const data = await getCompanyUsers(
        companyId,
        filters,
        {
          sortBy,
          sortOrder,
        }
      );
      setUsers(data.users);
    } catch (err) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4" data-testid="directory-screen">
      <h1 className="text-2xl font-bold mb-4" data-testid="page-title-company-directory">Company Directory</h1>
      {error && <div className="mb-4 text-red-600" data-testid="directory-error">{error}</div>}
      <div className="flex space-x-4 mb-4">
        <select
          value={selectedDepartment || ''}
          onChange={(e) => setSelectedDepartment(e.target.value || null)}
          className="border border-gray-300 rounded px-3 py-2"
          data-testid="directory-filter-department"
        >
          <option value="">All Departments</option>
          {departments.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>
        <select
          value={selectedPosition || ''}
          onChange={(e) => setSelectedPosition(e.target.value || null)}
          className="border border-gray-300 rounded px-3 py-2"
          data-testid="directory-filter-position"
        >
          <option value="">All Positions</option>
          {positions.map((pos) => (
            <option key={pos} value={pos}>
              {pos}
            </option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          data-testid="directory-sort-by"
          aria-label="Sort by"
        >
          <option value="full_name">Name</option>
          <option value="role">Role</option>
          <option value="department">Department</option>
          <option value="position">Position</option>
        </select>
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
          className="border border-gray-300 rounded px-3 py-2"
          data-testid="directory-sort-order"
          aria-label="Sort order"
        >
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>
      {loading ? (
        <div data-testid="directory-loading">Loading users...</div>
      ) : users.length === 0 ? (
        <div data-testid="directory-empty">No users found.</div>
      ) : (
        <table className="w-full border-collapse border border-gray-300" data-testid="directory-user-list">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-name">Name</th>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-email">Email</th>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-role">Role</th>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-department">Department</th>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-position">Position</th>
              <th className="border border-gray-300 px-4 py-2 text-left" data-testid="directory-header-status">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-100 cursor-pointer" data-testid={`directory-item-${user.id}`}>
                <td className="border border-gray-300 px-4 py-2">{user.full_name || '-'}</td>
                <td className="border border-gray-300 px-4 py-2" data-testid={`directory-user-email-${user.id}`}>{user.email || '-'}</td>
                <td className="border border-gray-300 px-4 py-2">{user.role}</td>
                <td className="border border-gray-300 px-4 py-2">{user.employee_profile?.department || '-'}</td>
                <td className="border border-gray-300 px-4 py-2">{user.employee_profile?.position || '-'}</td>
                <td className="border border-gray-300 px-4 py-2">
                  {user.is_active ? (
                    <span className="text-green-600 font-semibold" data-testid="status-active">Active</span>
                  ) : (
                    <span className="text-red-600 font-semibold" data-testid="status-inactive">Inactive</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DirectoryScreen;
