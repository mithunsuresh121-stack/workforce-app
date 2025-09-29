import React, { useState, useEffect } from "react";
import { Card, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TextField, Select, MenuItem, FormControl, InputLabel, Box, IconButton, Chip, useMediaQuery, useTheme } from "@mui/material";
import { MagnifyingGlassIcon, ArrowUpIcon, ArrowDownIcon, PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/outline";
import DashboardLayout from "../layouts/DashboardLayout";
import { api } from "../contexts/AuthContext";

const initialEmployees = [
  { id: 1, name: 'John Doe', role: 'Developer', status: 'Active' },
  { id: 2, name: 'Jane Smith', role: 'Designer', status: 'Active' },
  { id: 3, name: 'Bob Johnson', role: 'Manager', status: 'Inactive' },
];

export default function Employees() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [employees, setEmployees] = useState(initialEmployees);
  const [filteredEmployees, setFilteredEmployees] = useState(initialEmployees);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [editingCell, setEditingCell] = useState(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    filterAndSortEmployees();
  }, [employees, searchTerm, statusFilter, sortField, sortDirection]);

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const filterAndSortEmployees = () => {
    let filtered = employees.filter(employee =>
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.role.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (statusFilter !== 'All') {
      filtered = filtered.filter(employee => employee.status === statusFilter);
    }

    filtered.sort((a, b) => {
      const aValue = a[sortField].toLowerCase();
      const bValue = b[sortField].toLowerCase();
      if (sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    });

    setFilteredEmployees(filtered);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleEditCell = (employeeId, field, value) => {
    setEditingCell({ employeeId, field });
    setEditValue(value);
  };

  const handleSaveEdit = () => {
    setEmployees(employees.map(emp =>
      emp.id === editingCell.employeeId
        ? { ...emp, [editingCell.field]: editValue }
        : emp
    ));
    setEditingCell(null);
  };

  const handleCancelEdit = () => {
    setEditingCell(null);
  };

  const renderTableCell = (employee, field, value) => {
    const isEditing = editingCell?.employeeId === employee.id && editingCell?.field === field;

    if (isEditing) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            size="small"
            fullWidth
          />
          <IconButton size="small" onClick={handleSaveEdit}>
            <CheckIcon style={{ width: 16, height: 16 }} />
          </IconButton>
          <IconButton size="small" onClick={handleCancelEdit}>
            <XMarkIcon style={{ width: 16, height: 16 }} />
          </IconButton>
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography>{value}</Typography>
        <IconButton size="small" onClick={() => handleEditCell(employee.id, field, value)}>
          <PencilIcon style={{ width: 16, height: 16 }} />
        </IconButton>
      </Box>
    );
  };

  const renderEmployeeCard = (employee) => (
    <Card key={employee.id} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" sx={{ color: 'text.primary' }}>{employee.name}</Typography>
        <Chip label={employee.status} color={employee.status === 'Active' ? 'success' : 'default'} />
      </Box>
      <Typography sx={{ color: 'text.secondary' }}>{employee.role}</Typography>
      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
        <IconButton size="small" onClick={() => handleEditCell(employee.id, 'name', employee.name)}>
          <PencilIcon style={{ width: 16, height: 16 }} />
        </IconButton>
      </Box>
    </Card>
  );

  return (
    <DashboardLayout>
      <Typography variant="h4" sx={{ mb: 3, color: 'text.primary' }}>Employees</Typography>
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search employees..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <MagnifyingGlassIcon style={{ width: 20, height: 20, marginRight: 8 }} />,
          }}
          sx={{ minWidth: 250 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <MenuItem value="All">All</MenuItem>
            <MenuItem value="Active">Active</MenuItem>
            <MenuItem value="Inactive">Inactive</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <Card sx={{ p: 3 }}>
        {isMobile ? (
          <Box>
            {filteredEmployees.map(renderEmployeeCard)}
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell onClick={() => handleSort('id')} sx={{ cursor: 'pointer' }}>
                    ID {sortField === 'id' && (sortDirection === 'asc' ? <ArrowUpIcon style={{ width: 16, height: 16 }} /> : <ArrowDownIcon style={{ width: 16, height: 16 }} />)}
                  </TableCell>
                  <TableCell onClick={() => handleSort('name')} sx={{ cursor: 'pointer' }}>
                    Name {sortField === 'name' && (sortDirection === 'asc' ? <ArrowUpIcon style={{ width: 16, height: 16 }} /> : <ArrowDownIcon style={{ width: 16, height: 16 }} />)}
                  </TableCell>
                  <TableCell onClick={() => handleSort('role')} sx={{ cursor: 'pointer' }}>
                    Role {sortField === 'role' && (sortDirection === 'asc' ? <ArrowUpIcon style={{ width: 16, height: 16 }} /> : <ArrowDownIcon style={{ width: 16, height: 16 }} />)}
                  </TableCell>
                  <TableCell onClick={() => handleSort('status')} sx={{ cursor: 'pointer' }}>
                    Status {sortField === 'status' && (sortDirection === 'asc' ? <ArrowUpIcon style={{ width: 16, height: 16 }} /> : <ArrowDownIcon style={{ width: 16, height: 16 }} />)}
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredEmployees.map((employee) => (
                  <TableRow key={employee.id} sx={{ '&:hover': { backgroundColor: 'action.hover' } }}>
                    <TableCell>{employee.id}</TableCell>
                    <TableCell>{renderTableCell(employee, 'name', employee.name)}</TableCell>
                    <TableCell>{renderTableCell(employee, 'role', employee.role)}</TableCell>
                    <TableCell>
                      <Chip label={employee.status} color={employee.status === 'Active' ? 'success' : 'default'} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>
    </DashboardLayout>
  );
}
