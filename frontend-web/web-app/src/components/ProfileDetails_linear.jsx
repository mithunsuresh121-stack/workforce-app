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
  ChevronRightIcon
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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ textAlign: 'center', padding: '2rem 0' }}>
          <div style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}>
            <div style={{
              height: '2rem',
              width: '12rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '0.25rem',
              margin: '0 auto 1rem'
            }}></div>
            <div style={{
              height: '1rem',
              width: '16rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '0.25rem',
              margin: '0 auto 0.5rem'
            }}></div>
            <div style={{
              height: '1rem',
              width: '14rem',
              backgroundColor: '#e5e7eb',
              borderRadius: '0.25rem',
              margin: '0 auto'
            }}></div>
          </div>
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1rem'
        }}>
          {[...Array(4)].map((_, i) => (
            <div key={i} style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              boxShadow: 'var(--shadow)',
              padding: '1rem'
            }}>
              <div style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}>
                <div style={{
                  height: '1.5rem',
                  width: '8rem',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '0.25rem',
                  marginBottom: '0.5rem'
                }}></div>
                <div style={{
                  height: '1rem',
                  width: '6rem',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '0.25rem'
                }}></div>
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
      <div key={field.label} style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '0.75rem',
        boxShadow: 'var(--shadow)',
        padding: '1rem',
        transition: 'all 0.3s',
        cursor: 'pointer'
      }} className="hover:shadow-lg">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div style={{
            padding: '0.625rem',
            borderRadius: '50%',
            backgroundColor: field.bgColor,
            flexShrink: 0,
            alignSelf: 'flex-start',
            marginTop: '0.25rem'
          }}>
            <Icon style={{ width: '1.25rem', height: '1.25rem', color: field.iconColor }} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-secondary)' }}>
                {field.label}
              </h4>
              <div style={{ flexShrink: 0 }}>
                {isSet ? (
                  <CheckCircleIcon style={{ width: '1rem', height: '1rem', color: '#15803d' }} />
                ) : (
                  <ExclamationTriangleIcon style={{ width: '1rem', height: '1rem', color: '#d97706' }} />
                )}
              </div>
            </div>
            <p style={{
              color: 'var(--text-primary)',
              wordBreak: 'break-word',
              lineHeight: '1.625',
              marginBottom: '0.25rem',
              fontWeight: '500'
            }}>
              {field.value}
            </p>
            {!isSet && (
              <p style={{
                color: 'var(--text-secondary)',
                fontStyle: 'italic',
                fontSize: '0.75rem'
              }}>
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
      <div style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '0.75rem',
        boxShadow: 'var(--shadow)',
        overflow: 'hidden'
      }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '1.5rem',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          onClick={() => toggleCard('overview')}
          className="hover:bg-gray-50"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              padding: '0.5rem',
              backgroundColor: '#fef3c7',
              borderRadius: '0.5rem'
            }}>
              <UserIcon style={{ width: '1.25rem', height: '1.25rem', color: '#d97706' }} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--text-primary)' }}>Overview</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Profile summary and quick stats</p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.875rem', fontWeight: '500', color: 'var(--text-secondary)' }}>Completion</div>
              <div style={{ fontSize: '1.125rem', fontWeight: '700', color: 'var(--accent)' }}>{completionPercentage}%</div>
            </div>
            {expandedCards.overview ? (
              <ChevronDownIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
            ) : (
              <ChevronRightIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
            )}
          </div>
        </div>

        {expandedCards.overview && (
          <div style={{
            padding: '0 1.5rem 1.5rem',
            borderTop: '1px solid var(--border)'
          }}>
            <div style={{ paddingTop: '1.5rem' }}>
              {/* Quick Stats */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '1rem',
                marginBottom: '2rem'
              }}>
                {hasWorkData && (
                  <div style={{
                    textAlign: 'center',
                    padding: '1rem',
                    backgroundColor: '#fef3c7',
                    borderRadius: '0.75rem',
                    border: '1px solid #fde68a'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#d97706'
                    }}>
                      {workFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: 'var(--text-secondary)'
                    }}>Work Details</div>
                  </div>
                )}
                {hasContactData && (
                  <div style={{
                    textAlign: 'center',
                    padding: '1rem',
                    backgroundColor: '#dcfce7',
                    borderRadius: '0.75rem',
                    border: '1px solid #bbf7d0'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#15803d'
                    }}>
                      {contactFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: 'var(--text-secondary)'
                    }}>Contact Info</div>
                  </div>
                )}
                {hasPersonalData && (
                  <div style={{
                    textAlign: 'center',
                    padding: '1rem',
                    backgroundColor: '#f3e8ff',
                    borderRadius: '0.75rem',
                    border: '1px solid #e9d5ff'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#7c3aed'
                    }}>
                      {personalFields.filter(field => field.value !== 'Not set').length}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: 'var(--text-secondary)'
                    }}>Personal Info</div>
                  </div>
                )}
                <div style={{
                  textAlign: 'center',
                  padding: '1rem',
                  backgroundColor: '#fef3c7',
                  borderRadius: '0.75rem',
                  border: '1px solid #fde68a'
                }}>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: '#d97706'
                  }}>
                    {profile.profile_picture_url ? '1' : '0'}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: 'var(--text-secondary)'
                  }}>Profile Picture</div>
                </div>
              </div>

              {/* Key Information Sections */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr',
                gap: '2rem'
              }} className="lg:grid-cols-2">
                {hasWorkData && (
                  <div>
                    <h4 style={{
                      fontSize: '1.125rem',
                      fontWeight: '600',
                      color: 'var(--text-primary)',
                      marginBottom: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <BriefcaseIcon style={{ width: '1.25rem', height: '1.25rem', color: '#d97706' }} />
                      Work Information
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {workFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
                    </div>
                  </div>
                )}
                {hasContactData && (
                  <div>
                    <h4 style={{
                      fontSize: '1.125rem',
                      fontWeight: '600',
                      color: 'var(--text-primary)',
                      marginBottom: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <PhoneIcon style={{ width: '1.25rem', height: '1.25rem', color: '#15803d' }} />
                      Contact Information
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
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
    <div style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '0.75rem',
      boxShadow: 'var(--shadow)',
      overflow: 'hidden'
    }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.5rem',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
        onClick={() => toggleCard('personal')}
        className="hover:bg-gray-50"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            padding: '0.5rem',
            backgroundColor: '#f3e8ff',
            borderRadius: '0.5rem'
          }}>
            <UserIcon style={{ width: '1.25rem', height: '1.25rem', color: '#7c3aed' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--text-primary)' }}>Personal Information</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Personal details and demographics</p>
          </div>
        </div>
        {expandedCards.personal ? (
          <ChevronDownIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        ) : (
          <ChevronRightIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        )}
      </div>

      {expandedCards.personal && (
        <div style={{
          padding: '0 1.5rem 1.5rem',
          borderTop: '1px solid var(--border)'
        }}>
          <div style={{ paddingTop: '1.5rem' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
              {personalFields.map(renderField)}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderContactCard = () => (
    <div style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '0.75rem',
      boxShadow: 'var(--shadow)',
      overflow: 'hidden'
    }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.5rem',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
        onClick={() => toggleCard('contact')}
        className="hover:bg-gray-50"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            padding: '0.5rem',
            backgroundColor: '#dcfce7',
            borderRadius: '0.5rem'
          }}>
            <PhoneIcon style={{ width: '1.25rem', height: '1.25rem', color: '#15803d' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--text-primary)' }}>Contact Details</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Phone, address, and emergency contact</p>
          </div>
        </div>
        {expandedCards.contact ? (
          <ChevronDownIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        ) : (
          <ChevronRightIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        )}
      </div>

      {expandedCards.contact && (
        <div style={{
          padding: '0 1.5rem 1.5rem',
          borderTop: '1px solid var(--border)'
        }}>
          <div style={{ paddingTop: '1.5rem' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
              {contactFields.map(renderField)}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderWorkCard = () => (
    <div style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '0.75rem',
      boxShadow: 'var(--shadow)',
      overflow: 'hidden'
    }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.5rem',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
        onClick={() => toggleCard('work')}
        className="hover:bg-gray-50"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            padding: '0.5rem',
            backgroundColor: '#fef3c7',
            borderRadius: '0.5rem'
          }}>
            <BriefcaseIcon style={{ width: '1.25rem', height: '1.25rem', color: '#d97706' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--text-primary)' }}>Work Information</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Department, position, and employment details</p>
          </div>
        </div>
        {expandedCards.work ? (
          <ChevronDownIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        ) : (
          <ChevronRightIcon style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
        )}
      </div>

      {expandedCards.work && (
        <div style={{
          padding: '0 1.5rem 1.5rem',
          borderTop: '1px solid var(--border)'
        }}>
          <div style={{ paddingTop: '1.5rem' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {renderPersonalCard()}
          </div>
        );
      case 'contact':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {renderContactCard()}
          </div>
        );
      case 'work':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {renderWorkCard()}
          </div>
        );
      default:
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {renderOverviewCard()}
            {renderPersonalCard()}
            {renderContactCard()}
            {renderWorkCard()}
          </div>
        );
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {renderContent()}
    </div>
  );
};

export default ProfileDetails;
