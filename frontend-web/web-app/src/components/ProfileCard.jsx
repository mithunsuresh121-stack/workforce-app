import React from 'react';
import { Card, CardBody, Avatar, Typography, Button, Chip, Tooltip } from '@material-tailwind/react';
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
      <Card className="w-full">
        <CardBody className="text-center p-6">
          <UserIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <Typography variant="h6" color="gray">
            User not found
          </Typography>
          <Typography variant="small" color="gray" className="mt-2">
            Please log in to view your profile
          </Typography>
        </CardBody>
      </Card>
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
    <Card className="w-full">
      <CardBody className="p-6">
        {/* Profile Picture Section */}
        <div className="text-center mb-6">
          <div className="relative inline-block">
            <Avatar
              src={profile?.profile_picture_url || user.profile_picture_url || 'https://via.placeholder.com/150'}
              alt={user.full_name}
              size="xl"
              className="mx-auto mb-3 ring-4 ring-blue-50"
              placeholder={
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-2xl font-bold flex items-center justify-center w-full h-full">
                  {getInitials(user.full_name)}
                </div>
              }
            />
            <Tooltip content="Change Profile Picture">
              <button
                onClick={onEdit}
                className="absolute bottom-0 right-0 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full shadow-lg transition-colors"
              >
                <CameraIcon className="h-4 w-4" />
              </button>
            </Tooltip>
          </div>

          {/* User Info */}
          <div className="space-y-2">
            <Typography variant="h5" color="blue-gray" className="font-bold">
              {user.full_name}
            </Typography>
            <Typography variant="small" color="gray" className="flex items-center justify-center gap-1">
              <EnvelopeIcon className="h-4 w-4" />
              {user.email}
            </Typography>

            {/* Role Badge */}
            <div className="flex justify-center">
              <Chip
                size="sm"
                variant="ghost"
                color={getRoleColor(user.role)}
                value={user.role?.toUpperCase() || 'USER'}
                className="capitalize"
              />
            </div>
          </div>
        </div>

        {/* Profile Stats */}
        {profile && (
          <div className="space-y-4 mb-6">
            <div className="text-center">
              <Typography variant="small" color="gray" className="font-medium mb-2">
                Profile Status
              </Typography>
              <div className="flex justify-center">
                <Chip
                  size="sm"
                  variant="ghost"
                  color={profile.is_active ? 'green' : 'red'}
                  value={profile.is_active ? 'Active' : 'Inactive'}
                  icon={profile.is_active ? null : <UserIcon className="h-4 w-4" />}
                />
              </div>
            </div>

            {/* Quick Info */}
            <div className="space-y-3 text-sm">
              {profile.department && (
                <div className="flex items-center gap-2 text-gray-600">
                  <BuildingOfficeIcon className="h-4 w-4 text-blue-500" />
                  <span>{profile.department}</span>
                </div>
              )}
              {profile.position && (
                <div className="flex items-center gap-2 text-gray-600">
                  <UserIcon className="h-4 w-4 text-green-500" />
                  <span>{profile.position}</span>
                </div>
              )}
              {profile.city && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPinIcon className="h-4 w-4 text-purple-500" />
                  <span>{profile.city}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={onEdit}
            className="w-full flex items-center justify-center gap-2"
            size="sm"
          >
            <PencilIcon className="h-4 w-4" />
            Edit Profile
          </Button>

          <Button
            variant="outlined"
            className="w-full"
            size="sm"
          >
            View Full Profile
          </Button>
        </div>

        {/* Last Updated */}
        {profile?.updated_at && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Typography variant="small" color="gray" className="text-center">
              Last updated: {new Date(profile.updated_at).toLocaleDateString()}
            </Typography>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default ProfileCard;
