import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUserProfile, updateCurrentUserProfile } from '../api/userApi.js';

const ProfileScreen: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    department: '',
    position: '',
    phone: '',
    hire_date: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCurrentUserProfile();
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        department: data.employee_profile?.department ?? '',
        position: data.employee_profile?.position ?? '',
        phone: data.employee_profile?.phone ?? '',
        hire_date: data.employee_profile?.hire_date ? String(data.employee_profile.hire_date).split('T')[0] ?? '' : '',
      });
    } catch (err: any) {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const validateForm = () => {
    if (formData.phone && !/^\+?[0-9\s\-()]+$/.test(formData.phone)) {
      setError('Invalid phone number format');
      return false;
    }
    if (formData.hire_date && new Date(formData.hire_date) > new Date()) {
      setError('Hire date cannot be in the future');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    setError(null);
    try {
      await updateCurrentUserProfile({
        user: { full_name: formData.full_name },
        employee_profile: {
          department: formData.department || null,
          position: formData.position || null,
          phone: formData.phone || null,
          hire_date: formData.hire_date || null,
        },
      });
      setSuccess('Profile updated successfully');
      setEditMode(false);
      fetchProfile();
    } catch (err: any) {
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4" data-testid="page-title-user-profile">User Profile</h1>
      {error && <div className="mb-4 text-red-600" data-testid="profile-error-message">{error}</div>}
      {success && <div className="mb-4 text-green-600" data-testid="profile-success-message">{success}</div>}
      {!editMode ? (
        <div>
          <p><strong>Full Name:</strong> <span data-testid="profile-full-name">{profile?.full_name || '-'}</span></p>
          <p><strong>Department:</strong> <span data-testid="profile-department">{profile?.employee_profile?.department || '-'}</span></p>
          <p><strong>Position:</strong> <span data-testid="profile-position">{profile?.employee_profile?.position || '-'}</span></p>
          <p><strong>Phone:</strong> <span data-testid="profile-phone">{profile?.employee_profile?.phone || '-'}</span></p>
          <p><strong>Hire Date:</strong> <span data-testid="profile-hire-date">{profile?.employee_profile?.hire_date ? profile.employee_profile.hire_date.split('T')[0] : '-'}</span></p>
          <button
            onClick={() => setEditMode(true)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
            data-testid="profile-edit-button"
          >
            Edit Profile
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-semibold">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
              data-testid="profile-full-name"
            />
          </div>
          <div>
            <label className="block font-semibold">Department</label>
            <input
              type="text"
              name="department"
              value={formData.department}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              data-testid="profile-department"
            />
          </div>
          <div>
            <label className="block font-semibold">Position</label>
            <input
              type="text"
              name="position"
              value={formData.position}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              data-testid="profile-position"
            />
          </div>
          <div>
            <label className="block font-semibold">Phone</label>
            <input
              type="text"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              data-testid="profile-phone"
            />
          </div>
          <div>
            <label className="block font-semibold">Hire Date</label>
            <input
              type="date"
              name="hire_date"
              value={formData.hire_date}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              data-testid="profile-hire-date"
            />
          </div>
          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded"
              data-testid="profile-save-button"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => {
                setEditMode(false);
                setError(null);
                fetchProfile();
              }}
              className="px-4 py-2 bg-gray-300 rounded"
              data-testid="profile-cancel-button"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ProfileScreen;
