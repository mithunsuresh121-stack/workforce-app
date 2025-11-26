import React from 'react';
import {
  UserIcon,
  EnvelopeIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  PencilIcon,
  CameraIcon
} from '@heroicons/react/24/outline';

const ProfileCard = ({ user, profile, onEdit }) => {
  if (!user) {
    return (
      <div className="w-full bg-white rounded-lg shadow">
        <div className="text-center p-6">
          <UserIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-xl font-semibold text-gray-600">
            User not found
          </h2>
          <p className="text-sm text-gray-600 mt-2">
            Please log in to view your profile
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
        return 'red';
      case 'manager':
        return 'blue';
      case 'employee':
        return 'green';
      default:
        return 'gray';
    }
  };

  return (
    <div className="w-full bg-white rounded-lg shadow">
      <div className="p-6">
        {/* Profile Picture Section */}
        <div className="text-center mb-6">
          <div className="relative inline-block">
            <img
              src={profile?.profile_picture_url || user.profile_picture_url || 'https://via.placeholder.com/150'}
              alt={user.full_name}
              className="w-24 h-24 mx-auto mb-3 rounded-full ring-4 ring-blue-50 object-cover"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/150';
              }}
            />
            {!profile?.profile_picture_url && !user.profile_picture_url && (
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 text-white text-2xl font-bold flex items-center justify-center w-24 h-24 rounded-full">
                {getInitials(user.full_name)}
              </div>
            )}
            <button
              onClick={onEdit}
              title="Change Profile Picture"
              className="absolute bottom-0 right-0 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full shadow-lg transition-colors"
            >
              <CameraIcon className="h-4 w-4" />
            </button>
          </div>

          {/* User Info */}
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-gray-800">
              {user.full_name}
            </h3>
            <p className="text-sm text-gray-600 flex items-center justify-center gap-1">
              <EnvelopeIcon className="h-4 w-4" />
              {user.email}
            </p>

            {/* Role Badge */}
            <div className="flex justify-center">
              <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full capitalize ${
                getRoleColor(user.role) === 'red' ? 'bg-red-100 text-red-800' :
                getRoleColor(user.role) === 'blue' ? 'bg-blue-100 text-blue-800' :
                getRoleColor(user.role) === 'green' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {user.role?.toUpperCase() || 'USER'}
              </span>
            </div>
          </div>
        </div>

        {/* Profile Stats */}
        {profile && (
          <div className="space-y-4 mb-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 font-medium mb-2">
                Profile Status
              </p>
              <div className="flex justify-center">
                <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full capitalize ${
                  profile.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {profile.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            {/* Quick Info */}
          <div className="space-y-3 text-sm">
            {profile.department && (
              <div className="flex items-center gap-2 text-gray-600">
                <BuildingOfficeIcon className="h-4 w-4 text-blue-500 flex-shrink-0" />
                <span>{profile.department}</span>
              </div>
            )}
            {profile.position && (
              <div className="flex items-center gap-2 text-gray-600">
                <UserIcon className="h-4 w-4 text-green-500 flex-shrink-0" />
                <span>{profile.position}</span>
              </div>
            )}
            {profile.city && (
              <div className="flex items-center gap-2 text-gray-600">
                <MapPinIcon className="h-4 w-4 text-purple-500 flex-shrink-0" />
                <span>{profile.city}</span>
              </div>
            )}
          </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onEdit}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors"
          >
            <PencilIcon className="h-4 w-4" />
            Edit Profile
          </button>

          <button
            className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            View Full Profile
          </button>
        </div>

        {/* Last Updated */}
        {profile?.updated_at && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-600 text-center">
              Last updated: {new Date(profile.updated_at).toLocaleDateString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileCard;
