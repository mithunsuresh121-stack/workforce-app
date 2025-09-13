import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import {
  Card,
  CardBody,
  CardHeader,
  Typography,
  Input,
  Button,
  Avatar,
  Chip,
  Spinner,
  Alert
} from '@material-tailwind/react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

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
        const response = await axios.get('/api/users');
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

  const getRoleColor = (role) => {
    switch (role) {
      case 'Super Admin': return 'purple';
      case 'Company Admin': return 'blue';
      case 'Manager': return 'green';
      case 'Employee': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusColor = (status) => {
    return status === 'Active' ? 'green' : 'red';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="p-4">
      <Typography variant="h3" color="blue-gray" className="mb-6">
        Employee Directory
      </Typography>

      {error && (
        <Alert color="red" className="mb-6">
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Input
                type="text"
                label="Search employees..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                icon={<MagnifyingGlassIcon className="h-5 w-5" />}
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
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setRoleFilter('');
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Results Summary */}
      <Typography variant="small" color="gray" className="mb-4">
        Showing {filteredUsers.length} of {users.length} employees
      </Typography>

      {/* Employee Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredUsers.map((user) => (
          <Card key={user.id} className="hover:shadow-lg transition-shadow">
            <CardBody className="text-center">
              <Avatar
                src={user.avatar}
                alt={user.name}
                size="xl"
                className="mx-auto mb-4"
              />
              <Typography variant="h6" color="blue-gray" className="mb-2">
                {user.name}
              </Typography>
              <Typography variant="small" color="gray" className="mb-2">
                {user.email}
              </Typography>
              <div className="flex justify-center gap-2 mb-3">
                <Chip
                  color={getRoleColor(user.role)}
                  value={user.role}
                  size="sm"
                />
                <Chip
                  color={getStatusColor(user.status)}
                  value={user.status}
                  size="sm"
                  variant="outlined"
                />
              </div>
              {user.department && (
                <Typography variant="small" color="gray">
                  Department: {user.department}
                </Typography>
              )}
            </CardBody>
          </Card>
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <Card>
          <CardBody className="text-center py-12">
            <Typography variant="h6" color="gray">
              No employees found matching your criteria.
            </Typography>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default Directory;
