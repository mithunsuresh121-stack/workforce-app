import React, { useState, useEffect } from 'react';
import { api, useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';

const ManagerApprovals = () => {
  const { user: currentUser } = useAuth();
  const [leaves, setLeaves] = useState([]);
  const [swaps, setSwaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      setLoading(true);
      const [leavesResponse, swapsResponse] = await Promise.all([
        api.get('/leaves?status=Pending'),
        api.get('/shifts/swaps?status=PENDING')
      ]);
      setLeaves(leavesResponse.data);
      setSwaps(swapsResponse.data);
    } catch (error) {
      console.error('Error fetching pending requests:', error);
      toast.error('Failed to load pending requests');
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveApproval = async (leaveId, status) => {
    try {
      setProcessing(leaveId);
      await api.put(`/leaves/${leaveId}/status`, { status });
      toast.success(`Leave ${status.toLowerCase()} successfully`);
      fetchPendingRequests();
    } catch (error) {
      console.error('Error updating leave status:', error);
      toast.error('Failed to update leave status');
    } finally {
      setProcessing(null);
    }
  };

  const handleSwapApproval = async (swapId, action) => {
    try {
      setProcessing(swapId);
      const endpoint = action === 'approve' ? `/shifts/swap-approve/${swapId}` : `/shifts/swap-reject/${swapId}`;
      await api.post(endpoint);
      toast.success(`Swap ${action}d successfully`);
      fetchPendingRequests();
    } catch (error) {
      console.error('Error updating swap status:', error);
      toast.error('Failed to update swap status');
    } finally {
      setProcessing(null);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      Pending: 'bg-yellow-100 text-yellow-800',
      APPROVED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <h1 className="text-2xl font-semibold mb-4">Manager Approvals</h1>

      {/* Pending Leaves */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Pending Leave Requests</h2>
        {leaves.length === 0 ? (
          <p className="text-gray-500">No pending leave requests</p>
        ) : (
          <div className="space-y-4">
            {leaves.map((leave) => (
              <div key={leave.id} className="border rounded-lg p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">{leave.type} - {leave.employee_name || `Employee ${leave.employee_id}`}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(leave.start_at).toLocaleDateString()} - {new Date(leave.end_at).toLocaleDateString()}
                  </p>
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${getStatusBadge(leave.status)}`}>
                    {leave.status}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleLeaveApproval(leave.id, 'APPROVED')}
                    disabled={processing === leave.id}
                    className="flex items-center px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                  >
                    <CheckCircleIcon className="w-4 h-4 mr-1" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleLeaveApproval(leave.id, 'REJECTED')}
                    disabled={processing === leave.id}
                    className="flex items-center px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
                  >
                    <XCircleIcon className="w-4 h-4 mr-1" />
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pending Swaps */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium mb-4">Pending Shift Swap Requests</h2>
        {swaps.length === 0 ? (
          <p className="text-gray-500">No pending swap requests</p>
        ) : (
          <div className="space-y-4">
            {swaps.map((swap) => (
              <div key={swap.id} className="border rounded-lg p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">Swap Request #{swap.id}</p>
                  <p className="text-sm text-gray-600">
                    Requester: {swap.requester_name || `Employee ${swap.requester_id}`}
                  </p>
                  <p className="text-sm text-gray-600">
                    Target: {swap.target_employee_name || `Employee ${swap.target_employee_id}`}
                  </p>
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${getStatusBadge(swap.status)}`}>
                    {swap.status}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleSwapApproval(swap.id, 'approve')}
                    disabled={processing === swap.id}
                    className="flex items-center px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                  >
                    <CheckCircleIcon className="w-4 h-4 mr-1" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleSwapApproval(swap.id, 'reject')}
                    disabled={processing === swap.id}
                    className="flex items-center px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
                  >
                    <XCircleIcon className="w-4 h-4 mr-1" />
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManagerApprovals;
