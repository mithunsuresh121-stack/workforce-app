import React, { useEffect, useState } from 'react';
import { getCurrentUserFullProfile, updateCurrentUserProfile } from '../lib/api';

const ProfileScreen: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [employeeProfile, setEmployeeProfile] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    department: '',
    position: '',
    phone: '',
    hire_date: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCurrentUserFullProfile();
      if (data) {
        setProfile(data.user);
        setEmployeeProfile(data.employee_profile);
        setFormData({
          full_name: data.user.full_name || '',
          email: data.user.email || '',
          department: data.employee_profile?.department || '',
          position: data.employee_profile?.position || '',
          phone: data.employee_profile?.phone || '',
          hire_date: data.employee_profile?.hire_date || '',
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const updateData = {
        user: {
          full_name: formData.full_name,
        },
        employee_profile: {
          department: formData.department || null,
          position: formData.position || null,
          phone: formData.phone || null,
          hire_date: formData.hire_date || null,
        },
      };
      await updateCurrentUserProfile(updateData);
      setIsEditing(false);
      await fetchProfile();
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !profile) {
    return <div>Loading...</div>;
  }

  if (error && !profile) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">My Profile</h1>
      {error && <div className="mb-4 text-red-600">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-semibold mb-1" htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            disabled
            className="w-full border border-gray-300 rounded px-3 py-2 bg-gray-100"
          />
        </div>
        <div>
          <label className="block font-semibold mb-1" htmlFor="full_name">Full Name</label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            disabled={!isEditing}
            required
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block font-semibold mb-1" htmlFor="department">Department</label>
          <input
            type="text"
            id="department"
            name="department"
            value={formData.department}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block font-semibold mb-1" htmlFor="position">Position</label>
          <input
            type="text"
            id="position"
            name="position"
            value={formData.position}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block font-semibold mb-1" htmlFor="phone">Phone</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded px-3 py-2"
            pattern="^\\+?1?[-.\\s]?\\(?([0-9]{3})\\)?[-.\\s]?([0-9]{3})[-.\\s]?([0-9]{4})$"
            title="Phone number format: +1 (555) 123-4567 or similar"
          />
        </div>
        <div>
          <label className="block font-semibold mb-1" htmlFor="hire_date">Hire Date</label>
          <input
            type="date"
            id="hire_date"
            name="hire_date"
            value={formData.hire_date ? formData.hire_date.split('T')[0] : ''}
            onChange={handleChange}
            disabled={!isEditing}
            max={new Date().toISOString().split('T')[0]}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div className="flex space-x-4">
          {!isEditing && (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Edit Profile
            </button>
          )}
          {isEditing && (
            <>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded"
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  fetchProfile();
                }}
                className="px-4 py-2 bg-gray-400 text-white rounded"
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </form>
    </div>
  );
};

export default ProfileScreen;
