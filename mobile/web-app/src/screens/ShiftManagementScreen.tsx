import React, { useEffect, useState } from 'react';
import { getCurrentUserProfile, getMyShifts, createShift } from '../lib/api';

interface Shift {
  id: number;
  tenant_id: string;
  employee_id: number;
  start_at: string;
  end_at: string;
  location: string;
}

const ShiftManagementScreen: React.FC = () => {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newShift, setNewShift] = useState<Partial<Shift>>({
    start_at: '',
    end_at: '',
    location: '',
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
    fetchShifts();
  }, [userProfile]);

  const fetchShifts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyShifts();
      setShifts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewShift({
      ...newShift,
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
      const shiftPayload = {
        tenant_id: userProfile.company_id,
        employee_id: userProfile.id,
        start_at: newShift.start_at,
        end_at: newShift.end_at,
        location: newShift.location,
      };
      await createShift(shiftPayload);
      await fetchShifts();
      setNewShift({ start_at: '', end_at: '', location: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Shift Management</h1>
      {error && <div className="text-red-600 mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-2">
          <label htmlFor="start_at" className="block mb-1">Start Time</label>
          <input
            type="datetime-local"
            id="start_at"
            name="start_at"
            value={newShift.start_at || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          />
        </div>
        <div className="mb-2">
          <label htmlFor="end_at" className="block mb-1">End Time</label>
          <input
            type="datetime-local"
            id="end_at"
            name="end_at"
            value={newShift.end_at || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          />
        </div>
        <div className="mb-2">
          <label htmlFor="location" className="block mb-1">Location</label>
          <input
            type="text"
            id="location"
            name="location"
            value={newShift.location || ''}
            onChange={handleInputChange}
            required
            className="border p-2 rounded w-full"
          />
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Submit Shift
        </button>
      </form>
      <h2 className="text-xl font-semibold mb-2">My Shifts</h2>
      {loading ? (
        <p>Loading shifts...</p>
      ) : (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2">Start Time</th>
              <th className="border border-gray-300 p-2">End Time</th>
              <th className="border border-gray-300 p-2">Location</th>
            </tr>
          </thead>
          <tbody>
            {shifts.map((shift) => (
              <tr key={shift.id}>
                <td className="border border-gray-300 p-2">{new Date(shift.start_at).toLocaleString()}</td>
                <td className="border border-gray-300 p-2">{new Date(shift.end_at).toLocaleString()}</td>
                <td className="border border-gray-300 p-2">{shift.location}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ShiftManagementScreen;
