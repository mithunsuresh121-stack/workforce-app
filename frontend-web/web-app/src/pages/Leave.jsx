import PageLayout from "../layouts/PageLayout";
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
          </PageLayout>
  );
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
        </PageLayout>
  );
}
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved': return 'green';
      case 'Pending': return 'orange';
      case 'Rejected': return 'red';
      default: return 'gray';
        </PageLayout>
  );
}
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Approved': return <CheckCircleIcon className="h-4 w-4" />;
      case 'Pending': return <ClockIcon className="h-4 w-4" />;
      case 'Rejected': return <XCircleIcon className="h-4 w-4" />;
      default: return <ExclamationTriangleIcon className="h-4 w-4" />;
        </PageLayout>
  );
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
      </Card>
    );
      </PageLayout>
  );
}

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <Typography variant="h3" color="blue-gray">
          Leave Management
        </Typography>
        <Button
          onClick={() => setDialogOpen(true)    </PageLayout>
  );
}
          className="flex items-center gap-2"
        >
          <PlusIcon className="h-4 w-4" />
          Request Leave
        </Button>
      </Card>

      {error && (
        <Alert color="red" className="mb-6">
          {error    </PageLayout>
  );
}
        </Alert>
      )    </PageLayout>
  );
}

      {/* Leave Balances */    </PageLayout>
  );
}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {Object.entries(leaveBalances).map(([type, balance]) => (
          <Card key={type}>
            <CardBody>
              <Typography variant="h6" color="blue-gray" className="mb-2">
                {type    </PageLayout>
  );
}
              </Typography>
              <div className="flex justify-between items-center mb-2">
                <Typography variant="small" color="gray">
                  Used: {balance.used} days
                </Typography>
                <Typography variant="small" color="gray">
                  Total: {balance.total} days
                </Typography>
              </Card>
              <Progress
                value={(balance.used / balance.total) * 100    </PageLayout>
  );
}
                color={balance.used / balance.total > 0.8 ? 'red' : 'blue'    </PageLayout>
  );
}
                className="h-2"
              />
              <Typography variant="small" color="gray" className="mt-1">
                {balance.total - balance.used} days remaining
              </Typography>
            </CardBody>
          </Card>
        ))    </PageLayout>
  );
}
      </Card>

      {/* Filters */    </PageLayout>
  );
}
      <Card className="mb-6">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <select
                value={statusFilter    </PageLayout>
  );
}
                onChange={(e) => setStatusFilter(e.target.value)    </PageLayout>
  );
}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </Card>
            <div>
              <select
                value={typeFilter    </PageLayout>
  );
}
                onChange={(e) => setTypeFilter(e.target.value)    </PageLayout>
  );
}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="Annual Leave">Annual Leave</option>
                <option value="Sick Leave">Sick Leave</option>
                <option value="Personal Leave">Personal Leave</option>
              </select>
            </Card>
            <div className="flex items-end">
              <Button
                variant="outlined"
                onClick={() => {
                  setStatusFilter('');
                  setTypeFilter('');
                }    </PageLayout>
  );
}
                className="w-full"
              >
                Clear Filters
              </Button>
            </Card>
          </Card>
        </CardBody>
      </Card>

      {/* Leave History */    </PageLayout>
  );
}
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
                        {leave.type    </PageLayout>
  );
}
                      </Typography>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="h-4 w-4 text-gray-400" />
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()    </PageLayout>
  );
}
                        </Typography>
                      </Card>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {leave.days || calculateDays(leave.startDate, leave.endDate)    </PageLayout>
  );
}
                      </Typography>
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Chip
                        icon={getStatusIcon(leave.status)    </PageLayout>
  );
}
                        color={getStatusColor(leave.status)    </PageLayout>
  );
}
                        value={leave.status    </PageLayout>
  );
}
                        size="sm"
                      />
                    </td>
                    <td className="p-4 border-b border-blue-gray-50">
                      <Typography variant="small" color="blue-gray" className="font-normal">
                        {leave.reason    </PageLayout>
  );
}
                      </Typography>
                    </td>
                  </tr>
                ))    </PageLayout>
  );
}
              </tbody>
            </table>
          </Card>

          {filteredLeaves.length === 0 && (
            <div className="text-center py-12">
              <Typography variant="h6" color="gray">
                No leave requests found matching your criteria.
              </Typography>
            </Card>
          )    </PageLayout>
  );
}
        </CardBody>
      </Card>

      {/* Leave Request Dialog */    </PageLayout>
  );
}
      <Dialog open={dialogOpen} handler={setDialogOpen} size="lg">
        <DialogHeader>Request Leave</DialogHeader>
        <DialogBody divider>
          <Formik
            initialValues={{
              type: '',
              startDate: '',
              endDate: '',
              reason: ''
            }    </PageLayout>
  );
}
            validationSchema={validationSchema    </PageLayout>
  );
}
            onSubmit={handleSubmit    </PageLayout>
  );
}
          >
            {({ values, errors, touched, setFieldValue }) => (
              <Form className="space-y-6">
                <Select
                  label="Leave Type"
                  value={values.type    </PageLayout>
  );
}
                  onChange={(value) => setFieldValue('type', value)    </PageLayout>
  );
}
                  error={touched.type && errors.type    </PageLayout>
  );
}
                >
                  <Option value="Annual Leave">Annual Leave</Option>
                  <Option value="Sick Leave">Sick Leave</Option>
                  <Option value="Personal Leave">Personal Leave</Option>
                </Select>

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    type="date"
                    label="Start Date"
                    value={values.startDate    </PageLayout>
  );
}
                    onChange={(e) => setFieldValue('startDate', e.target.value)    </PageLayout>
  );
}
                    error={touched.startDate && errors.startDate    </PageLayout>
  );
}
                  />
                  <Input
                    type="date"
                    label="End Date"
                    value={values.endDate    </PageLayout>
  );
}
                    onChange={(e) => setFieldValue('endDate', e.target.value)    </PageLayout>
  );
}
                    error={touched.endDate && errors.endDate    </PageLayout>
  );
}
                  />
                </Card>

                <Textarea
                  label="Reason"
                  value={values.reason    </PageLayout>
  );
}
                  onChange={(e) => setFieldValue('reason', e.target.value)    </PageLayout>
  );
}
                  error={touched.reason && errors.reason    </PageLayout>
  );
}
                />

                {values.startDate && values.endDate && (
                  <Alert color="blue">
                    Total days: {calculateDays(values.startDate, values.endDate)    </PageLayout>
  );
}
                  </Alert>
                )    </PageLayout>
  );
}
              </Form>
            )    </PageLayout>
  );
}
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
            }    </PageLayout>
  );
}
            loading={submitting    </PageLayout>
  );
}
            disabled={submitting    </PageLayout>
  );
}
          >
            {submitting ? 'Submitting...' : 'Submit Request'    </PageLayout>
  );
}
          </Button>
        </DialogFooter>
      </Dialog>
    </Card>
  );
};

export default Leave;
