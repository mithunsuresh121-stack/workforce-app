import React, { useState } from 'react';
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
  HomeIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const ProfileDetails = ({ profile, view = 'overview' }) => {
  const [expandedCards, setExpandedCards] = useState({
    overview: true,
    personal: false,
    contact: false,
    work: false
  });

  if (!profile) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-neutral-200 rounded mx-auto mb-4"></div>
            <div className="h-4 w-64 bg-neutral-200 rounded mx-auto mb-2"></div>
            <div className="h-4 w-56 bg-neutral-200 rounded mx-auto"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-surface border border-border rounded-linear shadow-linear p-4">
              <div className="animate-pulse">
                <div className="h-6 w-32 bg-neutral-200 rounded mb-2"></div>
                <div className="h-4 w-24 bg-neutral-200 rounded"></div>
              </div>
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
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  };

  const toggleCard = (cardType) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardType]: !prev[cardType]
    }));
  };

  // Personal Information Fields
  const personalFields = [
    {
      icon: UserIcon,
      label: 'Gender',
      value: profile.gender || 'Not set',
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Date of Birth',
      value: profile.date_of_birth ? formatDate(profile.date_of_birth) : 'Not set',
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200'
    }
  ];

  // Contact Information Fields
  const contactFields = [
    {
      icon: PhoneIcon,
      label: 'Phone',
      value: formatPhone(profile.phone),
      color: 'success',
      bgColor: 'bg-success-50',
      iconColor: 'text-success-600',
      borderColor: 'border-success-200'
    },
    {
      icon: MapPinIcon,
      label: 'Address',
      value: profile.address || 'Not set',
      color: 'warning',
      bgColor: 'bg-warning-50',
      iconColor: 'text-warning-600',
      borderColor: 'border-warning-200'
    },
    {
      icon: HomeIcon,
      label: 'City',
      value: profile.city || 'Not set',
      color: 'accent',
      bgColor: 'bg-accent-50',
      iconColor: 'text-accent-600',
      borderColor: 'border-accent-200'
    },
    {
      icon: HeartIcon,
      label: 'Emergency Contact',
      value: profile.emergency_contact || 'Not set',
      color: 'danger',
      bgColor: 'bg-danger-50',
      iconColor: 'text-danger-600',
      borderColor: 'border-danger-200'
    }
  ];

  // Work Information Fields
  const workFields = [
    {
      icon: BuildingOfficeIcon,
      label: 'Department',
      value: profile.department || 'Not set',
      color: 'accent',
      bgColor: 'bg-accent-50',
      iconColor: 'text-accent-600',
      borderColor: 'border-accent-200'
    },
    {
      icon: BriefcaseIcon,
      label: 'Position',
      value: profile.position || 'Not set',
      color: 'success',
      bgColor: 'bg-success-50',
      iconColor: 'text-success-600',
      borderColor: 'border-success-200'
    },
    {
      icon: CalendarDaysIcon,
      label: 'Hire Date',
      value: formatDate(profile.hire_date),
      color: 'primary',
      bgColor: 'bg-primary-50',
      iconColor: 'text-primary-600',
      borderColor: 'border-primary-200'
    },
    {
      icon: StarIcon,
      label: 'Employee ID',
      value: profile.employee_id || 'Not set',
      color: 'warning',
      bgColor: 'bg-warning-50',
      iconColor: 'text-warning-600',
      borderColor: 'border-warning-200'
    }
  ];

  const renderField = (field) => {
    const Icon = field.icon;
    const isSet = field.value !== 'Not set';

    return (
      <div key={field.label} className={`bg-surface border border-border rounded-linear shadow-linear p-4 transition-all duration-300 hover:shadow-linear-lg hover:border-neutral-300`}>
        <div className="flex items-start gap-4">
          <div className={`p-2.5 rounded-full ${field.bgColor} flex-shrink-0 self-start mt-1`}>
            <Icon className={`h-5 w-5 ${field.iconColor}`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-neutral-700">
                {field.label}
              </h4>
              <div className="flex-shrink-0">
                {isSet ? (
                  <CheckCircleIcon className="h-4 w-4 text-success-600" />
                ) : (
                  <ExclamationTriangleIcon className="h-4 w-4 text-warning-600" />
                )}
              </div>
            </div>
            <p className="text-neutral-900 break-words leading-relaxed mb-1 font-medium">
              {field.value}
            </p>
            {!isSet && (
              <p className="text-neutral-500 italic text-xs">
                Click "Edit Profile" to add this information
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  const hasWorkData = workFields.some(field => field.value !== 'Not set');
  const hasContactData = contactFields.some(field => field.value !== 'Not set');
  const hasPersonalData = personalFields.some(field => field.value !== 'Not set');

  const renderOverviewCard = () => {
    const totalFields = workFields.length + contactFields.length + personalFields.length;
    const filledFields = [
      ...workFields,
      ...contactFields,
      ...personalFields
    ].filter(field => field.value !== 'Not set').length;
    const completionPercentage = Math.round((filledFields / totalFields) * 100);

    return (
      <div className="bg-surface border border-border rounded-linear shadow-linear overflow-hidden">
        <div
          className="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
          onClick={() => toggleCard('overview')}
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-accent-100 rounded-lg">
              <UserIcon className="h-5 w-5 text-accent-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-neutral-900">Overview</h3>
              <p className="text-neutral-600 text-sm">Profile summary and quick stats</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm font-medium text-neutral-600">Completion</div>
              <div className="text-lg font-bold text-accent-600">{completionPercentage}%</div>
            </div>
            {expandedCards.overview ? (
              <ChevronDownIcon className="h-5 w-5 text-neutral-500" />
            ) : (
              <ChevronRightIcon className="h-5 w-5 text-neutral-500" />
            )}
          </div>
        </div>

        {expandedCards.overview && (
          <div className="px-6 pb-6 border-t border-border">
            <div className="pt-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {hasWorkData && (
                  <div className="text-center p-4 bg-accent-50 rounded-linear border border-accent-200">
                    <div className="text-2xl font-bold text-accent-600">
                      {workFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div className="text-sm font-medium text-neutral-700">Work Details</div>
                  </div>
                )}
                {hasContactData && (
                  <div className="text-center p-4 bg-success-50 rounded-linear border border-success-200">
                    <div className="text-2xl font-bold text-success-600">
                      {contactFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div className="text-sm font-medium text-neutral-700">Contact Info</div>
                  </div>
                )}
                {hasPersonalData && (
                  <div className="text-center p-4 bg-purple-50 rounded-linear border border-purple-200">
                    <div className="text-2xl font-bold text-purple-600">
                      {personalFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div className="text-sm font-medium text-neutral-700">Personal Info</div>
                  </div>
                )}
                <div className="text-center p-4 bg-warning-50 rounded-linear border border-warning-200">
                  <div className="text-2xl font-bold text-warning-600">
                    {profile.profile_picture_url ? '1' : '0'}
                  </div>
                  <div className="text-sm font-medium text-neutral-700">Profile Picture</div>
                </div>
              </div>

              {/* Key Information Sections */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {hasWorkData && (
                  <div>
                    <h4 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                      <BriefcaseIcon className="h-5 w-5 text-accent-600" />
                      Work Information
                    </h4>
                    <div className="space-y-3">
                      {workFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
                    </div>
                  </div>
                )}
                {hasContactData && (
                  <div>
                    <h4 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                      <PhoneIcon className="h-5 w-5 text-success-600" />
                      Contact Information
                    </h4>
                    <div className="space-y-3">
                      {contactFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPersonalCard = () => (
    <div className="bg-surface border border-border rounded-linear shadow-linear overflow-hidden">
      <div
        className="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
        onClick={() => toggleCard('personal')}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <UserIcon className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">Personal Information</h3>
            <p className="text-neutral-600 text-sm">Personal details and demographics</p>
          </div>
        </div>
        {expandedCards.personal ? (
          <ChevronDownIcon className="h-5 w-5 text-neutral-500" />
        ) : (
          <ChevronRightIcon className="h-5 w-5 text-neutral-500" />
        )}
      </div>

      {expandedCards.personal && (
        <div className="px-6 pb-6 border-t border-border">
          <div className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {personalFields.map(renderField)}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderContactCard = () => (
    <div className="bg-surface border border-border rounded-linear shadow-linear overflow-hidden">
      <div
        className="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
        onClick={() => toggleCard('contact')}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-success-100 rounded-lg">
            <PhoneIcon className="h-5 w-5 text-success-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">Contact Details</h3>
            <p className="text-neutral-600 text-sm">Phone, address, and emergency contact</p>
          </div>
        </div>
        {expandedCards.contact ? (
          <ChevronDownIcon className="h-5 w-5 text-neutral-500" />
        ) : (
          <ChevronRightIcon className="h-5 w-5 text-neutral-500" />
        )}
      </div>

      {expandedCards.contact && (
        <div className="px-6 pb-6 border-t border-border">
          <div className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contactFields.map(renderField)}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderWorkCard = () => (
    <div className="bg-surface border border-border rounded-linear shadow-linear overflow-hidden">
      <div
        className="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
        onClick={() => toggleCard('work')}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent-100 rounded-lg">
            <BriefcaseIcon className="h-5 w-5 text-accent-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-neutral-900">Work Information</h3>
            <p className="text-neutral-600 text-sm">Department, position, and employment details</p>
          </div>
        </div>
        {expandedCards.work ? (
          <ChevronDownIcon className="h-5 w-5 text-neutral-500" />
        ) : (
          <ChevronRightIcon className="h-5 w-5 text-neutral-500" />
        )}
      </div>

      {expandedCards.work && (
        <div className="px-6 pb-6 border-t border-border">
          <div className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workFields.map(renderField)}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'personal':
        return (
          <div className="space-y-6">
            {renderPersonalCard()}
          </div>
        );
      case 'contact':
        return (
          <div className="space-y-6">
            {renderContactCard()}
          </div>
        );
      case 'work':
        return (
          <div className="space-y-6">
            {renderWorkCard()}
          </div>
        );
      default:
        return (
          <div className="space-y-6">
            {renderOverviewCard()}
            {renderPersonalCard()}
            {renderContactCard()}
            {renderWorkCard()}
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {renderContent()}
    </div>
  );
};

export default ProfileDetails;
