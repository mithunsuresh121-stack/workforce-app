import React from 'react';
import {
  UserIcon,
  EnvelopeIcon,
  BuildingOfficeIcon,
  PencilIcon,
  CameraIcon,
  CheckCircleIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/react/24/outline';

const ProfileCard = ({ user, profile, onEdit }) => {
  if (!user) {
    return (
      <div style={{
        width: '100%',
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '0.75rem',
        boxShadow: 'var(--shadow)',
        padding: '1.5rem'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}>
            <div style={{
              height: '5rem',
              width: '5rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '50%',
              margin: '0 auto 1rem'
            }}></div>
            <div style={{
              height: '1.5rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '0.25rem',
              width: '75%',
              margin: '0 auto 0.5rem'
            }}></div>
            <div style={{
              height: '1rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '0.25rem',
              width: '50%',
              margin: '0 auto'
            }}></div>
          </div>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: 'var(--text-primary)',
            marginTop: '1rem'
          }}>
            Loading Profile...
          </h3>
          <p style={{
            color: 'var(--text-secondary)',
            marginTop: '0.5rem'
          }}>
            Please wait while we fetch your information
          </p>
        </div>
      </div>
    );
  }

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };



  const getRoleIcon = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return <StarIcon className="h-4 w-4" />;
      case 'manager':
        return <BuildingOfficeIcon className="h-4 w-4" />;
      case 'employee':
        return <UserIcon className="h-4 w-4" />;
      default:
        return <UserIcon className="h-4 w-4" />;
    }
  };

  const getRoleColorClasses = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return { backgroundColor: '#fef2f2', color: '#b91c1c', borderColor: '#fecaca' };
      case 'manager':
        return { backgroundColor: '#fef3c7', color: '#d97706', borderColor: '#fde68a' };
      case 'employee':
        return { backgroundColor: '#dcfce7', color: '#15803d', borderColor: '#bbf7d0' };
      default:
        return { backgroundColor: '#f3f4f6', color: '#374151', borderColor: '#d1d5db' };
    }
  };

  return (
    <div style={{
      width: '100%',
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '0.75rem',
      boxShadow: 'var(--shadow)',
      transition: 'all 0.3s'
    }} className="hover:shadow-lg overflow-hidden">
      {/* Profile Picture Section */}
      <div style={{ textAlign: 'center', padding: '1.5rem', paddingBottom: '1rem' }}>
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <div style={{
            position: 'absolute',
            inset: '-0.25rem',
            background: 'linear-gradient(to right, var(--accent), var(--primary))',
            borderRadius: '50%',
            filter: 'blur(2px)',
            opacity: 0.25,
            transition: 'opacity 0.3s'
          }} className="group-hover:opacity-75"></div>
          <div style={{
            position: 'relative',
            width: '5rem',
            height: '5rem',
            background: 'linear-gradient(to bottom right, var(--accent), var(--primary))',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            border: '4px solid var(--surface)',
            boxShadow: 'var(--shadow-lg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {profile?.profile_picture_url || user.profile_picture_url ? (
              <img
                src={profile?.profile_picture_url || user.profile_picture_url}
                alt={user.full_name}
                style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
              />
            ) : (
              <span style={{ fontSize: '1.5rem', fontWeight: '700', color: 'white' }}>
                {getInitials(user.full_name)}
              </span>
            )}
          </div>
          <button
            onClick={onEdit}
            style={{
              position: 'absolute',
              bottom: '1rem',
              right: '50%',
              transform: 'translateX(2.5rem)',
              backgroundColor: 'var(--accent)',
              color: 'white',
              padding: '0.5rem',
              borderRadius: '50%',
              boxShadow: 'var(--shadow-lg)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            className="hover:scale-110"
          >
            <CameraIcon style={{ width: '1rem', height: '1rem' }} />
          </button>
        </div>

        {/* User Info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text-primary)' }}>
            {user.full_name}
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <EnvelopeIcon style={{ width: '1rem', height: '1rem' }} />
            <span style={{ fontSize: '0.875rem' }}>{user.email}</span>
          </div>

          {/* Role Badge */}
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.75rem' }}>
            <div style={{
              padding: '0 0.75rem 0.25rem',
              borderRadius: '50rem',
              fontSize: '0.875rem',
              fontWeight: '500',
              border: '1px solid',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
              ...getRoleColorClasses(user.role)
            }}>
              {getRoleIcon(user.role)}
              <span style={{ textTransform: 'capitalize' }}>{user.role || 'User'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Stats */}
      {profile && (
        <div style={{ padding: '0 1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Status Section */}
          <div style={{ textAlign: 'center' }}>
            <h4 style={{
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '0.5rem'
            }}>
              Status
            </h4>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <div style={{
                padding: '0 0.75rem 0.25rem',
                borderRadius: '50rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                backgroundColor: profile.is_active ? '#dcfce7' : '#fef2f2',
                color: profile.is_active ? '#15803d' : '#dc2626',
                border: `1px solid ${profile.is_active ? '#bbf7d0' : '#fecaca'}`
              }}>
                {profile.is_active ? (
                  <>
                    <CheckCircleIcon style={{ width: '1rem', height: '1rem' }} />
                    Active
                  </>
                ) : (
                  <>
                    <ClockIcon style={{ width: '1rem', height: '1rem' }} />
                    Inactive
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Quick Info - Only show if there's data */}
          {(profile.position || profile.department) && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <h4 style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: 'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                textAlign: 'center'
              }}>
                Quick Info
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                {profile.position && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
                    <div style={{
                      backgroundColor: '#dcfce7',
                      padding: '0.375rem',
                      borderRadius: '50%'
                    }}>
                      <UserIcon style={{ width: '0.75rem', height: '0.75rem', color: '#15803d' }} />
                    </div>
                    <span style={{ fontWeight: '500' }}>{profile.position}</span>
                  </div>
                )}
                {profile.department && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
                    <div style={{
                      backgroundColor: '#fef3c7',
                      padding: '0.375rem',
                      borderRadius: '50%'
                    }}>
                      <BuildingOfficeIcon style={{ width: '0.75rem', height: '0.75rem', color: '#d97706' }} />
                    </div>
                    <span style={{ fontWeight: '500' }}>{profile.department}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ padding: '0 1.5rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <button
          onClick={onEdit}
          className="btn"
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            backgroundColor: 'var(--accent)',
            color: 'white',
            fontWeight: '500'
          }}
        >
          <PencilIcon style={{ width: '1rem', height: '1rem' }} />
          Edit Profile
        </button>

        <button style={{
          width: '100%',
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
          transition: 'all 0.2s'
        }} className="hover:bg-gray-50 hover:border-gray-300">
          <UserIcon style={{ width: '1rem', height: '1rem' }} />
          View Full Profile
        </button>
      </div>

      {/* Last Updated - Only show if there's actual data */}
      {profile?.updated_at && (
        <div style={{
          padding: '0 1.5rem 1.5rem',
          borderTop: '1px solid #e5e7eb'
        }}>
          <p style={{
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            textAlign: 'center',
            marginTop: '1rem'
          }}>
            Last updated: {new Date(profile.updated_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </p>
        </div>
      )}
    </div>
  );
};

export default ProfileCard;
