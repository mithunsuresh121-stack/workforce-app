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
      <div className="w-full bg-surface border border-border rounded-linear shadow-linear p-6">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="h-20 w-20 bg-neutral-200 rounded-full mx-auto mb-4"></div>
            <div className="h-6 bg-neutral-200 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-neutral-200 rounded w-1/2 mx-auto"></div>
          </div>
          <h3 className="text-lg font-semibold text-neutral-900 mt-4">
            Loading Profile...
          </h3>
          <p className="text-neutral-600 mt-2">
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

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return 'danger';
      case 'manager':
        return 'accent';
      case 'employee':
        return 'success';
      default:
        return 'neutral';
    }
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
        return 'bg-danger-100 text-danger-700 border-danger-200';
      case 'manager':
        return 'bg-accent-100 text-accent-700 border-accent-200';
      case 'employee':
        return 'bg-success-100 text-success-700 border-success-200';
      default:
        return 'bg-neutral-100 text-neutral-700 border-neutral-200';
    }
  };

  return (
    <div className="w-full bg-surface border border-border rounded-linear shadow-linear hover:shadow-linear-lg transition-all duration-300 overflow-hidden">
      {/* Profile Picture Section */}
      <div className="text-center p-6 pb-4">
        <div className="relative inline-block group">
          <div className="absolute -inset-1 bg-gradient-to-r from-accent-500 to-accent-600 rounded-full blur opacity-25 group-hover:opacity-75 transition duration-300"></div>
          <div className="relative w-20 h-20 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full mx-auto mb-4 ring-4 ring-surface shadow-lg flex items-center justify-center">
            {profile?.profile_picture_url || user.profile_picture_url ? (
              <img
                src={profile?.profile_picture_url || user.profile_picture_url}
                alt={user.full_name}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              <span className="text-2xl font-bold text-white">
                {getInitials(user.full_name)}
              </span>
            )}
          </div>
          <button
            onClick={onEdit}
            className="absolute bottom-4 right-1/2 transform translate-x-10 bg-accent-500 hover:bg-accent-600 text-white p-2 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110"
          >
            <CameraIcon className="h-4 w-4" />
          </button>
        </div>

        {/* User Info */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-neutral-900">
            {user.full_name}
          </h3>
          <div className="flex items-center justify-center gap-2 text-neutral-600">
            <EnvelopeIcon className="h-4 w-4" />
            <span className="text-sm">{user.email}</span>
          </div>

          {/* Role Badge */}
          <div className="flex justify-center mt-3">
            <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getRoleColorClasses(user.role)} flex items-center gap-1`}>
              {getRoleIcon(user.role)}
              <span className="capitalize">{user.role || 'User'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Stats */}
      {profile && (
        <div className="px-6 pb-4 space-y-4">
          {/* Status Section */}
          <div className="text-center">
            <h4 className="text-sm font-semibold text-neutral-600 uppercase tracking-wide mb-2">
              Status
            </h4>
            <div className="flex justify-center">
              <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${
                profile.is_active
                  ? 'bg-success-100 text-success-700 border border-success-200'
                  : 'bg-danger-100 text-danger-700 border border-danger-200'
              }`}>
                {profile.is_active ? (
                  <>
                    <CheckCircleIcon className="h-4 w-4" />
                    Active
                  </>
                ) : (
                  <>
                    <ClockIcon className="h-4 w-4" />
                    Inactive
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Quick Info - Only show if there's data */}
          {(profile.position || profile.department) && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-neutral-600 uppercase tracking-wide text-center">
                Quick Info
              </h4>
              <div className="space-y-2 text-sm">
                {profile.position && (
                  <div className="flex items-center justify-center gap-2 text-neutral-700">
                    <div className="bg-success-100 p-1.5 rounded-full">
                      <UserIcon className="h-3 w-3 text-success-600" />
                    </div>
                    <span className="font-medium">{profile.position}</span>
                  </div>
                )}
                {profile.department && (
                  <div className="flex items-center justify-center gap-2 text-neutral-700">
                    <div className="bg-accent-100 p-1.5 rounded-full">
                      <BuildingOfficeIcon className="h-3 w-3 text-accent-600" />
                    </div>
                    <span className="font-medium">{profile.department}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="px-6 pb-6 space-y-3">
        <button
          onClick={onEdit}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium"
        >
          <PencilIcon className="h-4 w-4" />
          Edit Profile
        </button>

        <button className="w-full flex items-center justify-center gap-2 px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 hover:border-neutral-300 transition-colors duration-200 font-medium">
          <UserIcon className="h-4 w-4" />
          View Full Profile
        </button>
      </div>

      {/* Last Updated - Only show if there's actual data */}
      {profile?.updated_at && (
        <div className="px-6 pb-6 pt-0 border-t border-neutral-200">
          <p className="text-xs text-neutral-500 text-center mt-4">
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
