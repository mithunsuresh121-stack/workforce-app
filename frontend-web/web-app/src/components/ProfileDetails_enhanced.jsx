import React from 'react';
import { Typography, Card, CardBody, Skeleton } from '@material-tailwind/react';
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
          <Skeleton className="h-8 w-48 mx-auto mb-4" />
          <Skeleton className="h-4 w-64 mx-auto mb-2" />
          <Skeleton className="h-4 w-56 mx-auto" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton className="h-6 w-32 mb-2" />
              <Skeleton className="h-4 w-24" />
            </Card>
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
      <Card key={field.label} className={`transition-all duration-300 hover:shadow-md ${field.bgColor} border-l-4 border-${field.color}-200`}>
        <CardBody className="p-4">
          <div className="flex items-start gap-4">
            <div className={`p-2.5 rounded-full ${field.bgColor} flex-shrink-0 self-start mt-1`}>
              <Icon className={`h-5 w-5 ${field.iconColor}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <Typography variant="small" color="gray" className="font-semibold text-sm">
                  {field.label}
                </Typography>
                <div className="flex-shrink-0">
                  {isSet ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <ExclamationTriangleIcon className="h-4 w-4 text-amber-500" />
                  )}
                </div>
              </div>
              <Typography variant="h6" color="blue-gray" className="break-words leading-relaxed mb-1">
                {field.value}
              </Typography>
              {!isSet && (
                <Typography variant="small" color="gray" className="italic text-xs">
                  Click "Edit Profile" to add this information
                </Typography>
              )}
            </div>
          </div>
        </CardBody>
      </Card>
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
          <Card className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500">
            <Typography variant="h4" color="blue" className="font-bold">
              {workFields.filter(field => field.value !== 'Not set').length}
            </Typography>
            <Typography variant="small" color="gray" className="font-medium">
              Work Details
            </Typography>
          </Card>
        )}
        {hasContactData && (
          <Card className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 border-l-4 border-green-500">
            <Typography variant="h4" color="green" className="font-bold">
              {contactFields.filter(field => field.value !== 'Not set').length}
            </Typography>
            <Typography variant="small" color="gray" className="font-medium">
              Contact Info
            </Typography>
          </Card>
        )}
        {hasPersonalData && (
          <Card className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-l-4 border-purple-500">
            <Typography variant="h4" color="purple" className="font-bold">
              {personalFields.filter(field => field.value !== 'Not set').length}
            </Typography>
            <Typography variant="small" color="gray" className="font-medium">
              Personal Info
            </Typography>
          </Card>
        )}
        <Card className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-l-4 border-orange-500">
          <Typography variant="h4" color="orange" className="font-bold">
            {profile.profile_picture_url ? '1' : '0'}
          </Typography>
          <Typography variant="small" color="gray" className="font-medium">
            Profile Picture
          </Typography>
        </Card>
      </div>

      {/* Key Information Sections - Only show sections with data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {hasWorkData && (
          <div>
            <Typography variant="h5" color="blue-gray" className="mb-4 flex items-center gap-3 font-bold text-left">
              <BriefcaseIcon className="h-5 w-5 text-blue-600 flex-shrink-0" />
              <span>Work Information</span>
            </Typography>
            <div className="space-y-3">
              {workFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
            </div>
          </div>
        )}
        {hasContactData && (
          <div>
            <Typography variant="h5" color="blue-gray" className="mb-4 flex items-center gap-3 font-bold text-left">
              <PhoneIcon className="h-5 w-5 text-green-600 flex-shrink-0" />
              <span>Contact Information</span>
            </Typography>
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
              <Typography variant="h5" color="blue-gray" className="mb-4 flex items-center gap-3 font-bold text-left">
                <UserIcon className="h-5 w-5 text-purple-600 flex-shrink-0" />
                <span>Personal Information</span>
              </Typography>
              <div className="space-y-3">
                {personalFields.filter(field => field.value !== 'Not set').map(renderField)}
              </div>
            </div>
          )}
          {contactFields.filter(field => field.value !== 'Not set').slice(2).length > 0 && (
            <div>
              <Typography variant="h5" color="blue-gray" className="mb-4 flex items-center gap-3 font-bold text-left">
                <MapPinIcon className="h-5 w-5 text-orange-600 flex-shrink-0" />
                <span>Location & Emergency</span>
              </Typography>
              <div className="space-y-3">
                {contactFields.filter(field => field.value !== 'Not set').slice(2).map(renderField)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Show message if no data */}
      {!hasWorkData && !hasContactData && !hasPersonalData && (
        <Card className="p-8 text-center bg-gray-50">
          <Typography variant="h6" color="gray" className="mb-2">
            No profile information available
          </Typography>
          <Typography variant="small" color="gray">
            Click "Edit Profile" to add your information
          </Typography>
        </Card>
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
