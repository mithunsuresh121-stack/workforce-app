import React, { useState, useEffect } from 'react';
import {
  UserIcon,
  PhoneIcon,
  CalendarIcon,
  PencilIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import { useAuth, api } from '../contexts/AuthContext';
import ProfileCard from '../components/ProfileCard_linear';
import ProfileDetails from '../components/ProfileDetails_linear';
import EditProfileForm from '../components/EditProfileForm_linear';

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
      <div style={{
        minHeight: '100vh',
        backgroundColor: 'var(--surface)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{
          textAlign: 'center',
          backgroundColor: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: '0.5rem',
          padding: '2rem',
          boxShadow: 'var(--shadow)'
        }}>
          <div style={{
            width: '2rem',
            height: '2rem',
            border: '2px solid var(--accent)',
            borderTop: '2px solid transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: 'var(--text-primary)',
            marginBottom: '0.5rem'
          }}>
            Loading Profile...
          </h3>
          <p style={{
            color: 'var(--text-secondary)'
          }}>
            Please wait while we fetch your information
          </p>
        </div>
      </div>
    );
  }

  const profileCompletion = calculateProfileCompletion(profile);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--surface)' }}>
      {/* Modern Header Section */}
      <div style={{ backgroundColor: 'var(--surface)', borderBottom: '1px solid var(--border)' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem 0 1.5rem', paddingTop: '1.5rem', paddingBottom: '1.5rem' }}>
          {/* Header Content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} className="lg:flex-row lg:items-center lg:justify-between">
            <div style={{ flex: 1, minWidth: 0 }}>
              <h1 style={{ fontSize: '1.5rem', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                Employee Profile
              </h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <UserIcon style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
                <span>Manage your personal and professional information</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }} className="sm:flex-row lg:flex-shrink-0">
              <button style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                color: 'var(--text-secondary)',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
                backgroundColor: 'transparent',
                cursor: 'pointer',
                fontWeight: '500',
                transition: 'all 0.2s',
                minWidth: '7.5rem'
              }} className="hover:bg-gray-50 hover:border-gray-300">
                <ArrowDownTrayIcon style={{ width: '1.25rem', height: '1.25rem' }} />
                <span className="hidden sm:inline">Export</span>
              </button>
              <button
                onClick={() => setEditing(true)}
                className="btn"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  backgroundColor: 'var(--accent)',
                  color: 'white',
                  fontWeight: '500',
                  minWidth: '8.75rem'
                }}
              >
                <PencilIcon style={{ width: '1.25rem', height: '1.25rem' }} />
                <span>Edit Profile</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem 0 1.5rem', paddingTop: '2rem', paddingBottom: '2rem' }}>
        {/* Profile Completion Status */}
        <div style={{ marginBottom: '2rem', backgroundColor: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '0.5rem', padding: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }} className="lg:flex-row lg:items-center lg:justify-between">
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircleIcon style={{ width: '1.5rem', height: '1.5rem', color: '#10b981' }} />
                  Profile Completion
                </h3>
                <div style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '50rem',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  backgroundColor: profileCompletion === 100 ? '#dcfce7' : profileCompletion >= 75 ? '#fef3c7' : '#fef2f2',
                  color: profileCompletion === 100 ? '#15803d' : profileCompletion >= 75 ? '#d97706' : '#dc2626'
                }}>
                  {profileCompletion}% Complete
                </div>
              </div>
              <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '0.25rem', height: '0.75rem', marginBottom: '0.75rem' }}>
                <div
                  style={{
                    height: '0.75rem',
                    borderRadius: '0.25rem',
                    transition: 'all 0.3s',
                    width: `${profileCompletion}%`,
                    backgroundColor: profileCompletion === 100 ? '#10b981' : 'var(--accent)'
                  }}
                ></div>
              </div>
              <p style={{ color: 'var(--text-secondary)' }}>
                {profileCompletion === 100
                  ? '🎉 Your profile is complete! Great job maintaining your information.'
                  : `📝 ${100 - profileCompletion}% of fields need to be filled to complete your profile.`
                }
              </p>
            </div>
            {profileCompletion < 100 && (
              <div style={{ flexShrink: 0 }}>
                <button
                  onClick={() => setEditing(true)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent-light)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'transparent',
                    cursor: 'pointer',
                    fontWeight: '500',
                    transition: 'all 0.2s'
                  }}
                  className="hover:bg-accent-50"
                >
                  <PencilIcon style={{ width: '1rem', height: '1rem' }} />
                  Complete Profile
                </button>
              </div>
            )}
          </div>
        </div>

        {alert.show && (
          <div style={{
            marginBottom: '1.5rem',
            padding: '1rem',
            borderRadius: '0.5rem',
            border: `1px solid ${alert.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
            backgroundColor: alert.type === 'success' ? '#dcfce7' : '#fef2f2',
            color: alert.type === 'success' ? '#166534' : '#991b1b'
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              {alert.type === 'success' ? (
                <CheckCircleIcon style={{ width: '1.25rem', height: '1.25rem', marginTop: '0.125rem', flexShrink: 0 }} />
              ) : (
                <ExclamationTriangleIcon style={{ width: '1.25rem', height: '1.25rem', marginTop: '0.125rem', flexShrink: 0 }} />
              )}
              <p>{alert.message}</p>
              <button
                onClick={() => setAlert({ show: false })}
                style={{
                  marginLeft: 'auto',
                  color: 'currentColor',
                  cursor: 'pointer'
                }}
                className="hover:opacity-70"
              >
                <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '2rem'
        }} className="xl:grid-cols-4">
          {/* Profile Card - Left Sidebar */}
          <div className="xl:col-span-1">
            <div style={{ position: 'sticky', top: '2rem' }}>
              <ProfileCard
                user={user}
                profile={profile}
                onEdit={() => setEditing(true)}
              />
            </div>
          </div>

          {/* Profile Details - Main Content */}
          <div className="xl:col-span-3">
            <div style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: '0.5rem',
              overflow: 'hidden'
            }}>
              <div style={{ borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex' }}>
                  {tabs.map(({ label, value, icon: Icon }) => (
                    <button
                      key={value}
                      onClick={() => setActiveTab(value)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '1rem 1.5rem',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        transition: 'all 0.2s',
                        borderBottom: activeTab === value ? '2px solid var(--accent)' : 'none',
                        backgroundColor: activeTab === value ? '#fef3c7' : 'transparent',
                        color: activeTab === value ? 'var(--accent)' : 'var(--text-secondary)',
                        cursor: 'pointer'
                      }}
                      className={activeTab !== value ? 'hover:bg-gray-50 hover:text-gray-900' : ''}
                    >
                      <Icon style={{ width: '1.25rem', height: '1.25rem' }} />
                      <span>{label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div style={{ padding: '1.5rem' }}>
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
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          padding: '1rem'
        }}>
          <div style={{
            backgroundColor: 'var(--surface)',
            borderRadius: '0.5rem',
            boxShadow: 'var(--shadow)',
            maxWidth: '56rem',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1.5rem',
              borderBottom: '1px solid var(--border)'
            }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                  Edit Profile
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Request changes to your profile information
                </p>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.25rem 0.75rem',
                backgroundColor: '#fef3c7',
                color: '#d97706',
                borderRadius: '50rem',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                <ClockIcon style={{ width: '1rem', height: '1rem' }} />
                Pending Admin Review
              </div>
            </div>
            <div style={{ padding: '1.5rem' }}>
              <EditProfileForm
                profile={profile}
                onClose={() => setEditing(false)}
                onSuccess={handleEditSuccess}
              />
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.75rem',
              padding: '1.5rem',
              borderTop: '1px solid var(--border)',
              backgroundColor: '#f9fafb'
            }}>
              <button
                onClick={() => setEditing(false)}
                style={{
                  padding: '0.5rem 1rem',
                  color: 'var(--text-secondary)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  backgroundColor: 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                className="hover:bg-gray-50"
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
