import React, { useState, useEffect, useMemo } from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import {
  PlusIcon,
  CalendarDaysIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import {
  Box,
  Typography,
  Card,
  Button,
  Modal,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  IconButton,
  Grid,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { api, useAuth } from '../contexts/AuthContext';

const Leave = () => {
  const { user, isManager } = useAuth();
  const [leaves, setLeaves] = useState([]);
  const [pendingLeaves, setPendingLeaves] = useState([]);
  const [leaveBalances, setLeaveBalances] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [approveDialog, setApproveDialog] = useState({ open: false, leave: null, action: '' });

  useEffect(() => {
    const fetchLeaveData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch leave requests
        const leavesResponse = await api.get('/leaves');
        setLeaves(leavesResponse.data);

        // Fetch pending leaves if manager
        if (isManager()) {
          const pendingResponse = await api.get('/leaves/pending');
          setPendingLeaves(pendingResponse.data);
        }

        // Fetch leave balances
        const balancesResponse = await api.get('/leaves/balances');
        setLeaveBalances(balancesResponse.data);

      } catch (error) {
        console.error('Error fetching leave data:', error);
        setError('Failed to load leave data. Using sample data.');

        // Fallback sample data
        setLeaves([
          {
            id: 1,
            type: 'Annual Leave',
            startDate: '2024-01-15',
            endDate: '2024-01-20',
            status: 'Approved',
            reason: 'Family vacation',
            days: 6,
            createdAt: new Date().toISOString()
          },
          {
            id: 2,
            type: 'Sick Leave',
            startDate: '2024-01-10',
            endDate: '2024-01-10',
            status: 'Pending',
            reason: 'Medical appointment',
            days: 1,
            createdAt: new Date().toISOString()
          },
          {
            id: 3,
            type: 'Personal Leave',
            startDate: '2024-01-05',
            endDate: '2024-01-05',
            status: 'Rejected',
            reason: 'Personal matters',
            days: 1,
            createdAt: new Date().toISOString()
          },
        ]);

        setLeaveBalances({
          'Annual Leave': { used: 12, total: 25 },
          'Sick Leave': { used: 3, total: 10 },
          'Personal Leave': { used: 2, total: 5 },
        });
      } finally {
        setLoading(false);
      }
    };

    fetchLeaveData();
  }, []);

  const validationSchema = Yup.object({
    type: Yup.string().required('Leave type is required'),
    startDate: Yup.date().required('Start date is required'),
    endDate: Yup.date()
      .required('End date is required')
      .min(Yup.ref('startDate'), 'End date must be after start date'),
    reason: Yup.string().required('Reason is required'),
  });

  const handleSubmit = async (values, { resetForm }) => {
    try {
      setSubmitting(true);
      const response = await api.post('/leaves', values);
      setLeaves([response.data, ...leaves]);
      setDialogOpen(false);
      resetForm();
      // Refresh pending leaves if manager
      if (isManager()) {
        const pendingResponse = await api.get('/leaves/pending');
        setPendingLeaves(pendingResponse.data);
      }
    } catch (error) {
      console.error('Error submitting leave request:', error);
      setError('Failed to submit leave request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const calculateDays = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  };

  const handleApproveReject = async (leaveId, action) => {
    try {
      setLoading(true);
      const endpoint = `/leaves/${leaveId}/status`;
      const status = action === 'approve' ? 'Approved' : 'Rejected';
      await api.put(endpoint, { status });
      // Refresh leaves and pending leaves
      const leavesResponse = await api.get('/leaves');
      setLeaves(leavesResponse.data);
      if (isManager()) {
        const pendingResponse = await api.get('/leaves/pending');
        setPendingLeaves(pendingResponse.data);
      }
      setApproveDialog({ open: false, leave: null, action: '' });
    } catch (error) {
      console.error('Error updating leave status:', error);
      setError('Failed to update leave status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredLeaves = useMemo(() => {
    return leaves.filter(leave => {
      const matchesStatus = !statusFilter || leave.status === statusFilter;
      const matchesType = !typeFilter || leave.type === typeFilter;
      return matchesStatus && matchesType;
    });
  }, [leaves, statusFilter, typeFilter]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 256 }}>
        <Box sx={{ textAlign: 'center' }}>
          <Box sx={{ width: 32, height: 32, border: 2, borderColor: 'primary.main', borderTopColor: 'transparent', borderRadius: '50%', mx: 'auto', mb: 2, animation: 'spin 1s linear infinite' }} />
          <Typography variant="body2" color="text.secondary">Loading leave data...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Header Section */}
        <Box sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h4" sx={{ color: 'text.primary' }}>Leave Management</Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary' }}>Manage your leave requests and balances</Typography>
              </Box>
              <Button
                onClick={() => setDialogOpen(true)}
                variant="contained"
                startIcon={<PlusIcon />}
              >
                Request Leave
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Main Content */}
        <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
          {error && (
            <Alert severity="error" onClose={() => setError('')} sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Leave Balances */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {Object.entries(leaveBalances).map(([type, balance]) => (
              <Grid item xs={12} md={4} key={type}>
                <Card sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ color: 'text.primary' }}>{type}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                      <ClockIcon sx={{ width: 20, height: 20 }} />
                      <Typography variant="body2" fontWeight="medium">{balance.total - balance.used} left</Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                      <Typography sx={{ color: 'text.secondary' }}>Used</Typography>
                      <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>{balance.used} days</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                      <Typography sx={{ color: 'text.secondary' }}>Total</Typography>
                      <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>{balance.total} days</Typography>
                    </Box>
                    <Box sx={{ width: '100%', height: 8, bgcolor: 'grey.200', borderRadius: 1 }}>
                      <Box
                        sx={{
                          width: `${(balance.used / balance.total) * 100}%`,
                          height: '100%',
                          bgcolor: 'primary.main',
                          borderRadius: 1,
                          transition: 'width 0.3s'
                        }}
                      />
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {Math.round((balance.used / balance.total) * 100)}% utilized
                      </Typography>
                    </Box>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Filters */}
          <Card sx={{ p: 3, mb: 4 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    label="Status"
                  >
                    <MenuItem value="">All Statuses</MenuItem>
                    <MenuItem value="Pending">Pending</MenuItem>
                    <MenuItem value="Approved">Approved</MenuItem>
                    <MenuItem value="Rejected">Rejected</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    label="Type"
                  >
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="Annual Leave">Annual Leave</MenuItem>
                    <MenuItem value="Sick Leave">Sick Leave</MenuItem>
                    <MenuItem value="Personal Leave">Personal Leave</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    setStatusFilter('');
                    setTypeFilter('');
                  }}
                >
                  Clear Filters
                </Button>
              </Grid>
            </Grid>
          </Card>

          {/* Leave History */}
          <Card sx={{ overflow: 'hidden' }}>
            <Box sx={{ px: 3, py: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
              <Typography variant="h6" sx={{ color: 'text.primary' }}>Leave History</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>View and manage your leave requests</Typography>
            </Box>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    <TableCell>Type</TableCell>
                    <TableCell>Dates</TableCell>
                    <TableCell>Days</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Reason</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLeaves.map((leave) => (
                    <TableRow key={leave.id} hover>
                      <TableCell>
                      <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>{leave.type}</Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CalendarDaysIcon sx={{ width: 16, height: 16, color: 'text.secondary' }} />
                          <Typography sx={{ color: 'text.primary' }}>
                            {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>
                          {leave.days || calculateDays(leave.startDate, leave.endDate)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={leave.status}
                          size="small"
                          color={
                            leave.status === 'Approved' ? 'success' :
                            leave.status === 'Pending' ? 'warning' :
                            'error'
                          }
                          icon={
                            leave.status === 'Approved' ? <CheckCircleIcon sx={{ width: 16, height: 16 }} /> :
                            leave.status === 'Pending' ? <ClockIcon sx={{ width: 16, height: 16 }} /> :
                            <XCircleIcon sx={{ width: 16, height: 16 }} />
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', color: 'text.primary' }}>
                          {leave.reason}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {filteredLeaves.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 12 }}>
                <Box sx={{ width: 64, height: 64, bgcolor: 'grey.100', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
                  <CalendarDaysIcon sx={{ width: 32, height: 32, color: 'text.secondary' }} />
                </Box>
                <Typography variant="h6" sx={{ mb: 1, color: 'text.primary' }}>No leave requests found</Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {statusFilter || typeFilter
                    ? "No leave requests match your current filters. Try adjusting your search criteria."
                    : "You haven't submitted any leave requests yet."
                  }
                </Typography>
              </Box>
            )}
          </Card>

          {/* Leave Request Modal */}
          <Modal
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
          >
            <Box sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '100%',
              maxWidth: 600,
              bgcolor: 'background.paper',
              borderRadius: 2,
              boxShadow: 24,
              p: 4,
              maxHeight: '90vh',
              overflowY: 'auto'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, borderBottom: 1, borderColor: 'divider', pb: 2 }}>
                <Box>
                <Typography variant="h5" sx={{ color: 'text.primary' }}>Request Leave</Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>Submit a new leave request</Typography>
                </Box>
                <IconButton onClick={() => setDialogOpen(false)}>
                  <XMarkIcon sx={{ width: 24, height: 24 }} />
                </IconButton>
              </Box>
              <Formik
                initialValues={{
                  type: '',
                  startDate: '',
                  endDate: '',
                  reason: ''
                }}
                validationSchema={validationSchema}
                onSubmit={handleSubmit}
              >
                {({ values, errors, touched, handleChange, handleSubmit, isSubmitting }) => (
                  <Form onSubmit={handleSubmit}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <FormControl fullWidth error={touched.type && Boolean(errors.type)}>
                        <InputLabel>Leave Type</InputLabel>
                        <Select
                          name="type"
                          value={values.type}
                          onChange={handleChange}
                          label="Leave Type"
                        >
                          <MenuItem value="">Select leave type</MenuItem>
                          <MenuItem value="Annual Leave">Annual Leave</MenuItem>
                          <MenuItem value="Sick Leave">Sick Leave</MenuItem>
                          <MenuItem value="Personal Leave">Personal Leave</MenuItem>
                        </Select>
                        {touched.type && errors.type && (
                          <Typography variant="caption" sx={{ color: 'error' }}>{errors.type}</Typography>
                        )}
                      </FormControl>

                      <Grid container spacing={3}>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            label="Start Date"
                            type="date"
                            name="startDate"
                            value={values.startDate}
                            onChange={handleChange}
                            error={touched.startDate && Boolean(errors.startDate)}
                            helperText={touched.startDate && errors.startDate}
                            sx={{ '& .MuiFormHelperText-root': { color: 'error.main' } }}
                            InputLabelProps={{ shrink: true }}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            label="End Date"
                            type="date"
                            name="endDate"
                            value={values.endDate}
                            onChange={handleChange}
                            error={touched.endDate && Boolean(errors.endDate)}
                            helperText={touched.endDate && errors.endDate}
                            sx={{ '& .MuiFormHelperText-root': { color: 'error.main' } }}
                            InputLabelProps={{ shrink: true }}
                          />
                        </Grid>
                      </Grid>

                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        label="Reason"
                        name="reason"
                        value={values.reason}
                        onChange={handleChange}
                        error={touched.reason && Boolean(errors.reason)}
                        helperText={touched.reason && errors.reason}
                        sx={{ '& .MuiFormHelperText-root': { color: 'error.main' } }}
                      />

                      {values.startDate && values.endDate && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CalendarDaysIcon sx={{ width: 20, height: 20 }} />
                          <Typography sx={{ color: 'text.primary' }}>Total days: {calculateDays(values.startDate, values.endDate)}</Typography>
                          </Box>
                        </Alert>
                      )}

                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                        <Button variant="outlined" onClick={() => setDialogOpen(false)} disabled={isSubmitting}>
                          Cancel
                        </Button>
                        <Button type="submit" variant="contained" disabled={isSubmitting}>
                          {isSubmitting ? 'Submitting...' : 'Submit Request'}
                        </Button>
                      </Box>
                    </Box>
                  </Form>
                )}
              </Formik>
            </Box>
          </Modal>

        {/* Pending Leaves for Manager Approval */}
        {isManager() && (
          <Card sx={{ overflow: 'hidden', mt: 6 }}>
            <Box sx={{ px: 3, py: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
              <Typography variant="h6" sx={{ color: 'text.primary' }}>Pending Leave Approvals</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>Approve or reject leave requests</Typography>
            </Box>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    <TableCell>Employee</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Dates</TableCell>
                    <TableCell>Days</TableCell>
                    <TableCell>Reason</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingLeaves.map((leave) => (
                    <TableRow key={leave.id} hover>
                      <TableCell>
                        <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>
                          {leave.employee_name || 'Unknown'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ color: 'text.primary' }}>{leave.type}</Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CalendarDaysIcon sx={{ width: 16, height: 16, color: 'text.secondary' }} />
                          <Typography sx={{ color: 'text.primary' }}>
                            {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ fontWeight: 'medium', color: 'text.primary' }}>
                          {leave.days || calculateDays(leave.startDate, leave.endDate)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', color: 'text.primary' }}>
                          {leave.reason}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            size="small"
                            variant="contained"
                            color="success"
                            startIcon={<CheckIcon sx={{ width: 16, height: 16 }} />}
                            onClick={() => setApproveDialog({ open: true, leave, action: 'approve' })}
                          >
                            Approve
                          </Button>
                          <Button
                            size="small"
                            variant="contained"
                            color="error"
                            startIcon={<XCircleIcon sx={{ width: 16, height: 16 }} />}
                            onClick={() => setApproveDialog({ open: true, leave, action: 'reject' })}
                          >
                            Reject
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {pendingLeaves.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 12 }}>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  No pending leave requests to approve.
                </Typography>
              </Box>
            )}
          </Card>
        )}

        {/* Approval Confirmation Dialog */}
        <Dialog
          open={approveDialog.open}
          onClose={() => setApproveDialog({ open: false, leave: null, action: '' })}
        >
          <DialogTitle>
            Confirm {approveDialog.action === 'approve' ? 'Approval' : 'Rejection'}
          </DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to {approveDialog.action} the leave request from {approveDialog.leave?.employee_name}?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setApproveDialog({ open: false, leave: null, action: '' })}>
              Cancel
            </Button>
            <Button
              onClick={() => handleApproveReject(approveDialog.leave?.id, approveDialog.action)}
              color={approveDialog.action === 'approve' ? 'success' : 'error'}
              variant="contained"
            >
              {approveDialog.action === 'approve' ? 'Approve' : 'Reject'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  </>
);
};

export default Leave;
