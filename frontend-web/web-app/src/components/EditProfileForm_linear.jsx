import React, { useState, useRef } from 'react';
import { useAuth, api } from '../contexts/AuthContext';
import {
  UserIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  InformationCircleIcon,
  CameraIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const EditProfileFormLinear = ({ profile, onClose, onSuccess }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone: profile?.phone || '',
    address: profile?.address || '',
    city: profile?.city || '',
    department: profile?.department || '',
    position: profile?.position || '',
    emergency_contact: profile?.emergency_contact || '',
    employee_id: profile?.employee_id || '',
    hire_date: profile?.hire_date || '',
    profile_picture_url: profile?.profile_picture_url || '',
    gender: profile?.gender || '',
    date_of_birth: profile?.date_of_birth || ''
  });
  const [errors, setErrors] = useState({});
  const [showSuccess, setShowSuccess] = useState(false);
  const [profilePictureFile, setProfilePictureFile] = useState(null);
  const [profilePicturePreview, setProfilePicturePreview] = useState(profile?.profile_picture_url || null);
  const fileInputRef = useRef(null);

  const totalSteps = 4; // Added profile picture step

  const steps = [
    {
      number: 1,
      title: 'Profile Picture',
      description: 'Upload your profile photo',
      icon: CameraIcon,
      fields: ['profile_picture']
    },
    {
      number: 2,
      title: 'Personal Information',
      description: 'Basic personal details',
      icon: UserIcon,
      fields: ['full_name', 'gender', 'date_of_birth']
    },
    {
      number: 3,
      title: 'Contact & Location',
      description: 'Contact information and address',
      icon: PhoneIcon,
      fields: ['phone', 'address', 'city', 'emergency_contact']
    },
    {
      number: 4,
      title: 'Work Information',
      description: 'Employment details',
      icon: BuildingOfficeIcon,
      fields: ['department', 'position', 'employee_id', 'hire_date']
    }
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({ ...prev, profile_picture: 'Please select a valid image file' }));
        return;
      }

      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, profile_picture: 'Image size must be less than 5MB' }));
        return;
      }

      setProfilePictureFile(file);
      setProfilePicturePreview(URL.createObjectURL(file));
      setErrors(prev => ({ ...prev, profile_picture: '' }));
    }
  };

  const removeProfilePicture = () => {
    setProfilePictureFile(null);
    setProfilePicturePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const validateStep = (stepNumber) => {
    const newErrors = {};
    const currentStepData = steps.find(step => step.number === stepNumber);

    if (!currentStepData) return true;

    // Profile picture validation for step 1
    if (stepNumber === 1 && !profilePicturePreview && !profile?.profile_picture_url) {
      newErrors.profile_picture = 'Profile picture is required';
    }

    // Other field validations
    currentStepData.fields.forEach(field => {
      if (field !== 'profile_picture' && !formData[field]) {
        newErrors[field] = `${field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} is required`;
      }
    });

    // Specific validations
    if (formData.phone && !/^\+?[\d\s\-()]{10,}$/.test(formData.phone)) {
      newErrors.phone = 'Please enter a valid phone number';
    }

    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);
    try {
      const submitData = new FormData();

      // Add all form fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          submitData.append(key, formData[key]);
        }
      });

      // Add profile picture if selected
      if (profilePictureFile) {
        submitData.append('profile_picture', profilePictureFile);
      }

      // Submit profile update request
      await api.put('/profile/update-request', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setShowSuccess(true);
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (error) {
      console.error('Error updating profile:', error);
      setErrors({ submit: 'Failed to submit profile update request. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        {steps.map((step) => (
          <div key={step.number} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{
              width: '3rem',
              height: '3rem',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid',
              transition: 'all 0.3s',
              backgroundColor: step.number === currentStep ? 'var(--accent)' : step.number < currentStep ? '#10b981' : '#e5e7eb',
              borderColor: step.number === currentStep ? 'var(--accent)' : step.number < currentStep ? '#10b981' : '#d1d5db',
              color: step.number === currentStep || step.number < currentStep ? 'white' : '#6b7280'
            }}>
              {step.number < currentStep ? (
                <CheckCircleIcon style={{ width: '1.5rem', height: '1.5rem' }} />
              ) : (
                <step.icon style={{ width: '1.5rem', height: '1.5rem' }} />
              )}
            </div>
            <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
              <p style={{
                fontWeight: '500',
                fontSize: '0.875rem',
                color: step.number <= currentStep ? 'var(--accent)' : 'var(--text-secondary)'
              }}>
                {step.title}
              </p>
              <p style={{
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                display: 'none'
              }} className="sm:block">
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
      <div style={{
        width: '100%',
        backgroundColor: '#e5e7eb',
        borderRadius: '0.75rem',
        height: '0.5rem'
      }}>
        <div
          style={{
            backgroundColor: 'var(--accent)',
            height: '0.5rem',
            borderRadius: '0.75rem',
            transition: 'all 0.3s',
            width: `${(currentStep / totalSteps) * 100}%`
          }}
        />
      </div>
    </div>
  );

  const renderProfilePictureStep = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <div style={{
              width: '8rem',
              height: '8rem',
              borderRadius: '0.75rem',
              border: '4px solid #e5e7eb',
              backgroundColor: '#f9fafb',
              margin: '0 auto',
              overflow: 'hidden'
            }}>
              {profilePicturePreview ? (
                <img
                  src={profilePicturePreview}
                  alt="Profile preview"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <div style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <CameraIcon style={{ width: '3rem', height: '3rem', color: '#9ca3af' }} />
                </div>
              )}
            </div>
            {profilePicturePreview && (
              <button
                onClick={removeProfilePicture}
                style={{
                  position: 'absolute',
                  top: '-0.5rem',
                  right: '-0.5rem',
                  width: '2rem',
                  height: '2rem',
                  backgroundColor: '#dc2626',
                  color: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                className="hover:bg-red-600"
              >
                <XMarkIcon style={{ width: '1rem', height: '1rem' }} />
              </button>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            style={{
              marginTop: '1rem',
              backgroundColor: 'var(--accent)',
              color: 'white',
              fontWeight: '500',
              padding: '0.5rem 1rem',
              borderRadius: '0.75rem',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            className="hover:bg-accent-dark"
          >
            {profilePicturePreview ? 'Change Picture' : 'Upload Picture'}
          </button>
        </div>
        {errors.profile_picture && (
          <p style={{
            color: '#dc2626',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}>{errors.profile_picture}</p>
        )}
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '0.875rem'
        }}>
          Upload a professional headshot. Max file size: 5MB
        </p>
      </div>
    </div>
  );

  const renderPersonalInfoStep = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '1.5rem'
      }} className="md:grid-cols-2">
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Full Name
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => handleInputChange('full_name', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Enter your full name"
          />
          {errors.full_name && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.full_name}</p>
          )}
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Gender
          </label>
          <select
            value={formData.gender}
            onChange={(e) => handleInputChange('gender', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
          >
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
          {errors.gender && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.gender}</p>
          )}
        </div>
      </div>

      <div>
        <label style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: '500',
          color: 'var(--text-secondary)',
          marginBottom: '0.5rem'
        }}>
          Date of Birth
        </label>
        <input
          type="date"
          value={formData.date_of_birth}
          onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            border: '1px solid var(--border)',
            borderRadius: '0.75rem',
            backgroundColor: 'var(--surface)',
            color: 'var(--text-primary)',
            transition: 'all 0.2s'
          }}
          className="focus:ring-2 focus:ring-accent focus:border-accent"
        />
        {errors.date_of_birth && (
          <p style={{
            color: '#dc2626',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginTop: '0.25rem'
          }}>{errors.date_of_birth}</p>
        )}
      </div>
    </div>
  );

  const renderContactStep = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <label style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: '500',
          color: 'var(--text-secondary)',
          marginBottom: '0.5rem'
        }}>
          Phone Number
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => handleInputChange('phone', e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            border: '1px solid var(--border)',
            borderRadius: '0.75rem',
            backgroundColor: 'var(--surface)',
            color: 'var(--text-primary)',
            transition: 'all 0.2s'
          }}
          className="focus:ring-2 focus:ring-accent focus:border-accent"
          placeholder="(555) 123-4567"
        />
        {errors.phone && (
          <p style={{
            color: '#dc2626',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginTop: '0.25rem'
          }}>{errors.phone}</p>
        )}
      </div>

      <div>
        <label style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: '500',
          color: 'var(--text-secondary)',
          marginBottom: '0.5rem'
        }}>
          Address
        </label>
        <textarea
          value={formData.address}
          onChange={(e) => handleInputChange('address', e.target.value)}
          rows={3}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            border: '1px solid var(--border)',
            borderRadius: '0.75rem',
            backgroundColor: 'var(--surface)',
            color: 'var(--text-primary)',
            transition: 'all 0.2s'
          }}
          className="focus:ring-2 focus:ring-accent focus:border-accent"
          placeholder="Enter your full address"
        />
        {errors.address && (
          <p style={{
            color: '#dc2626',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginTop: '0.25rem'
          }}>{errors.address}</p>
        )}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '1.5rem'
      }} className="md:grid-cols-2">
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            City
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Enter your city"
          />
          {errors.city && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.city}</p>
          )}
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Emergency Contact
          </label>
          <input
            type="text"
            value={formData.emergency_contact}
            onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Name & Phone Number"
          />
          {errors.emergency_contact && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.emergency_contact}</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderWorkStep = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '1.5rem'
      }} className="md:grid-cols-2">
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Department
          </label>
          <input
            type="text"
            value={formData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Enter your department"
          />
          {errors.department && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.department}</p>
          )}
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Position
          </label>
          <input
            type="text"
            value={formData.position}
            onChange={(e) => handleInputChange('position', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Enter your position"
          />
          {errors.position && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.position}</p>
          )}
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '1.5rem'
      }} className="md:grid-cols-2">
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Employee ID
          </label>
          <input
            type="text"
            value={formData.employee_id}
            onChange={(e) => handleInputChange('employee_id', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
            placeholder="Enter your employee ID"
          />
          {errors.employee_id && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.employee_id}</p>
          )}
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            Hire Date
          </label>
          <input
            type="date"
            value={formData.hire_date}
            onChange={(e) => handleInputChange('hire_date', e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              backgroundColor: 'var(--surface)',
              color: 'var(--text-primary)',
              transition: 'all 0.2s'
            }}
            className="focus:ring-2 focus:ring-accent focus:border-accent"
          />
          {errors.hire_date && (
            <p style={{
              color: '#dc2626',
              fontSize: '0.875rem',
              fontWeight: '500',
              marginTop: '0.25rem'
            }}>{errors.hire_date}</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderProfilePictureStep();
      case 2:
        return renderPersonalInfoStep();
      case 3:
        return renderContactStep();
      case 4:
        return renderWorkStep();
      default:
        return null;
    }
  };

  if (showSuccess) {
    return (
      <div style={{ textAlign: 'center', paddingTop: '3rem', paddingBottom: '3rem' }}>
        <div style={{
          margin: '0 auto',
          width: '6rem',
          height: '6rem',
          backgroundColor: '#dcfce7',
          borderRadius: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.5rem'
        }}>
          <CheckCircleIcon style={{ width: '3rem', height: '3rem', color: '#10b981' }} />
        </div>
        <h3 style={{
          fontSize: '1.25rem',
          fontWeight: '600',
          color: 'var(--text-primary)',
          marginBottom: '1rem'
        }}>
          Profile Update Submitted!
        </h3>
        <p style={{
          color: 'var(--text-secondary)',
          marginBottom: '1.5rem'
        }}>
          Your profile update request has been submitted successfully. An administrator will review your changes shortly.
        </p>
        <div style={{
          backgroundColor: '#dcfce7',
          border: '1px solid #bbf7d0',
          borderRadius: '0.75rem',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <InformationCircleIcon style={{ width: '1.25rem', height: '1.25rem', color: '#10b981', marginRight: '0.5rem' }} />
            <p style={{ color: '#166534', fontWeight: '500' }}>
              You will receive a notification once your changes are approved.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '56rem', margin: '0 auto' }}>
      {renderStepIndicator()}

      <div style={{
        backgroundColor: 'var(--surface)',
        borderRadius: '0.75rem',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow)'
      }}>
        <div style={{
          backgroundColor: 'var(--accent)',
          color: 'white',
          padding: '1.5rem',
          borderRadius: '0.75rem 0.75rem 0 0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              padding: '0.75rem',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '0.75rem'
            }}>
              {React.createElement(steps[currentStep - 1].icon, { style: { width: '2rem', height: '2rem' } })}
            </div>
            <div>
              <h2 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: 'white'
              }}>
                Step {currentStep}: {steps[currentStep - 1].title}
              </h2>
              <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                {steps[currentStep - 1].description}
              </p>
            </div>
          </div>
        </div>

        <div style={{ padding: '1.5rem' }}>
          {errors.submit && (
            <div style={{
              marginBottom: '1.5rem',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '0.75rem',
              padding: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <ExclamationTriangleIcon style={{ width: '1.25rem', height: '1.25rem', color: '#dc2626', marginRight: '0.5rem' }} />
                <p style={{ color: '#991b1b', fontWeight: '500' }}>{errors.submit}</p>
              </div>
            </div>
          )}

          {renderCurrentStep()}

          {/* Navigation Buttons */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '2rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--border)'
          }}>
            <div>
              {currentStep > 1 && (
                <button
                  onClick={handlePrevious}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    border: '1px solid var(--border)',
                    borderRadius: '0.75rem',
                    color: 'var(--text-secondary)',
                    backgroundColor: 'transparent',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  className="hover:bg-gray-50"
                >
                  <ArrowLeftIcon style={{ width: '1rem', height: '1rem' }} />
                  Previous
                </button>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                onClick={onClose}
                style={{
                  padding: '0.5rem 1rem',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                className="hover:text-gray-800"
              >
                Cancel
              </button>

              {currentStep < totalSteps ? (
                <button
                  onClick={handleNext}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    backgroundColor: 'var(--accent)',
                    color: 'white',
                    fontWeight: '500',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  className="hover:bg-accent-dark"
                >
                  Next
                  <ArrowRightIcon style={{ width: '1rem', height: '1rem' }} />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    backgroundColor: '#10b981',
                    color: 'white',
                    fontWeight: '500',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.75rem',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                  className={loading ? 'opacity-50' : 'hover:bg-green-600'}
                >
                  <CheckCircleIcon style={{ width: '1rem', height: '1rem' }} />
                  {loading ? 'Submitting...' : 'Submit Request'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div style={{ marginTop: '1rem', textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
          <InformationCircleIcon style={{ width: '1rem', height: '1rem', marginRight: '0.25rem' }} />
          <p style={{ fontSize: '0.875rem' }}>
            All changes require administrator approval before taking effect
          </p>
        </div>
      </div>
    </div>
  );
};

export default EditProfileFormLinear;
