import React, { useEffect, useState } from 'react';
import { getCurrentUserProfile, getMyLeaves, createLeave } from '../lib/api';

interface LeaveRequest {
  id: number;
  tenant_id: string;
  employee_id: number;
  type: string;
  start_at: string;
  end_at: string;
  status: string;
}

const LeaveManagementScreen: React.FC = () => {
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newLeave, setNewLeave] = useState<Partial<LeaveRequest>>({
    type: '',
    start_at: '',
    end_at: '',
  });
  const [userProfile, setUserProfile] = useState<any>(null);

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const profile = await getCurrentUserProfile();
        setUserProfile(profile);
      } catch (err) {
        setError('Failed to load user profile');
      }
    };
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (!userProfile) return;
    fetchLeaves();
  }, [userProfile]);

  const fetchLeaves = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyLeaves();
      setLeaves(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setNewLeave({
      ...newLeave,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userProfile) {
      setError('User profile not loaded');
      return;
    }
    try {
      const leavePayload = {
        tenant_id: userProfile.company_id,
        employee_id: userProfile.id,
        type: newLeave.type,
        start_at: newLeave.start_at,
        end_at: newLeave.end_at,
        status: 'Pending',
      };
      await createLeave(leavePayload);
      await fetchLeaves();
      setNewLeave({ type: '', start_at: '', end_at: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Leave Management</h1>
      {error && <div className="text-red-600 mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-2">
          <label htmlFor="type" className="block mb-1">Leave Type</label>
          <select
            id="type"
            name="type"
            value={newLeave.type || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          >
            <option value="">Select type</option>
            <option value="vacation">Vacation</option>
            <option value="sick">Sick</option>
            <option value="personal">Personal</option>
          </select>
        </div>
        <div className="mb-2">
          <label htmlFor="start_at" className="block mb-1">Start Date</label>
          <input
            type="date"
            id="start_at"
            name="start_at"
            value={newLeave.start_at || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          />
        </div>
        <div className="mb-2">
          <label htmlFor="end_at" className="block mb-1">End Date</label>
          <input
            type="date"
            id="end_at"
            name="end_at"
            value={newLeave.end_at || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Submit Leave Request
        </button>
      </form>
      <h2 className="text-xl font-semibold mb-2">My Leave Requests</h2>
      {loading ? (
        <p>Loading leaves...</p>
      ) : (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2">Type</th>
              <th className="border border-gray-300 p-2">Start Date</th>
              <th className="border border-gray-300 p-2">End Date</th>
              <th className="border border-gray-300 p-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {leaves.map((leave) => (
              <tr key={leave.id}>
                <td className="border border-gray-300 p-2">{leave.type}</td>
                <td className="border border-gray-300 p-2">{new Date(leave.start_at).toLocaleDateString()}</td>
                <td className="border border-gray-300 p-2">{new Date(leave.end_at).toLocaleDateString()}</td>
                <td className="border border-gray-300 p-2">{leave.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default LeaveManagementScreen;
