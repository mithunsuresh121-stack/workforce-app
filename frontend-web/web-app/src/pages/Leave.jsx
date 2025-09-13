import React, { useState, useEffect, useMemo } from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import {
  Card,
  CardBody,
  CardHeader,
  Typography,
  Button,
  Input,
  Textarea,
  Select,
  Option,
  Chip,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Spinner,
  Alert,
  IconButton,
  Progress
} from '@material-tailwind/react';
import {
  PlusIcon,
  CalendarDaysIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const Leave = () => {
  const [leaves, setLeaves] = useState([]);
  const [leaveBalances, setLeaveBalances] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchLeaveData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch leave requests
        const leavesResponse = await axios.get('/api/leaves');
        setLeaves(leavesResponse.data);

        // Fetch leave balances
        const balancesResponse = await axios.get('/api/leaves/balances');
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

  const filteredLeaves = useMemo(() => {
    return leaves.filter(leave => {
      const matchesStatus = !statusFilter || leave.status === statusFilter;
      const matchesType = !typeFilter || leave.type === typeFilter;
      return matchesStatus && matchesType;
    });
  }, [leaves, statusFilter, typeFilter]);

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
      const response = await axios.post('/api/leaves', values);
      setLeaves([response.data, ...leaves]);
      setDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('Error submitting leave request:', error);
      setError('Failed to submit leave request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved': return 'green';
      case 'Pending': return 'orange';
      case 'Rejected': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Approved': return <CheckCircleIcon className="h-4 w-4" />;
      case 'Pending': return <ClockIcon className="h-4 w-4" />;
      case 'Rejected': return <XCircleIcon className="h-4 w-4" />;
      default: return <ExclamationTriangleIcon className="h-4 w-4" />;
    }
  };

  const calculateDays = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
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
      <div className="flex justify-between items-center mb-6">
        <Typography variant="h3" color="blue-gray">
          Leave Management
        </Typography>
        <Button
          onClick={() => setDialogOpen(true)}
          className="flex items-center gap-2"
        >
          <PlusIcon className="h-4 w-4" />
          Request Leave
        </Button>
      </div>

      {error && (
        <Alert color="red" className="mb-6">
          {error}
        </Alert>
      )}

      {/* Leave Balances */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {Object.entries(leaveBalances).map(([type, balance]) => (
          <Card key={type}>
            <CardBody>
              <Typography variant="h6" color="blue-gray" className="mb-2">
                {type}
              </Typography>
              <div className="flex justify-between items-center mb-2">
                <Typography variant="small" color="gray">
                  Used: {balance.used} days
                </Typography>
                <Typography variant="small" color="gray">
                  Total: {balance.total} days
                </Typography>
              </div>
              <Progress
                value={(balance.used / balance.total) * 100}
                color={balance.used / balance.total > 0.8 ? 'red' : 'blue'}
                className="h-2"
              />
              <Typography variant="small" color="gray" className="mt-1">
                {balance.total - balance.used} days remaining
              </Typography>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
            <div>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="Annual Leave">Annual Leave</option>
                <option value="Sick Leave">Sick Leave</option>
                <option value="Personal Leave">Personal Leave</option>
              </select>
            </div>
            <div className="flex items-end">
              <Button
                variant="outlined"
                onClick={() => {
                  setStatusFilter('');
                  setTypeFilter('');
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Leave History */}
      <Card>
        <CardHeader floated={false} shadow={false} color="transparent">
          <Typography variant="h5" color="blue-gray">
            Leave History
          </Typography>
        </CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full min-w-max table-auto text-left">
              <thead>
                <tr>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Type
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Dates
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Days
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Status
                    </Typography>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                      Reason
                    </Typography>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredLeaves.map((leave) => (
                  <tr key={leave.id}>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {leave.type}
                      </Typography>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="h-4 w-4 text-gray-400" />
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                        </Typography>
                      </div>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {leave.days || calculateDays(leave.startDate, leave.endDate)}
                      </Typography>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Chip
                        icon={getStatusIcon(leave.status)}
                        color={getStatusColor(leave.status)}
                        value={leave.status}
                        size="sm"
                      />
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {leave.reason}
                      </Typography>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredLeaves.length === 0 && (
            <div className="text-center py-12">
              <Typography variant="h6" color="gray">
                No leave requests found matching your criteria.
              </Typography>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Leave Request Dialog */}
      <Dialog open={dialogOpen} handler={setDialogOpen} size="lg">
        <DialogHeader>Request Leave</DialogHeader>
        <DialogBody divider>
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
            {({ values, errors, touched, setFieldValue }) => (
              <Form className="space-y-6">
                <Select
                  label="Leave Type"
                  value={values.type}
                  onChange={(value) => setFieldValue('type', value)}
                  error={touched.type && errors.type}
                >
                  <Option value="Annual Leave">Annual Leave</Option>
                  <Option value="Sick Leave">Sick Leave</Option>
                  <Option value="Personal Leave">Personal Leave</Option>
                </Select>

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    type="date"
                    label="Start Date"
                    value={values.startDate}
                    onChange={(e) => setFieldValue('startDate', e.target.value)}
                    error={touched.startDate && errors.startDate}
                  />
                  <Input
                    type="date"
                    label="End Date"
                    value={values.endDate}
                    onChange={(e) => setFieldValue('endDate', e.target.value)}
                    error={touched.endDate && errors.endDate}
                  />
                </div>

                <Textarea
                  label="Reason"
                  value={values.reason}
                  onChange={(e) => setFieldValue('reason', e.target.value)}
                  error={touched.reason && errors.reason}
                />

                {values.startDate && values.endDate && (
                  <Alert color="blue">
                    Total days: {calculateDays(values.startDate, values.endDate)}
                  </Alert>
                )}
              </Form>
            )}
          </Formik>
        </DialogBody>
        <DialogFooter>
          <Button variant="text" color="red" onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="gradient"
            color="green"
            onClick={() => {
              const form = document.querySelector('form');
              if (form) form.requestSubmit();
            }}
            loading={submitting}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Request'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

export default Leave;
