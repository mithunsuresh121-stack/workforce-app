import React from 'react';
import { Card, CardBody, Avatar, Typography, Button, Chip, Tooltip, Badge } from '@material-tailwind/react';
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
      <Card className="w-full shadow-lg border-0 bg-gradient-to-br from-gray-50 to-blue-50">
        <CardBody className="text-center p-8">
          <div className="animate-pulse">
            <div className="h-20 w-20 bg-gray-300 rounded-full mx-auto mb-4"></div>
            <div className="h-6 bg-gray-300 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
          </div>
          <Typography variant="h6" color="gray" className="mt-4">
            Loading Profile...
          </Typography>
          <Typography variant="small" color="gray" className="mt-2">
            Please wait while we fetch your information
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

  return (
    <Card className="w-full shadow-xl border-0 bg-gradient-to-br from-white to-blue-50 hover:shadow-2xl transition-all duration-300 overflow-hidden">
      {/* Decorative top border */}
      <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500"></div>

      <CardBody className="p-6">
        {/* Profile Picture Section */}
        <div className="text-center mb-6">
          <div className="relative inline-block group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <Avatar
              src={profile?.profile_picture_url || user.profile_picture_url || 'https://via.placeholder.com/150'}
              alt={user.full_name}
              size="xl"
              className="relative mx-auto mb-4 ring-4 ring-white shadow-lg"
              placeholder={
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-3xl font-bold flex items-center justify-center w-full h-full rounded-full">
                  {getInitials(user.full_name)}
                </div>
              }
            />
            <Tooltip content="Change Profile Picture">
              <button
                onClick={onEdit}
                className="absolute bottom-2 right-2 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white p-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110"
              >
                <CameraIcon className="h-5 w-5" />
              </button>
            </Tooltip>
          </div>

          {/* User Info */}
          <div className="space-y-3">
            <Typography variant="h5" color="blue-gray" className="font-bold tracking-tight">
              {user.full_name}
            </Typography>
            <Typography variant="small" color="gray" className="flex items-center justify-center gap-2">
              <EnvelopeIcon className="h-4 w-4" />
              {user.email}
            </Typography>

            {/* Role Badge */}
            <div className="flex justify-center">
              <Chip
                size="sm"
                variant="filled"
                color={getRoleColor(user.role)}
                value={user.role?.toUpperCase() || 'USER'}
                icon={getRoleIcon(user.role)}
                className="capitalize shadow-md"
              />
            </div>
          </div>
        </div>

        {/* Profile Stats */}
        {profile && (
          <div className="space-y-4 mb-6">
            {/* Status Section */}
            <div className="text-center">
              <Typography variant="small" color="gray" className="font-semibold mb-2 uppercase tracking-wide">
                Status
              </Typography>
              <div className="flex justify-center">
                <Badge
                  color={profile.is_active ? 'green' : 'red'}
                  className="px-3 py-1 flex items-center gap-1"
                >
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
                </Badge>
              </div>
            </div>

            {/* Quick Info - Only show if there's data */}
            {(profile.position || profile.department) && (
              <div className="space-y-3">
                <Typography variant="small" color="gray" className="font-semibold uppercase tracking-wide text-center">
                  Quick Info
                </Typography>
                <div className="space-y-2 text-sm">
                  {profile.position && (
                    <div className="flex items-center justify-center gap-2 text-gray-700">
                      <div className="bg-green-100 p-1.5 rounded-full">
                        <UserIcon className="h-3 w-3 text-green-600" />
                      </div>
                      <Typography variant="small" color="blue-gray" className="font-medium">
                        {profile.position}
                      </Typography>
                    </div>
                  )}
                  {profile.department && (
                    <div className="flex items-center justify-center gap-2 text-gray-700">
                      <div className="bg-blue-100 p-1.5 rounded-full">
                        <BuildingOfficeIcon className="h-3 w-3 text-blue-600" />
                      </div>
                      <Typography variant="small" color="blue-gray" className="font-medium">
                        {profile.department}
                      </Typography>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={onEdit}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all duration-300"
            size="lg"
          >
            <PencilIcon className="h-5 w-5" />
            Edit Profile
          </Button>

          <Button
            variant="outlined"
            className="w-full border-2 hover:bg-blue-50 hover:border-blue-300 transition-all duration-300"
            size="lg"
          >
            <UserIcon className="h-5 w-5 mr-2" />
            View Full Profile
          </Button>
        </div>

        {/* Last Updated - Only show if there's actual data */}
        {profile?.updated_at && (
          <div className="mt-6 pt-4 border-t border-gray-200">
            <Typography variant="small" color="gray" className="text-center">
              Last updated: {new Date(profile.updated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
              })}
            </Typography>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default ProfileCard;
