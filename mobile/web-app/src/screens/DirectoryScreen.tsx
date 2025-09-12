import React, { useEffect, useState } from 'react';
import { getCompanyUsers, getCompanyDepartments, getCompanyPositions } from '../lib/api';

const DirectoryScreen: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [departments, setDepartments] = useState<string[]>([]);
  const [positions, setPositions] = useState<string[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [selectedPosition, setSelectedPosition] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('full_name');
  const [sortOrder, setSortOrder] = useState<string>('asc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [companyId, setCompanyId] = useState<number | null>(null);

  useEffect(() => {
    // Get company ID from localStorage or auth context
    const storedCompanyId = localStorage.getItem('company_id');
    if (storedCompanyId) {
      setCompanyId(parseInt(storedCompanyId));
    }
  }, []);

  useEffect(() => {
    if (companyId) {
      fetchData();
    }
  }, [companyId]);

  const fetchData = async () => {
    if (!companyId) return;
    setLoading(true);
    setError(null);
    try {
      const [usersData, departmentsData, positionsData] = await Promise.all([
        getCompanyUsers(companyId, {
          department: selectedDepartment || undefined,
          position: selectedPosition || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        }),
        getCompanyDepartments(companyId),
        getCompanyPositions(companyId),
      ]);
      setUsers(usersData);
      setDepartments(departmentsData);
      setPositions(positionsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load directory data');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = () => {
    fetchData();
  };

  const handleSortChange = (newSortBy: string) => {
    if (newSortBy === sortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
    setTimeout(fetchData, 0);
  };

  if (loading && users.length === 0) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (error && users.length === 0) {
    return <div className="text-red-600 text-center p-4">Error: {error}</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Company Directory</h1>

      {/* Filters */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block font-semibold mb-2" htmlFor="department">Department</label>
          <select
            id="department"
            value={selectedDepartment}
            onChange={(e) => {
              setSelectedDepartment(e.target.value);
              setTimeout(handleFilterChange, 0);
            }}
            className="w-full border border-gray-300 rounded px-3 py-2"
          >
            <option value="">All Departments</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block font-semibold mb-2" htmlFor="position">Position</label>
          <select
            id="position"
            value={selectedPosition}
            onChange={(e) => {
              setSelectedPosition(e.target.value);
              setTimeout(handleFilterChange, 0);
            }}
            className="w-full border border-gray-300 rounded px-3 py-2"
          >
            <option value="">All Positions</option>
            {positions.map((pos) => (
              <option key={pos} value={pos}>
                {pos}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Sorting */}
      <div className="mb-4 flex flex-wrap gap-2">
        <span className="font-semibold">Sort by:</span>
        {[
          { key: 'full_name', label: 'Name' },
          { key: 'role', label: 'Role' },
          { key: 'department', label: 'Department' },
          { key: 'position', label: 'Position' },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => handleSortChange(key)}
            className={`px-3 py-1 rounded ${
              sortBy === key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {label} {sortBy === key && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
        ))}
      </div>

      {/* User List */}
      {loading && users.length > 0 && (
        <div className="text-center py-4">Loading...</div>
      )}

      {error && users.length > 0 && (
        <div className="text-red-600 text-center py-4">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {users.map((user) => (
          <div
            key={user.id}
            className="border border-gray-300 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center mb-2">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                {user.full_name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div>
                <h3 className="font-semibold text-lg">{user.full_name || 'User'}</h3>
                <p className="text-gray-600">{user.role}</p>
              </div>
            </div>
            <div className="space-y-1 text-sm">
              <p><span className="font-medium">Email:</span> {user.email}</p>
              {user.employee_profile?.department && (
                <p><span className="font-medium">Department:</span> {user.employee_profile.department}</p>
              )}
              {user.employee_profile?.position && (
                <p><span className="font-medium">Position:</span> {user.employee_profile.position}</p>
              )}
              {user.employee_profile?.phone && (
                <p><span className="font-medium">Phone:</span> {user.employee_profile.phone}</p>
              )}
            </div>
            <div className="mt-3 flex items-center">
              <span
                className={`inline-block w-3 h-3 rounded-full mr-2 ${
                  user.is_active ? 'bg-green-500' : 'bg-red-500'
                }`}
              ></span>
              <span className="text-sm text-gray-600">
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {users.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          No users found matching the current filters.
        </div>
      )}
    </div>
  );
};

export default DirectoryScreen;
