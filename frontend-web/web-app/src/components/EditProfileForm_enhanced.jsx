import React, { useState } from 'react';
import {
  Typography,
  Button,
  Input,
  Textarea,
  Select,
  Option,
  Card,
  CardBody,
  CardHeader,
  Progress,
  Alert
} from '@material-tailwind/react';
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
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useAuth, api } from '../contexts/AuthContext';

const EditProfileForm = ({ profile, onClose, onSuccess }) => {
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

  const totalSteps = 3;

  const steps = [
    {
      number: 1,
      title: 'Personal Information',
      description: 'Basic personal details',
      icon: UserIcon,
      fields: ['full_name', 'gender', 'date_of_birth']
    },
    {
      number: 2,
      title: 'Contact & Location',
      description: 'Contact information and address',
      icon: PhoneIcon,
      fields: ['phone', 'address', 'city', 'emergency_contact']
    },
    {
      number: 3,
      title: 'Work Information',
      description: 'Employment details',
      icon: BuildingOfficeIcon,
      fields: ['department', 'position', 'employee_id', 'hire_date']
    }
  ];

  const validateStep = (stepNumber) => {
    const newErrors = {};
    const currentStepData = steps.find(step => step.number === stepNumber);

    if (!currentStepData) return true;

    currentStepData.fields.forEach(field => {
      if (!formData[field] && field !== 'profile_picture_url') {
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
      // Submit profile update request
      await api.put('/profile/update-request', formData);

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
            <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
              step.number === currentStep
                ? 'bg-blue-600 border-blue-600 text-white'
                : step.number < currentStep
                ? 'bg-green-600 border-green-600 text-white'
                : 'bg-gray-200 border-gray-300 text-gray-500'
            }`}>
              {step.number < currentStep ? (
                <CheckCircleIcon className="h-6 w-6" />
              ) : (
                <step.icon className="h-6 w-6" />
              )}
            </div>
            <div className="text-center mt-2">
              <Typography variant="small" className={`font-medium ${
                step.number <= currentStep ? 'text-blue-600' : 'text-gray-500'
              }`}>
                {step.title}
              </Typography>
              <Typography variant="small" color="gray" className="hidden sm:block">
                {step.description}
              </Typography>
            </div>
          </div>
        ))}
      </div>
      <Progress
        value={(currentStep / totalSteps) * 100}
        color="blue"
        className="h-2"
      />
    </div>
  );

  const renderPersonalInfoStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <Input
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => handleInputChange('full_name', e.target.value)}
            error={!!errors.full_name}
            icon={<UserIcon className="h-5 w-5" />}
          />
          {errors.full_name && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.full_name}
            </Typography>
          )}
        </div>

        <div>
          <Select
            label="Gender"
            value={formData.gender}
            onChange={(value) => handleInputChange('gender', value)}
            error={!!errors.gender}
          >
            <Option value="male">Male</Option>
            <Option value="female">Female</Option>
            <Option value="other">Other</Option>
            <Option value="prefer_not_to_say">Prefer not to say</Option>
          </Select>
          {errors.gender && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.gender}
            </Typography>
          )}
        </div>
      </div>

      <div>
        <Input
          type="date"
          label="Date of Birth"
          value={formData.date_of_birth}
          onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
          error={!!errors.date_of_birth}
          icon={<CalendarDaysIcon className="h-5 w-5" />}
        />
        {errors.date_of_birth && (
          <Typography variant="small" color="red" className="mt-1">
            {errors.date_of_birth}
          </Typography>
        )}
      </div>
    </div>
  );

  const renderContactStep = () => (
    <div className="space-y-6">
      <div>
        <Input
          label="Phone Number"
          value={formData.phone}
          onChange={(e) => handleInputChange('phone', e.target.value)}
          error={!!errors.phone}
          icon={<PhoneIcon className="h-5 w-5" />}
          placeholder="(555) 123-4567"
        />
        {errors.phone && (
          <Typography variant="small" color="red" className="mt-1">
            {errors.phone}
          </Typography>
        )}
      </div>

      <div>
        <Textarea
          label="Address"
          value={formData.address}
          onChange={(e) => handleInputChange('address', e.target.value)}
          error={!!errors.address}
          icon={<MapPinIcon className="h-5 w-5" />}
        />
        {errors.address && (
          <Typography variant="small" color="red" className="mt-1">
            {errors.address}
          </Typography>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <Input
            label="City"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            error={!!errors.city}
            icon={<MapPinIcon className="h-5 w-5" />}
          />
          {errors.city && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.city}
            </Typography>
          )}
        </div>

        <div>
          <Input
            label="Emergency Contact"
            value={formData.emergency_contact}
            onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
            error={!!errors.emergency_contact}
            icon={<PhoneIcon className="h-5 w-5" />}
            placeholder="Name & Phone Number"
          />
          {errors.emergency_contact && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.emergency_contact}
            </Typography>
          )}
        </div>
      </div>
    </div>
  );

  const renderWorkStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <Input
            label="Department"
            value={formData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            error={!!errors.department}
            icon={<BuildingOfficeIcon className="h-5 w-5" />}
          />
          {errors.department && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.department}
            </Typography>
          )}
        </div>

        <div>
          <Input
            label="Position"
            value={formData.position}
            onChange={(e) => handleInputChange('position', e.target.value)}
            error={!!errors.position}
            icon={<UserIcon className="h-5 w-5" />}
          />
          {errors.position && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.position}
            </Typography>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <Input
            label="Employee ID"
            value={formData.employee_id}
            onChange={(e) => handleInputChange('employee_id', e.target.value)}
            error={!!errors.employee_id}
            icon={<UserIcon className="h-5 w-5" />}
          />
          {errors.employee_id && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.employee_id}
            </Typography>
          )}
        </div>

        <div>
          <Input
            type="date"
            label="Hire Date"
            value={formData.hire_date}
            onChange={(e) => handleInputChange('hire_date', e.target.value)}
            error={!!errors.hire_date}
            icon={<CalendarDaysIcon className="h-5 w-5" />}
          />
          {errors.hire_date && (
            <Typography variant="small" color="red" className="mt-1">
              {errors.hire_date}
            </Typography>
          )}
        </div>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderPersonalInfoStep();
      case 2:
        return renderContactStep();
      case 3:
        return renderWorkStep();
      default:
        return null;
    }
  };

  if (showSuccess) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6">
          <CheckCircleIcon className="h-12 w-12 text-green-600" />
        </div>
        <Typography variant="h4" color="green" className="mb-4">
          Profile Update Submitted!
        </Typography>
        <Typography variant="lead" color="gray" className="mb-6">
          Your profile update request has been submitted successfully. An administrator will review your changes shortly.
        </Typography>
        <Alert color="green" className="mb-6">
          <InformationCircleIcon className="h-5 w-5" />
          You will receive a notification once your changes are approved.
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {renderStepIndicator()}

      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-full">
              {React.createElement(steps[currentStep - 1].icon, { className: "h-8 w-8" })}
            </div>
            <div>
              <Typography variant="h5" className="text-white font-bold">
                Step {currentStep}: {steps[currentStep - 1].title}
              </Typography>
              <Typography variant="small" className="text-blue-100">
                {steps[currentStep - 1].description}
              </Typography>
            </div>
          </div>
        </CardHeader>

        <CardBody className="p-6">
          {errors.submit && (
            <Alert color="red" className="mb-6">
              <ExclamationTriangleIcon className="h-5 w-5" />
              {errors.submit}
            </Alert>
          )}

          {renderCurrentStep()}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <div>
              {currentStep > 1 && (
                <Button
                  variant="outlined"
                  onClick={handlePrevious}
                  className="flex items-center gap-2"
                >
                  <ArrowLeftIcon className="h-4 w-4" />
                  Previous
                </Button>
              )}
            </div>

            <div className="flex gap-3">
              <Button variant="text" color="gray" onClick={onClose}>
                Cancel
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  onClick={handleNext}
                  className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600"
                >
                  Next
                  <ArrowRightIcon className="h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  loading={loading}
                  className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600"
                >
                  <CheckCircleIcon className="h-4 w-4" />
                  Submit Request
                </Button>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Help Text */}
      <div className="mt-4 text-center">
        <Typography variant="small" color="gray">
          <InformationCircleIcon className="h-4 w-4 inline mr-1" />
          All changes require administrator approval before taking effect
        </Typography>
      </div>
    </div>
  );
};

export default EditProfileForm;
