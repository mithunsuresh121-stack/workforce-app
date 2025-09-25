import React, { useState, useRef } from 'react';
import { useAuth, api } from '../contexts/AuthContext';
import {
  UserIcon,
  PhoneIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  CalendarDaysIcon,
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
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {steps.map((step) => (
          <div key={step.number} className="flex flex-col items-center">
            <div className={`w-12 h-12 rounded-linear flex items-center justify-center border-2 transition-all duration-300 ${
              step.number === currentStep
                ? 'bg-accent-500 border-accent-500 text-white'
                : step.number < currentStep
                ? 'bg-success-500 border-success-500 text-white'
                : 'bg-neutral-200 border-neutral-300 text-neutral-500'
            }`}>
              {step.number < currentStep ? (
                <CheckCircleIcon className="h-6 w-6" />
              ) : (
                <step.icon className="h-6 w-6" />
              )}
            </div>
            <div className="text-center mt-2">
              <p className={`font-medium text-sm ${
                step.number <= currentStep ? 'text-accent-600' : 'text-neutral-500'
              }`}>
                {step.title}
              </p>
              <p className="text-xs text-neutral-500 hidden sm:block">
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
      <div className="w-full bg-neutral-200 rounded-linear h-2">
        <div
          className="bg-accent-500 h-2 rounded-linear transition-all duration-300"
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>
    </div>
  );

  const renderProfilePictureStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="mb-6">
          <div className="relative inline-block">
            <div className="w-32 h-32 rounded-linear border-4 border-neutral-200 bg-neutral-100 mx-auto overflow-hidden">
              {profilePicturePreview ? (
                <img
                  src={profilePicturePreview}
                  alt="Profile preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <CameraIcon className="h-12 w-12 text-neutral-400" />
                </div>
              )}
            </div>
            {profilePicturePreview && (
              <button
                onClick={removeProfilePicture}
                className="absolute -top-2 -right-2 w-8 h-8 bg-danger-500 hover:bg-danger-600 text-white rounded-full flex items-center justify-center transition-colors duration-200"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="mt-4 bg-accent-500 hover:bg-accent-600 text-white font-medium py-2 px-4 rounded-linear transition-colors duration-200"
          >
            {profilePicturePreview ? 'Change Picture' : 'Upload Picture'}
          </button>
        </div>
        {errors.profile_picture && (
          <p className="text-danger-600 text-sm font-medium">{errors.profile_picture}</p>
        )}
        <p className="text-neutral-600 text-sm">
          Upload a professional headshot. Max file size: 5MB
        </p>
      </div>
    </div>
  );

  const renderPersonalInfoStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Full Name
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => handleInputChange('full_name', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Enter your full name"
          />
          {errors.full_name && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.full_name}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Gender
          </label>
          <select
            value={formData.gender}
            onChange={(e) => handleInputChange('gender', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
          >
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
          {errors.gender && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.gender}</p>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Date of Birth
        </label>
        <input
          type="date"
          value={formData.date_of_birth}
          onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
          className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
        />
        {errors.date_of_birth && (
          <p className="text-danger-600 text-sm font-medium mt-1">{errors.date_of_birth}</p>
        )}
      </div>
    </div>
  );

  const renderContactStep = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Phone Number
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => handleInputChange('phone', e.target.value)}
          className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
          placeholder="(555) 123-4567"
        />
        {errors.phone && (
          <p className="text-danger-600 text-sm font-medium mt-1">{errors.phone}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Address
        </label>
        <textarea
          value={formData.address}
          onChange={(e) => handleInputChange('address', e.target.value)}
          rows={3}
          className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
          placeholder="Enter your full address"
        />
        {errors.address && (
          <p className="text-danger-600 text-sm font-medium mt-1">{errors.address}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            City
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Enter your city"
          />
          {errors.city && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.city}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Emergency Contact
          </label>
          <input
            type="text"
            value={formData.emergency_contact}
            onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Name & Phone Number"
          />
          {errors.emergency_contact && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.emergency_contact}</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderWorkStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Department
          </label>
          <input
            type="text"
            value={formData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Enter your department"
          />
          {errors.department && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.department}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Position
          </label>
          <input
            type="text"
            value={formData.position}
            onChange={(e) => handleInputChange('position', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Enter your position"
          />
          {errors.position && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.position}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Employee ID
          </label>
          <input
            type="text"
            value={formData.employee_id}
            onChange={(e) => handleInputChange('employee_id', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
            placeholder="Enter your employee ID"
          />
          {errors.employee_id && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.employee_id}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Hire Date
          </label>
          <input
            type="date"
            value={formData.hire_date}
            onChange={(e) => handleInputChange('hire_date', e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-linear bg-surface text-neutral-900 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 transition-colors duration-200"
          />
          {errors.hire_date && (
            <p className="text-danger-600 text-sm font-medium mt-1">{errors.hire_date}</p>
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
      <div className="text-center py-12">
        <div className="mx-auto w-24 h-24 bg-success-100 rounded-linear flex items-center justify-center mb-6">
          <CheckCircleIcon className="h-12 w-12 text-success-600" />
        </div>
        <h3 className="text-xl font-semibold text-neutral-900 mb-4">
          Profile Update Submitted!
        </h3>
        <p className="text-neutral-600 mb-6">
          Your profile update request has been submitted successfully. An administrator will review your changes shortly.
        </p>
        <div className="bg-success-50 border border-success-200 rounded-linear p-4 mb-6">
          <div className="flex items-center justify-center">
            <InformationCircleIcon className="h-5 w-5 text-success-600 mr-2" />
            <p className="text-success-700 font-medium">
              You will receive a notification once your changes are approved.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {renderStepIndicator()}

      <div className="bg-surface rounded-linear border border-border shadow-linear">
        <div className="bg-accent-500 text-white p-6 rounded-t-linear">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-linear">
              {React.createElement(steps[currentStep - 1].icon, { className: "h-8 w-8" })}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">
                Step {currentStep}: {steps[currentStep - 1].title}
              </h2>
              <p className="text-accent-100">
                {steps[currentStep - 1].description}
              </p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {errors.submit && (
            <div className="mb-6 bg-danger-50 border border-danger-200 rounded-linear p-4">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 text-danger-600 mr-2" />
                <p className="text-danger-700 font-medium">{errors.submit}</p>
              </div>
            </div>
          )}

          {renderCurrentStep()}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-border">
            <div>
              {currentStep > 1 && (
                <button
                  onClick={handlePrevious}
                  className="flex items-center gap-2 px-4 py-2 border border-border rounded-linear text-neutral-700 hover:bg-neutral-50 transition-colors duration-200"
                >
                  <ArrowLeftIcon className="h-4 w-4" />
                  Previous
                </button>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-neutral-600 hover:text-neutral-800 transition-colors duration-200"
              >
                Cancel
              </button>

              {currentStep < totalSteps ? (
                <button
                  onClick={handleNext}
                  className="flex items-center gap-2 bg-accent-500 hover:bg-accent-600 text-white font-medium py-2 px-4 rounded-linear transition-colors duration-200"
                >
                  Next
                  <ArrowRightIcon className="h-4 w-4" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex items-center gap-2 bg-success-500 hover:bg-success-600 disabled:bg-success-300 text-white font-medium py-2 px-4 rounded-linear transition-colors duration-200 disabled:cursor-not-allowed"
                >
                  <CheckCircleIcon className="h-4 w-4" />
                  {loading ? 'Submitting...' : 'Submit Request'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center text-neutral-600">
          <InformationCircleIcon className="h-4 w-4 mr-1" />
          <p className="text-sm">
            All changes require administrator approval before taking effect
          </p>
        </div>
      </div>
    </div>
  );
};

export default EditProfileFormLinear;
