import React from 'react';
import {
  BuildingOfficeIcon,
  PhoneIcon,
  CalendarDaysIcon,
  MapPinIcon,
  UserIcon,
  HeartIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  StarIcon,
  BriefcaseIcon,
  HomeIcon
} from '@heroicons/react/24/outline';

const ProfileDetails = ({ profile, view = 'overview' }) => {
  if (!profile) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="h-8 w-48 mx-auto mb-4 bg-gray-200 animate-pulse rounded"></div>
          <div className="h-4 w-64 mx-auto mb-2 bg-gray-200 animate-pulse rounded"></div>
          <div className="h-4 w-56 mx-auto bg-gray-200 animate-pulse rounded"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="p-4 bg-white rounded-lg shadow">
              <div className="h-6 w-32 mb-2 bg-gray-200 animate-pulse rounded"></div>
              <div className="h-4 w-24 bg-gray-200 animate-pulse rounded"></div>
            </div>
          ))}
        </div>
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
      category: 'personal',
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Date of Birth',
      value: profile.date_of_birth ? formatDate(profile.date_of_birth) : 'Not set',
      category: 'personal',
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600'
    }
  ];

  // Contact Information Fields
  const contactFields = [
    {
      icon: PhoneIcon,
      label: 'Phone',
      value: formatPhone(profile.phone),
      category: 'contact',
      color: 'green',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600'
    },
    {
      icon: MapPinIcon,
      label: 'Address',
      value: profile.address || 'Not set',
      category: 'contact',
      color: 'orange',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600'
    },
    {
      icon: HomeIcon,
      label: 'City',
      value: profile.city || 'Not set',
      category: 'contact',
      color: 'indigo',
      bgColor: 'bg-indigo-50',
      iconColor: 'text-indigo-600'
    },
    {
      icon: HeartIcon,
      label: 'Emergency Contact',
      value: profile.emergency_contact || 'Not set',
      category: 'contact',
      color: 'red',
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600'
    }
  ];

  // Work Information Fields
  const workFields = [
    {
      icon: BuildingOfficeIcon,
      label: 'Department',
      value: profile.department || 'Not set',
      category: 'work',
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600'
    },
    {
      icon: BriefcaseIcon,
      label: 'Position',
      value: profile.position || 'Not set',
      category: 'work',
      color: 'emerald',
      bgColor: 'bg-emerald-50',
      iconColor: 'text-emerald-600'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Hire Date',
      value: formatDate(profile.hire_date),
      category: 'work',
      color: 'teal',
      bgColor: 'bg-teal-50',
      iconColor: 'text-teal-600'
    },
    {
      icon: StarIcon,
      label: 'Employee ID',
      value: profile.employee_id || 'Not set',
      category: 'work',
      color: 'amber',
      bgColor: 'bg-amber-50',
      iconColor: 'text-amber-600'
    }
  ];

  const renderField = (field) => {
    const Icon = field.icon;
    const isSet = field.value !== 'Not set';

    return (
      <div key={field.label} className={`transition-all duration-300 hover:shadow-md ${field.bgColor} border-l-4 border-${field.color}-200 bg-white rounded-lg`}>
        <div className="p-4">
          <div className="flex items-start gap-4">
            <div className={`p-2.5 rounded-full ${field.bgColor} flex-shrink-0 self-start mt-1`}>
              <Icon className={`h-5 w-5 ${field.iconColor}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold text-sm text-gray-600">
                  {field.label}
                </p>
                <div className="flex-shrink-0">
                  {isSet ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <ExclamationTriangleIcon className="h-4 w-4 text-amber-500" />
                  )}
                </div>
              </div>
              <h2 className="text-xl font-semibold text-gray-800 break-words leading-relaxed mb-1">
                {field.value}
              </h2>
              {!isSet && (
                <p className="italic text-xs text-gray-600">
                  Click "Edit Profile" to add this information
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const hasWorkData = workFields.some(field => field.value !== 'Not set');
  const hasContactData = contactFields.some(field => field.value !== 'Not set');
  const hasPersonalData = personalFields.some(field => field.value !== 'Not set');

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Quick Stats - Only show categories with data */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {hasWorkData && (
          <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500 rounded-lg">
            <h4 className="text-2xl font-bold text-blue-600">
              {workFields.filter(field => field.value !== 'Not set').length}
            </h4>
            <p className="text-sm text-gray-600 font-medium">
              Work Details
            </p>
          </div>
        )}
        {hasContactData && (
          <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 border-l-4 border-green-500 rounded-lg">
            <h4 className="text-2xl font-bold text-green-600">
              {contactFields.filter(field => field.value !== 'Not set').length}
            </h4>
            <p className="text-sm text-gray-600 font-medium">
              Contact Info
            </p>
          </div>
        )}
        {hasPersonalData && (
          <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-l-4 border-purple-500 rounded-lg">
            <h4 className="text-2xl font-bold text-purple-600">
              {personalFields.filter(field => field.value !== 'Not set').length}
            </h4>
            <p className="text-sm text-gray-600 font-medium">
              Personal Info
            </p>
          </div>
        )}
        <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-l-4 border-orange-500 rounded-lg">
          <h4 className="text-2xl font-bold text-orange-600">
            {profile.profile_picture_url ? '1' : '0'}
          </h4>
          <p className="text-sm text-gray-600 font-medium">
            Profile Picture
          </p>
        </div>
      </div>

      {/* Key Information Sections - Only show sections with data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {hasWorkData && (
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-3 text-left">
              <BriefcaseIcon className="h-5 w-5 text-blue-600 flex-shrink-0" />
              <span>Work Information</span>
            </h3>
            <div className="space-y-3">
              {workFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
            </div>
          </div>
        )}
        {hasContactData && (
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-3 text-left">
              <PhoneIcon className="h-5 w-5 text-green-600 flex-shrink-0" />
              <span>Contact Information</span>
            </h3>
            <div className="space-y-3">
              {contactFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
            </div>
          </div>
        )}
      </div>

      {/* Additional Information - Only show sections with data */}
      {(hasPersonalData || contactFields.filter(field => field.value !== 'Not set').slice(2).length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {hasPersonalData && (
            <div>
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-3 text-left">
                <UserIcon className="h-5 w-5 text-purple-600 flex-shrink-0" />
                <span>Personal Information</span>
              </h3>
              <div className="space-y-3">
                {personalFields.filter(field => field.value !== 'Not set').map(renderField)}
              </div>
            </div>
          )}
          {contactFields.filter(field => field.value !== 'Not set').slice(2).length > 0 && (
            <div>
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-3 text-left">
                <MapPinIcon className="h-5 w-5 text-orange-600 flex-shrink-0" />
                <span>Location & Emergency</span>
              </h3>
              <div className="space-y-3">
                {contactFields.filter(field => field.value !== 'Not set').slice(2).map(renderField)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Show message if no data */}
      {!hasWorkData && !hasContactData && !hasPersonalData && (
        <div className="p-8 text-center bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-600 mb-2">
            No profile information available
          </h3>
          <p className="text-sm text-gray-600">
            Click "Edit Profile" to add your information
          </p>
        </div>
      )}
    </div>
  );

  const renderPersonal = () => (
    <div>
      <Typography variant="h5" color="blue-gray" className="mb-6 flex items-center gap-3 font-bold text-left">
        <UserIcon className="h-5 w-5 text-purple-600 flex-shrink-0" />
        <span>Personal Information</span>
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {personalFields.map(renderField)}
      </div>
    </div>
  );

  const renderContact = () => (
    <div>
      <Typography variant="h5" color="blue-gray" className="mb-6 flex items-center gap-3 font-bold text-left">
        <PhoneIcon className="h-5 w-5 text-green-600 flex-shrink-0" />
        <span>Contact Details</span>
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contactFields.map(renderField)}
      </div>
    </div>
  );

  const renderWork = () => (
    <div>
      <Typography variant="h5" color="blue-gray" className="mb-6 flex items-center gap-3 font-bold text-left">
        <BriefcaseIcon className="h-5 w-5 text-blue-600 flex-shrink-0" />
        <span>Work Information</span>
      </Typography>
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
