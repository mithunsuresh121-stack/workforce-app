import PageLayout from "../layouts/PageLayout";
import React, { useState, useEffect, useMemo } from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { api } from '../contexts/AuthContext';

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
        const leavesResponse = await api.get('/leaves');
        setLeaves(leavesResponse.data);

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
      const response = await api.post('/leaves', values);
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
      case 'Approved': return '✓';
      case 'Pending': return '⏳';
      case 'Rejected': return '✗';
      default: return '⚠';
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <PageLayout>
      <div className="p-4">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-3xl font-bold text-gray-800">
            Leave Management
          </h3>
          <button
            onClick={() => setDialogOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            +
            Request Leave
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Leave Balances */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {Object.entries(leaveBalances).map(([type, balance]) => (
            <div key={type} className="bg-white p-6 rounded-lg shadow-md border">
              <h6 className="text-lg font-semibold text-gray-800 mb-2">
                {type}
              </h6>
              <div className="flex justify-between items-center mb-2">
                <p className="text-sm text-gray-600">
                  Used: {balance.used} days
                </p>
                <p className="text-sm text-gray-600">
                  Total: {balance.total} days
                </p>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div
                  className={`h-2 rounded ${
                    balance.used / balance.total > 0.8 ? 'bg-red-600' : 'bg-blue-600'
                  }`}
                  style={{ width: `${(balance.used / balance.total) * 100}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {balance.total - balance.used} days remaining
              </p>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md border mb-6">
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
              <button
                onClick={() => {
                  setStatusFilter('');
                  setTypeFilter('');
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Leave History */}
        <div className="bg-white rounded-lg shadow-md border">
          <div className="p-4 border-b border-gray-200">
            <h5 className="text-lg font-semibold text-gray-800">Leave History</h5>
          </div>
          <div className="overflow-x-auto p-4">
            <table className="w-full min-w-max table-auto text-left">
              <thead>
                <tr>
                  <th className="border-b border-gray-200 bg-gray-50 p-4">
                    <p className="text-sm font-normal leading-none opacity-70">
                      Type
                    </p>
                  </th>
                  <th className="border-b border-gray-200 bg-gray-50 p-4">
                    <p className="text-sm font-normal leading-none opacity-70">
                      Dates
                    </p>
                  </th>
                  <th className="border-b border-gray-200 bg-gray-50 p-4">
                    <p className="text-sm font-normal leading-none opacity-70">
                      Days
                    </p>
                  </th>
                  <th className="border-b border-gray-200 bg-gray-50 p-4">
                    <p className="text-sm font-normal leading-none opacity-70">
                      Status
                    </p>
                  </th>
                  <th className="border-b border-gray-200 bg-gray-50 p-4">
                    <p className="text-sm font-normal leading-none opacity-70">
                      Reason
                    </p>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredLeaves.map((leave) => (
                  <tr key={leave.id}>
                    <td className="p-4 border-b border-gray-100">
                      <p className="text-sm font-normal">
                        {leave.type}
                      </p>
                    </td>
                    <td className="p-4 border-b border-gray-100">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">📅</span>
                        <p className="text-sm font-normal">
                          {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                        </p>
                      </div>
                    </td>
                    <td className="p-4 border-b border-gray-100">
                      <p className="text-sm font-normal">
                        {leave.days || calculateDays(leave.startDate, leave.endDate)}
                      </p>
                    </td>
                    <td className="p-4 border-b border-gray-100">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                        leave.status === 'Approved' ? 'bg-green-100 text-green-800 border-green-200' :
                        leave.status === 'Pending' ? 'bg-orange-100 text-orange-800 border-orange-200' :
                        leave.status === 'Rejected' ? 'bg-red-100 text-red-800 border-red-200' :
                        'bg-gray-100 text-gray-800 border-gray-200'
                      }`}>
                        {getStatusIcon(leave.status)} {leave.status}
                      </span>
                    </td>
                    <td className="p-4 border-b border-gray-100">
                      <p className="text-sm font-normal">
                        {leave.reason}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredLeaves.length === 0 && (
            <div className="text-center py-12">
              <p className="text-lg font-semibold text-gray-600">
                No leave requests found matching your criteria.
              </p>
            </div>
          )}
        </div>

        {/* Leave Request Dialog */}
        {dialogOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6">
              <h4 className="text-xl font-semibold mb-4">Request Leave</h4>
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
                    <div>
                      <label className="block mb-1 font-medium">Leave Type</label>
                      <select
                        value={values.type}
                        onChange={(e) => setFieldValue('type', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                          touched.type && errors.type ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        <option value="">Select leave type</option>
                        <option value="Annual Leave">Annual Leave</option>
                        <option value="Sick Leave">Sick Leave</option>
                        <option value="Personal Leave">Personal Leave</option>
                      </select>
                      {touched.type && errors.type && (
                        <p className="text-red-500 text-sm mt-1">{errors.type}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block mb-1 font-medium">Start Date</label>
                        <input
                          type="date"
                          value={values.startDate}
                          onChange={(e) => setFieldValue('startDate', e.target.value)}
                          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                            touched.startDate && errors.startDate ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {touched.startDate && errors.startDate && (
                          <p className="text-red-500 text-sm mt-1">{errors.startDate}</p>
                        )}
                      </div>
                      <div>
                        <label className="block mb-1 font-medium">End Date</label>
                        <input
                          type="date"
                          value={values.endDate}
                          onChange={(e) => setFieldValue('endDate', e.target.value)}
                          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                            touched.endDate && errors.endDate ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {touched.endDate && errors.endDate && (
                          <p className="text-red-500 text-sm mt-1">{errors.endDate}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block mb-1 font-medium">Reason</label>
                      <textarea
                        value={values.reason}
                        onChange={(e) => setFieldValue('reason', e.target.value)}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                          touched.reason && errors.reason ? 'border-red-500' : 'border-gray-300'
                        }`}
                      />
                      {touched.reason && errors.reason && (
                        <p className="text-red-500 text-sm mt-1">{errors.reason}</p>
                      )}
                    </div>

                    {values.startDate && values.endDate && (
                      <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded">
                        Total days: {calculateDays(values.startDate, values.endDate)}
                      </div>
                    )}

                    <div className="flex justify-end gap-4">
                      <button
                        type="button"
                        onClick={() => setDialogOpen(false)}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={submitting}
                        className={`px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                          submitting ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {submitting ? 'Submitting...' : 'Submit Request'}
                      </button>
                    </div>
                  </Form>
                )}
              </Formik>
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
};

export default Leave;
