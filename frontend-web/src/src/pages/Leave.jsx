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
  XMarkIcon
} from '@heroicons/react/24/outline';
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
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-accent-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-neutral-600">Loading leave data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-900">Leave Management</h1>
              <p className="text-neutral-600 mt-1">Manage your leave requests and balances</p>
            </div>
            <button
              onClick={() => setDialogOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              Request Leave
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6">
        {error && (
          <div className="mb-6 p-4 bg-danger-50 border border-danger-200 text-danger-800 rounded-lg">
            <div className="flex items-start gap-3">
              <ExclamationTriangleIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <p>{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-current hover:opacity-70"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Leave Balances */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {Object.entries(leaveBalances).map(([type, balance]) => (
            <div key={type} className="bg-surface border border-border rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">{type}</h3>
                <div className="flex items-center gap-2 text-neutral-500">
                  <ClockIcon className="w-5 h-5" />
                  <span className="text-sm font-medium">{balance.total - balance.used} left</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Used</span>
                  <span className="font-medium text-neutral-900">{balance.used} days</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Total</span>
                  <span className="font-medium text-neutral-900">{balance.total} days</span>
                </div>
                <div className="w-full bg-neutral-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      balance.used / balance.total > 0.8 ? 'bg-danger-500' :
                      balance.used / balance.total > 0.6 ? 'bg-warning-500' : 'bg-accent-500'
                    }`}
                    style={{ width: `${(balance.used / balance.total) * 100}%` }}
                  />
                </div>
                <div className="text-xs text-neutral-500">
                  {Math.round((balance.used / balance.total) * 100)}% utilized
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="bg-surface border border-border rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
            <div className="relative">
              <CalendarDaysIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent appearance-none bg-white"
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
                className="w-full px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Leave History */}
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-border bg-neutral-50">
            <h2 className="text-lg font-semibold text-neutral-900">Leave History</h2>
            <p className="text-sm text-neutral-600 mt-1">View and manage your leave requests</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 border-b border-border">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                    Type
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                    Dates
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                    Days
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                    Reason
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredLeaves.map((leave) => (
                  <tr key={leave.id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-neutral-900">{leave.type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="w-4 h-4 text-neutral-400" />
                        <span className="text-neutral-700">
                          {new Date(leave.startDate).toLocaleDateString()} - {new Date(leave.endDate).toLocaleDateString()}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-neutral-900">
                        {leave.days || calculateDays(leave.startDate, leave.endDate)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                        leave.status === 'Approved' ? 'bg-success-100 text-success-700' :
                        leave.status === 'Pending' ? 'bg-warning-100 text-warning-700' :
                        leave.status === 'Rejected' ? 'bg-danger-100 text-danger-700' :
                        'bg-neutral-100 text-neutral-700'
                      }`}>
                        {leave.status === 'Approved' && <CheckCircleIcon className="w-4 h-4" />}
                        {leave.status === 'Pending' && <ClockIcon className="w-4 h-4" />}
                        {leave.status === 'Rejected' && <XCircleIcon className="w-4 h-4" />}
                        {leave.status}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-neutral-600 max-w-xs truncate">{leave.reason}</p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredLeaves.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CalendarDaysIcon className="w-8 h-8 text-neutral-400" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                No leave requests found
              </h3>
              <p className="text-neutral-600">
                {statusFilter || typeFilter
                  ? "No leave requests match your current filters. Try adjusting your search criteria."
                  : "You haven't submitted any leave requests yet."
                }
              </p>
            </div>
          )}
        </div>

      {/* Leave Request Dialog */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4">
          <div className="bg-surface rounded-lg shadow-linear-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h2 className="text-xl font-semibold text-neutral-900">Request Leave</h2>
                <p className="text-sm text-neutral-600 mt-1">Submit a new leave request</p>
              </div>
              <button
                onClick={() => setDialogOpen(false)}
                className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
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
                <Form className="p-6 space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Leave Type *
                    </label>
                    <select
                      value={values.type}
                      onChange={(e) => setFieldValue('type', e.target.value)}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent bg-white ${
                        touched.type && errors.type ? 'border-danger-300' : 'border-neutral-200'
                      }`}
                    >
                      <option value="">Select leave type</option>
                      <option value="Annual Leave">Annual Leave</option>
                      <option value="Sick Leave">Sick Leave</option>
                      <option value="Personal Leave">Personal Leave</option>
                    </select>
                    {touched.type && errors.type && (
                      <p className="text-danger-600 text-sm mt-1">{errors.type}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Start Date *
                      </label>
                      <input
                        type="date"
                        value={values.startDate}
                        onChange={(e) => setFieldValue('startDate', e.target.value)}
                        className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent ${
                          touched.startDate && errors.startDate ? 'border-danger-300' : 'border-neutral-200'
                        }`}
                      />
                      {touched.startDate && errors.startDate && (
                        <p className="text-danger-600 text-sm mt-1">{errors.startDate}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        End Date *
                      </label>
                      <input
                        type="date"
                        value={values.endDate}
                        onChange={(e) => setFieldValue('endDate', e.target.value)}
                        className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent ${
                          touched.endDate && errors.endDate ? 'border-danger-300' : 'border-neutral-200'
                        }`}
                      />
                      {touched.endDate && errors.endDate && (
                        <p className="text-danger-600 text-sm mt-1">{errors.endDate}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Reason *
                    </label>
                    <textarea
                      value={values.reason}
                      onChange={(e) => setFieldValue('reason', e.target.value)}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent resize-none ${
                        touched.reason && errors.reason ? 'border-danger-300' : 'border-neutral-200'
                      }`}
                      rows={4}
                      placeholder="Please provide a reason for your leave request"
                    />
                    {touched.reason && errors.reason && (
                      <p className="text-danger-600 text-sm mt-1">{errors.reason}</p>
                    )}
                  </div>

                  {values.startDate && values.endDate && (
                    <div className="bg-accent-50 border border-accent-200 text-accent-800 px-4 py-3 rounded-lg">
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="w-5 h-5" />
                        <span className="font-medium">Total days: {calculateDays(values.startDate, values.endDate)}</span>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end gap-3 pt-4 border-t border-border">
                    <button
                      type="button"
                      onClick={() => setDialogOpen(false)}
                      className="px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={submitting}
                      className={`px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium ${
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
    </div>
  );
};

export default Leave;
