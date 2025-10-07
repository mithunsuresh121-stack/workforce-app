import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CheckIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { api, useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const LeaveApproval = () => {
  const { user, isManager } = useAuth();
  const navigate = useNavigate();
  const [pendingLeaves, setPendingLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isManager()) {
      navigate('/dashboard');
      return;
    }
    fetchPendingLeaves();
  }, []);

  const fetchPendingLeaves = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/leaves/pending');
      setPendingLeaves(response.data);
    } catch (err) {
      setError('Failed to load pending leaves');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (leaveId, action) => {
    setLoading(true);
    setError('');
    try {
      const endpoint = `/leaves/${leaveId}/${action}`;
      await api.patch(endpoint);
      await fetchPendingLeaves();
    } catch (err) {
      setError(`Failed to ${action} leave request`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Card sx={{ p: 3 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Pending Leave Approvals
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {pendingLeaves.length === 0 ? (
          <Typography>No pending leave requests to approve.</Typography>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee Name</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Dates</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pendingLeaves.map((leave) => (
                  <TableRow key={leave.id} hover>
                    <TableCell>{leave.employee_name || 'Unknown'}</TableCell>
                    <TableCell>{leave.type}</TableCell>
                    <TableCell>
                      {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{leave.reason}</TableCell>
                    <TableCell>{leave.status}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<CheckIcon style={{ width: 20, height: 20 }} />}
                        onClick={() => handleAction(leave.id, 'approve')}
                        sx={{ mr: 1 }}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="contained"
                        color="error"
                        startIcon={<XCircleIcon style={{ width: 20, height: 20 }} />}
                        onClick={() => handleAction(leave.id, 'reject')}
                      >
                        Reject
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>
    </Box>
  );
};

export default LeaveApproval;
