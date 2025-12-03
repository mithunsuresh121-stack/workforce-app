import React from 'react';
import {
  BuildingOfficeIcon,
  UserGroupIcon,
  PhoneIcon,
  CalendarDaysIcon,
  MapPinIcon,
  UserIcon,
  HeartIcon
} from '@heroicons/react/24/outline';

const ProfileDetails = ({ profile, view = 'overview' }) => {
  if (!profile) {
    return (
      <div className="text-center py-8">
        <h2 className="text-xl font-semibold text-gray-600">
          Profile details not available
        </h2>
        <p className="text-sm text-gray-600 mt-2">
          Please complete your profile information
        </p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatPhone = (phone) => {
    if (!phone) return 'Not set';
    // Basic phone formatting - you can enhance this based on your needs
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  };

  // Personal Information Fields
  const personalFields = [
    {
      icon: UserIcon,
      label: 'Gender',
      value: profile.gender || 'Not set',
      category: 'personal'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Date of Birth',
      value: profile.date_of_birth ? formatDate(profile.date_of_birth) : 'Not set',
      category: 'personal'
    }
  ];

  // Contact Information Fields
  const contactFields = [
    {
      icon: PhoneIcon,
      label: 'Phone',
      value: formatPhone(profile.phone),
      category: 'contact'
    },
    {
      icon: MapPinIcon,
      label: 'Address',
      value: profile.address || 'Not set',
      category: 'contact'
    },
    {
      icon: BuildingOfficeIcon,
      label: 'City',
      value: profile.city || 'Not set',
      category: 'contact'
    },
    {
      icon: HeartIcon,
      label: 'Emergency Contact',
      value: profile.emergency_contact || 'Not set',
      category: 'contact'
    }
  ];

  // Work Information Fields
  const workFields = [
    {
      icon: BuildingOfficeIcon,
      label: 'Department',
      value: profile.department || 'Not set',
      category: 'work'
    },
    {
      icon: UserGroupIcon,
      label: 'Position',
      value: profile.position || 'Not set',
      category: 'work'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Hire Date',
      value: formatDate(profile.hire_date),
      category: 'work'
    },
    {
      icon: UserIcon,
      label: 'Employee ID',
      value: profile.employee_id || 'Not set',
      category: 'work'
    }
  ];

  const renderField = (field) => {
    const Icon = field.icon;
    return (
      <div key={field.label} className="flex items-start gap-3 p-4 rounded-lg bg-gray-50">
        <div className="flex-shrink-0">
          <Icon className="h-5 w-5 text-blue-500 mt-0.5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-600 font-medium mb-1">
            {field.label}
          </p>
          <p className="text-base text-gray-800 break-words">
            {field.value}
          </p>
        </div>
      </div>
    );
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <h4 className="text-2xl font-bold text-blue-600">
            {workFields.filter(field => field.value !== 'Not set').length}
          </h4>
          <p className="text-sm text-gray-600">
            Work Details
          </p>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <h4 className="text-2xl font-bold text-green-600">
            {contactFields.filter(field => field.value !== 'Not set').length}
          </h4>
          <p className="text-sm text-gray-600">
            Contact Info
          </p>
        </div>
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <h4 className="text-2xl font-bold text-purple-600">
            {personalFields.filter(field => field.value !== 'Not set').length}
          </h4>
          <p className="text-sm text-gray-600">
            Personal Info
          </p>
        </div>
        <div className="text-center p-4 bg-orange-50 rounded-lg">
          <h4 className="text-2xl font-bold text-orange-600">
            {profile.profile_picture_url ? '1' : '0'}
          </h4>
          <p className="text-sm text-gray-600">
            Profile Picture
          </p>
        </div>
      </div>

      {/* Key Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <BuildingOfficeIcon className="h-5 w-5" />
            Work Information
          </h2>
          <div className="space-y-2">
            {workFields.slice(0, 2).map(renderField)}
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <PhoneIcon className="h-5 w-5" />
            Contact Information
          </h2>
          <div className="space-y-2">
            {contactFields.slice(0, 2).map(renderField)}
          </div>
        </div>
      </div>
    </div>
  );

  const renderPersonal = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <UserIcon className="h-5 w-5" />
        Personal Information
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {personalFields.map(renderField)}
      </div>
    </div>
  );

  const renderContact = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <PhoneIcon className="h-5 w-5" />
        Contact Details
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contactFields.map(renderField)}
      </div>
    </div>
  );

  const renderWork = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <BuildingOfficeIcon className="h-5 w-5" />
        Work Information
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {workFields.map(renderField)}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'personal':
        return renderPersonal();
      case 'contact':
        return renderContact();
      case 'work':
        return renderWork();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="space-y-6">
      {renderContent()}
    </div>
  );
};

export default ProfileDetails;
