import React, { useEffect, useState } from 'react';
import { getLeaveRequests, createLeaveRequest, updateLeaveRequest } from '../api/leaveApi.js';

interface LeaveRequest {
  id: number;
  user_id: number;
  start_date: string;
  end_date: string;
  reason?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const LeaveScreen: React.FC = () => {
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newLeave, setNewLeave] = useState({ start_date: '', end_date: '', reason: '' });

  useEffect(() => {
    fetchLeaveRequests();
  }, []);

  const fetchLeaveRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getLeaveRequests();
      setLeaveRequests(data);
    } catch (err: any) {
      setError('Failed to load leave requests');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createLeaveRequest({
        start_date: newLeave.start_date,
        end_date: newLeave.end_date,
        reason: newLeave.reason,
      });
      setNewLeave({ start_date: '', end_date: '', reason: '' });
      fetchLeaveRequests();
    } catch (err: any) {
      setError('Failed to create leave request');
    }
  };

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await updateLeaveRequest(id, { status });
      fetchLeaveRequests();
    } catch (err: any) {
      setError('Failed to update leave request');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Leave Management</h1>
      {error && <div className="mb-4 text-red-600">{error}</div>}
      <form onSubmit={handleCreateLeave} className="mb-4">
        <input
          type="date"
          placeholder="Start date"
          value={newLeave.start_date}
          onChange={(e) => setNewLeave({ ...newLeave, start_date: e.target.value })}
          className="border border-gray-300 rounded px-3 py-2 mr-2"
          required
        />
        <input
          type="date"
          placeholder="End date"
          value={newLeave.end_date}
          onChange={(e) => setNewLeave({ ...newLeave, end_date: e.target.value })}
          className="border border-gray-300 rounded px-3 py-2 mr-2"
          required
        />
        <input
          type="text"
          placeholder="Reason"
          value={newLeave.reason}
          onChange={(e) => setNewLeave({ ...newLeave, reason: e.target.value })}
          className="border border-gray-300 rounded px-3 py-2 mr-2"
        />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">
          Request Leave
        </button>
      </form>
      {loading ? (
        <div>Loading leave requests...</div>
      ) : (
        <ul>
          {leaveRequests.map((leave) => (
            <li key={leave.id} className="mb-2 p-2 border border-gray-300 rounded">
              <p>From: {leave.start_date} To: {leave.end_date}</p>
              <p>Reason: {leave.reason}</p>
              <p>Status: {leave.status}</p>
              <button
                onClick={() => handleUpdateStatus(leave.id, leave.status === 'pending' ? 'approved' : 'pending')}
                className="px-2 py-1 bg-green-600 text-white rounded"
              >
                Toggle Status
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LeaveScreen;
