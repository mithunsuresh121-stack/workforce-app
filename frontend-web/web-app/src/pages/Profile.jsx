import React, { useState, useEffect } from 'react';
import {
  UserIcon,
  PhoneIcon,
  CalendarIcon,
  PencilIcon,
  ShareIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { useAuth, api } from '../contexts/AuthContext';
import ProfileCard from '../components/ProfileCard_linear';
import ProfileDetails from '../components/ProfileDetails_linear';
import EditProfileForm from '../components/EditProfileForm_enhanced';

const Profile = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (profile) {
      setUser({
        full_name: authUser?.full_name,
        role: authUser?.role,
        employee_id: profile.employee_id,
        profile_picture_url: profile.profile_picture_url,
      });
    }
  }, [profile, authUser]);

  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });

  // Calculate profile completion percentage
  const calculateProfileCompletion = (profile) => {
    if (!profile) return 0;
    const fields = ['department', 'position', 'phone', 'hire_date', 'address', 'city', 'emergency_contact', 'employee_id'];
    const filledFields = fields.filter(field => profile[field]).length;
    return Math.round((filledFields / fields.length) * 100);
  };

  const tabs = [
    { label: 'Overview', value: 'overview', icon: UserIcon },
    { label: 'Personal Info', value: 'personal', icon: UserIcon },
    { label: 'Contact Details', value: 'contact', icon: PhoneIcon },
    { label: 'Work Info', value: 'work', icon: CalendarIcon },
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        // Fetch employee profile from backend
        const response = await api.get('/profile/me');
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        // Use mock data for demonstration when database is not available
        setProfile({
          id: 1,
          user_id: 35,
          company_id: 1,
          department: 'Engineering',
          position: 'Software Engineer',
          phone: '+1-555-0123',
          hire_date: '2023-01-15T00:00:00Z',
          address: '123 Tech Street',
          city: 'San Francisco',
          emergency_contact: 'Jane Doe - +1-555-0456',
          employee_id: 'EMP001',
          profile_picture_url: null,
          is_active: true
        });
        setAlert({ show: true, message: 'Using demo data - Database connection issue detected.', type: 'warning' });
      } finally {
        setLoading(false);
      }
    };

    if (authUser) {
      fetchProfile();
    }
  }, [authUser]);

  const handleEditSuccess = () => {
    setEditing(false);
    setAlert({ show: true, message: 'Profile update request submitted successfully! It will be reviewed by an administrator.', type: 'success' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex justify-center items-center">
        <div className="text-center bg-surface border border-border rounded-lg p-8 shadow-linear-lg">
          <div className="w-8 h-8 border-2 border-accent-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-neutral-900 mb-2">
            Loading Profile...
          </h3>
          <p className="text-neutral-600">
            Please wait while we fetch your information
          </p>
        </div>
      </div>
    );
  }

  const profileCompletion = calculateProfileCompletion(profile);

  return (
    <div className="min-h-screen bg-surface">
      {/* Modern Header Section */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          {/* Header Content */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-semibold text-neutral-900 mb-2">
                Employee Profile
              </h1>
              <div className="flex items-center gap-2 text-neutral-600">
                <UserIcon className="w-5 h-5 flex-shrink-0" />
                <span>Manage your personal and professional information</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 lg:flex-shrink-0">
              <button className="flex items-center justify-center gap-2 px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 hover:border-neutral-300 transition-colors duration-200 min-w-[120px]">
                <ArrowDownTrayIcon className="w-5 h-5" />
                <span className="hidden sm:inline font-medium">Export</span>
              </button>
              <button
                onClick={() => setEditing(true)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 min-w-[140px] font-medium"
              >
                <PencilIcon className="w-5 h-5" />
                <span>Edit Profile</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Profile Completion Status */}
        <div className="mb-8 bg-surface border border-border rounded-lg p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
                  <CheckCircleIcon className="w-6 h-6 text-success-500" />
                  Profile Completion
                </h3>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  profileCompletion === 100 ? 'bg-success-100 text-success-700' :
                  profileCompletion >= 75 ? 'bg-accent-100 text-accent-700' :
                  'bg-warning-100 text-warning-700'
                }`}>
                  {profileCompletion}% Complete
                </div>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-3 mb-3">
                <div
                  className={`h-3 rounded-full transition-all duration-300 ${
                    profileCompletion === 100 ? 'bg-success-500' : 'bg-accent-500'
                  }`}
                  style={{ width: `${profileCompletion}%` }}
                ></div>
              </div>
              <p className="text-neutral-600">
                {profileCompletion === 100
                  ? '🎉 Your profile is complete! Great job maintaining your information.'
                  : `📝 ${100 - profileCompletion}% of fields need to be filled to complete your profile.`
                }
              </p>
            </div>
            {profileCompletion < 100 && (
              <div className="flex-shrink-0">
                <button
                  onClick={() => setEditing(true)}
                  className="flex items-center gap-2 px-4 py-2 text-accent-600 border border-accent-200 rounded-lg hover:bg-accent-50 transition-colors duration-200"
                >
                  <PencilIcon className="w-4 h-4" />
                  Complete Profile
                </button>
              </div>
            )}
          </div>
        </div>

        {alert.show && (
          <div className={`mb-6 p-4 rounded-lg border ${
            alert.type === 'success'
              ? 'bg-success-50 border-success-200 text-success-800'
              : 'bg-danger-50 border-danger-200 text-danger-800'
          }`}>
            <div className="flex items-start gap-3">
              {alert.type === 'success' ? (
                <CheckCircleIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
              ) : (
                <ExclamationTriangleIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
              )}
              <p>{alert.message}</p>
              <button
                onClick={() => setAlert({ show: false })}
                className="ml-auto text-current hover:opacity-70"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Profile Card - Left Sidebar */}
          <div className="xl:col-span-1">
            <div className="sticky top-8">
              <ProfileCard
                user={user}
                profile={profile}
                onEdit={() => setEditing(true)}
              />
            </div>
          </div>

          {/* Profile Details - Main Content */}
          <div className="xl:col-span-3">
            <div className="bg-surface border border-border rounded-lg overflow-hidden">
              <div className="border-b border-border">
                <div className="flex">
                  {tabs.map(({ label, value, icon: Icon }) => (
                    <button
                      key={value}
                      onClick={() => setActiveTab(value)}
                      className={`flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors duration-200 ${
                        activeTab === value
                          ? 'text-accent-600 border-b-2 border-accent-500 bg-accent-50'
                          : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="p-6">
                {activeTab === 'overview' && <ProfileDetails profile={profile} view="overview" />}
                {activeTab === 'personal' && <ProfileDetails profile={profile} view="personal" />}
                {activeTab === 'contact' && <ProfileDetails profile={profile} view="contact" />}
                {activeTab === 'work' && <ProfileDetails profile={profile} view="work" />}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Dialog */}
      {editing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-lg shadow-linear-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h2 className="text-xl font-semibold text-neutral-900">
                  Edit Profile
                </h2>
                <p className="text-neutral-600 mt-1">
                  Request changes to your profile information
                </p>
              </div>
              <div className="flex items-center gap-2 px-3 py-1 bg-warning-100 text-warning-700 rounded-full text-sm font-medium">
                <ClockIcon className="w-4 h-4" />
                Pending Admin Review
              </div>
            </div>
            <div className="p-6">
              <EditProfileForm
                profile={profile}
                onClose={() => setEditing(false)}
                onSuccess={handleEditSuccess}
              />
            </div>
            <div className="flex justify-end gap-3 p-6 border-t border-border bg-neutral-50">
              <button
                onClick={() => setEditing(false)}
                className="px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
