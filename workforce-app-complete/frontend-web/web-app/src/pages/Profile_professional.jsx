import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody,
  Typography,
  Button,
  Chip,
  Progress,
  IconButton,
  Tooltip,
  Badge,
  Avatar,
  Tabs,
  TabsHeader,
  TabsBody,
  Tab,
  TabPanel,
  Alert,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter
} from '@material-tailwind/react';
import {
  UserIcon,
  PhoneIcon,
  CalendarIcon,
  PencilIcon,
  ShareIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  EnvelopeIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  HeartIcon,
  CameraIcon,
  StarIcon,
  TrophyIcon,
  ChartBarIcon,
  EyeIcon,
  DocumentTextIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import { useAuth, api } from '../contexts/AuthContext';
import EditProfileForm from '../components/EditProfileForm_enhanced';

const ProfileProfessional = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });

  // Calculate profile completion percentage
  const calculateProfileCompletion = (profile) => {
    if (!profile) return 0;
    const fields = ['department', 'position', 'phone', 'hire_date', 'address', 'city', 'emergency_contact', 'employee_id'];
    const filledFields = fields.filter(field => profile[field]).length;
    return Math.round((filledFields / fields.length) * 100);
  };

  const tabs = [
    { label: 'Overview', value: 'overview', icon: EyeIcon },
    { label: 'Personal', value: 'personal', icon: UserIcon },
    { label: 'Contact', value: 'contact', icon: PhoneIcon },
    { label: 'Professional', value: 'professional', icon: BriefcaseIcon },
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await api.get('/profile/me');
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        setProfile({
          id: 1,
          user_id: 35,
          company_id: 1,
          department: 'Engineering',
          position: 'Senior Software Engineer',
          phone: '+1-555-0123',
          hire_date: '2023-01-15T00:00:00Z',
          address: '123 Tech Street',
          city: 'San Francisco',
          emergency_contact: 'Jane Doe - +1-555-0456',
          employee_id: 'EMP001',
          profile_picture_url: null,
          is_active: true
        });
        setAlert({ show: true, message: 'Using demo data - Database connection issue detected.', type: 'warning' });
      } finally {
        setLoading(false);
      }
    };

    if (authUser) {
      fetchProfile();
    }
  }, [authUser]);

  useEffect(() => {
    if (profile) {
      setUser({
        full_name: authUser?.full_name,
        role: authUser?.role,
        employee_id: profile.employee_id,
        profile_picture_url: profile.profile_picture_url,
      });
    }
  }, [profile, authUser]);

  const handleEditSuccess = () => {
    setEditing(false);
    setAlert({ show: true, message: 'Profile update request submitted successfully! It will be reviewed by an administrator.', type: 'success' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex justify-center items-center p-4">
        <Card className="w-full max-w-4xl shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardBody className="p-8">
            <div className="animate-pulse space-y-6">
              <div className="flex items-center space-x-4">
                <div className="h-20 w-20 bg-gray-300 rounded-full"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-8 bg-gray-300 rounded w-1/3"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/4"></div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  const profileCompletion = calculateProfileCompletion(profile);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-100 via-transparent to-transparent opacity-40"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-indigo-200/30 to-transparent rounded-full -translate-y-48 translate-x-48"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-blue-200/30 to-transparent rounded-full translate-y-48 -translate-x-48"></div>

      {/* Professional Header */}
      <div className="relative bg-white/90 backdrop-blur-md shadow-lg border-b border-gray-200/60">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-10">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
              <div className="flex-1 text-center lg:text-left">
                <div className="flex items-center justify-center lg:justify-start gap-6 mb-6">
                  <div className="relative">
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl blur-lg opacity-30"></div>
                    <div className="relative h-20 w-20 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl border-4 border-white">
                      <UserIcon className="h-10 w-10 text-white" />
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Typography variant="h1" className="font-bold text-gray-900 mb-2 text-4xl bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                      Employee Profile
                    </Typography>
                    <Typography variant="lead" className="text-gray-600 flex items-center justify-center lg:justify-start gap-3 text-lg">
                      <div className="h-2 w-2 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"></div>
                      <span className="font-medium">Professional Information Management System</span>
                      <div className="h-2 w-2 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"></div>
                    </Typography>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-end">
                <Tooltip content="Export Profile Data" placement="top">
                  <Button
                    variant="outlined"
                    size="lg"
                    className="flex items-center justify-center gap-3 border-2 border-gray-300 hover:border-blue-500 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-300 shadow-md hover:shadow-lg px-6 py-4 rounded-xl font-semibold"
                  >
                    <DocumentTextIcon className="h-5 w-5" />
                    <span className="hidden sm:inline font-semibold">Export Data</span>
                  </Button>
                </Tooltip>
                <Button
                  onClick={() => setEditing(true)}
                  size="lg"
                  className="flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 shadow-xl hover:shadow-2xl transition-all duration-300 text-white font-bold px-8 py-4 rounded-xl transform hover:scale-105"
                >
                  <PencilIcon className="h-5 w-5" />
                  Edit Profile
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Completion Status */}
        <Card className="mb-8 shadow-2xl border-0 bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/50 backdrop-blur-sm relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5"></div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-200/20 to-transparent rounded-full -translate-y-16 translate-x-16"></div>
          <CardBody className="relative p-10">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-6">
                  <Typography variant="h4" className="font-bold text-gray-900 flex items-center gap-4">
                    <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg">
                      <ChartBarIcon className="h-7 w-7 text-white" />
                    </div>
                    <span className="bg-gradient-to-r from-gray-900 to-blue-900 bg-clip-text text-transparent">
                      Profile Completion Status
                    </span>
                  </Typography>
                  <Chip
                    size="lg"
                    color={profileCompletion === 100 ? 'green' : profileCompletion >= 75 ? 'blue' : 'amber'}
                    className="px-6 py-3 font-bold text-base shadow-lg"
                    value={`${profileCompletion}% Complete`}
                    icon={profileCompletion === 100 ? <TrophyIcon className="h-5 w-5" /> : <ClockIcon className="h-5 w-5" />}
                  />
                </div>
                <div className="mb-6">
                  <Progress
                    value={profileCompletion}
                    color={profileCompletion === 100 ? 'green' : 'blue'}
                    className="h-5 mb-4 shadow-inner"
                  />
                  <div className="flex justify-between text-sm text-gray-600 font-medium">
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                  </div>
                </div>
                <Typography className="text-gray-700 text-lg leading-relaxed">
                  {profileCompletion === 100
                    ? '🎉 Excellent! Your profile is complete and professionally presented with all required information.'
                    : `📝 ${100 - profileCompletion}% of fields need to be filled to complete your professional profile.`
                  }
                </Typography>
              </div>
              {profileCompletion < 100 && (
                <div className="flex-shrink-0">
                  <Button
                    variant="outlined"
                    size="lg"
                    onClick={() => setEditing(true)}
                    className="flex items-center gap-3 border-2 border-blue-400 hover:border-blue-500 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-300 shadow-lg hover:shadow-xl px-8 py-4 rounded-xl font-semibold text-blue-700"
                  >
                    <PencilIcon className="h-5 w-5" />
                    Complete Profile
                  </Button>
                </div>
              )}
            </div>
          </CardBody>
        </Card>

        {alert.show && (
          <Alert
            color={alert.type === 'success' ? 'green' : 'amber'}
            className="mb-6 shadow-lg border-l-4"
            onClose={() => setAlert({ show: false })}
            icon={alert.type === 'success' ? <CheckCircleIcon className="h-5 w-5" /> : <ExclamationTriangleIcon className="h-5 w-5" />}
          >
            {alert.message}
          </Alert>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Profile Card - Left Sidebar */}
          <div className="xl:col-span-1">
            <div className="sticky top-8">
              <ProfileCard user={user} profile={profile} onEdit={() => setEditing(true)} />
            </div>
          </div>

          {/* Profile Details - Main Content */}
          <div className="xl:col-span-3">
            <Card className="shadow-2xl border-0 bg-white/90 backdrop-blur-sm overflow-hidden relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5"></div>
              <CardBody className="relative p-0">
                <Tabs value={activeTab} onChange={setActiveTab}>
                  <TabsHeader className="bg-gradient-to-r from-gray-50 via-blue-50/50 to-indigo-50/50 border-b border-gray-200/60 backdrop-blur-sm">
                    {tabs.map(({ label, value, icon: Icon }) => (
                      <Tab
                        key={value}
                        value={value}
                        onClick={() => setActiveTab(value)}
                        className={`transition-all duration-300 px-8 py-5 relative ${
                          activeTab === value
                            ? 'text-blue-700 bg-white shadow-lg border-b-3 border-blue-500 font-bold'
                            : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50/70 font-semibold'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${
                            activeTab === value
                              ? 'bg-blue-100 text-blue-600'
                              : 'bg-gray-100 text-gray-500 group-hover:bg-blue-100 group-hover:text-blue-600'
                          } transition-all duration-300`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className="font-semibold text-base">{label}</span>
                        </div>
                        {activeTab === value && (
                          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500"></div>
                        )}
                      </Tab>
                    ))}
                  </TabsHeader>
                  <TabsBody className="bg-white">
                    <TabPanel value="overview" className="p-8">
                      <ProfileDetails profile={profile} view="overview" />
                    </TabPanel>
                    <TabPanel value="personal" className="p-8">
                      <ProfileDetails profile={profile} view="personal" />
                    </TabPanel>
                    <TabPanel value="contact" className="p-8">
                      <ProfileDetails profile={profile} view="contact" />
                    </TabPanel>
                    <TabPanel value="professional" className="p-8">
                      <ProfileDetails profile={profile} view="professional" />
                    </TabPanel>
                  </TabsBody>
                </Tabs>
              </CardBody>
            </Card>
          </div>
        </div>
      </div>

      {/* Edit Profile Dialog */}
      <Dialog open={editing} handler={setEditing} size="xl" className="max-h-[90vh] overflow-y-auto">
        <DialogHeader className="flex items-center justify-between bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white px-8 py-6">
          <div>
            <Typography variant="h3" className="text-white font-bold">
              Edit Professional Profile
            </Typography>
            <Typography variant="small" className="text-blue-100 mt-1">
              Update your professional information and career details
            </Typography>
          </div>
          <Chip
            size="sm"
            color="blue-gray"
            className="bg-blue-gray-50 text-blue-600 font-semibold"
            value="Pending Admin Review"
            icon={<ClockIcon className="h-4 w-4" />}
          />
        </DialogHeader>
        <DialogBody className="px-8 py-6">
          <EditProfileForm
            profile={profile}
            onClose={() => setEditing(false)}
            onSuccess={handleEditSuccess}
          />
        </DialogBody>
        <DialogFooter className="px-8 pb-6 bg-gray-50 border-t">
          <Button
            variant="text"
            color="red"
            onClick={() => setEditing(false)}
            className="mr-3 font-semibold"
          >
            Cancel
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

const ProfileCard = ({ user, profile, onEdit }) => {
  if (!user) {
    return (
      <Card className="w-full shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardBody className="text-center p-8">
          <div className="animate-pulse">
            <div className="h-24 w-24 bg-gray-300 rounded-full mx-auto mb-4"></div>
            <div className="h-6 bg-gray-300 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
          </div>
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
    <Card className="w-full shadow-2xl border-0 bg-white/90 backdrop-blur-sm hover:shadow-3xl transition-all duration-500 overflow-hidden">
      {/* Decorative gradient border */}
      <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500"></div>

      <CardBody className="p-8">
        {/* Profile Picture Section */}
        <div className="text-center mb-8">
          <div className="relative inline-block group">
            <div className="absolute -inset-2 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-full blur-lg opacity-20 group-hover:opacity-40 transition duration-500"></div>
            <Avatar
              src={profile?.profile_picture_url || user.profile_picture_url || 'https://via.placeholder.com/150'}
              alt={user.full_name}
              size="xl"
              className="relative mx-auto mb-6 ring-4 ring-white shadow-2xl"
              placeholder={
                <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white text-4xl font-bold flex items-center justify-center w-full h-full rounded-full shadow-inner">
                  {getInitials(user.full_name)}
                </div>
              }
            />
            <Tooltip content="Update Profile Picture">
              <button
                onClick={onEdit}
                className="absolute -bottom-2 -right-2 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white p-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 border-2 border-white"
              >
                <CameraIcon className="h-5 w-5" />
              </button>
            </Tooltip>
          </div>

          {/* User Info */}
          <div className="space-y-3 text-center">
            <Typography variant="h4" className="font-bold text-gray-900 tracking-tight leading-tight">
              {user.full_name}
            </Typography>
            <Typography className="text-gray-600 flex items-center justify-center gap-2 text-sm">
              <EnvelopeIcon className="h-4 w-4 flex-shrink-0" />
              <span className="truncate">{user.email}</span>
            </Typography>

            {/* Role Badge */}
            <div className="flex justify-center mt-4">
              <Chip
                size="lg"
                variant="filled"
                color={getRoleColor(user.role)}
                value={user.role?.toUpperCase() || 'USER'}
                icon={getRoleIcon(user.role)}
                className="capitalize shadow-lg px-4 py-2 font-bold"
              />
            </div>
          </div>
        </div>

        {/* Profile Stats */}
        {profile && (
          <div className="space-y-6 mb-8">
            {/* Status Section */}
            <div className="text-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100">
              <Typography variant="small" className="font-bold text-gray-700 uppercase tracking-wide mb-3">
                Account Status
              </Typography>
              <div className="flex justify-center">
                <Badge
                  color={profile.is_active ? 'green' : 'red'}
                  className="px-4 py-2 flex items-center gap-2 font-semibold text-sm"
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

            {/* Quick Info */}
            {(profile.position || profile.department) && (
              <div className="space-y-4">
                <Typography variant="small" className="font-bold text-gray-700 uppercase tracking-wide text-center">
                  Professional Summary
                </Typography>
                <div className="space-y-3">
                  {profile.position && (
                    <div className="flex items-center justify-center gap-3 text-gray-700 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="bg-blue-100 p-2 rounded-full flex-shrink-0">
                        <BriefcaseIcon className="h-4 w-4 text-blue-600" />
                      </div>
                      <Typography className="font-semibold text-blue-900 text-center">
                        {profile.position}
                      </Typography>
                    </div>
                  )}
                  {profile.department && (
                    <div className="flex items-center justify-center gap-3 text-gray-700 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                      <div className="bg-indigo-100 p-2 rounded-full flex-shrink-0">
                        <BuildingOfficeIcon className="h-4 w-4 text-indigo-600" />
                      </div>
                      <Typography className="font-semibold text-indigo-900 text-center">
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
        <div className="space-y-4">
          <Button
            onClick={onEdit}
            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-300 text-white font-bold py-4 rounded-xl"
            size="lg"
          >
            <PencilIcon className="h-5 w-5" />
            Edit Profile
          </Button>

          <Button
            variant="outlined"
            className="w-full border-2 border-gray-300 hover:border-blue-400 hover:bg-blue-50 transition-all duration-300 font-semibold py-4 rounded-xl"
            size="lg"
          >
            <EyeIcon className="h-5 w-5 mr-3" />
            View Full Profile
          </Button>
        </div>

        {/* Last Updated */}
        {profile?.updated_at && (
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <Typography variant="small" className="text-gray-500">
              Last updated: {new Date(profile.updated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </Typography>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

const ProfileDetails = ({ profile, view = 'overview' }) => {
  if (!profile) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-48 bg-gray-200 rounded mx-auto"></div>
            <div className="h-4 w-64 bg-gray-200 rounded mx-auto"></div>
          </div>
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

  // Personal Information Fields
  const personalFields = [
    {
      icon: UserIcon,
      label: 'Gender',
      value: profile.gender || 'Not set',
      category: 'personal',
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200'
    },
    {
      icon: CalendarIcon,
      label: 'Date of Birth',
      value: profile.date_of_birth ? formatDate(profile.date_of_birth) : 'Not set',
      category: 'personal',
      color: 'indigo',
      bgColor: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
      borderColor: 'border-indigo-200'
    }
  ];

  // Contact Information Fields
  const contactFields = [
    {
      icon: PhoneIcon,
      label: 'Phone Number',
      value: formatPhone(profile.phone),
      category: 'contact',
      color: 'green',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200'
    },
    {
      icon: MapPinIcon,
      label: 'Address',
      value: profile.address || 'Not set',
      category: 'contact',
      color: 'orange',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      borderColor: 'border-orange-200'
    },
    {
      icon: BuildingOfficeIcon,
      label: 'City',
      value: profile.city || 'Not set',
      category: 'contact',
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200'
    },
    {
      icon: HeartIcon,
      label: 'Emergency Contact',
      value: profile.emergency_contact || 'Not set',
      category: 'contact',
      color: 'red',
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600',
      borderColor: 'border-red-200'
    }
  ];

  // Professional Information Fields
  const professionalFields = [
    {
      icon: BuildingOfficeIcon,
      label: 'Department',
      value: profile.department || 'Not set',
      category: 'professional',
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200'
    },
    {
      icon: BriefcaseIcon,
      label: 'Position',
      value: profile.position || 'Not set',
      category: 'professional',
      color: 'emerald',
      bgColor: 'bg-emerald-50',
      iconColor: 'text-emerald-600',
      borderColor: 'border-emerald-200'
    },
    {
      icon: CalendarIcon,
      label: 'Hire Date',
      value: formatDate(profile.hire_date),
      category: 'professional',
      color: 'teal',
      bgColor: 'bg-teal-50',
      iconColor: 'text-teal-600',
      borderColor: 'border-teal-200'
    },
    {
      icon: AcademicCapIcon,
      label: 'Employee ID',
      value: profile.employee_id || 'Not set',
      category: 'professional',
      color: 'amber',
      bgColor: 'bg-amber-50',
      iconColor: 'text-amber-600',
      borderColor: 'border-amber-200'
    }
  ];

  const renderField = (field) => {
    const Icon = field.icon;
    const isSet = field.value !== 'Not set';

    return (
      <Card key={field.label} className={`transition-all duration-300 hover:shadow-xl ${field.bgColor} border-l-4 ${field.borderColor} hover:scale-[1.02] relative overflow-hidden group`}>
        <div className="absolute inset-0 bg-gradient-to-r from-white/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <CardBody className="relative p-8">
          <div className="flex items-start gap-6">
            <div className={`p-4 rounded-2xl ${field.bgColor} flex-shrink-0 shadow-lg group-hover:shadow-xl transition-all duration-300 relative`}>
              <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <Icon className={`h-7 w-7 ${field.iconColor} relative z-10`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-4">
                <Typography variant="h5" className="font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                  {field.label}
                </Typography>
                <div className="flex-shrink-0">
                  {isSet ? (
                    <div className="p-2 bg-green-100 rounded-full">
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    </div>
                  ) : (
                    <div className="p-2 bg-amber-100 rounded-full">
                      <ExclamationTriangleIcon className="h-5 w-5 text-amber-600" />
                    </div>
                  )}
                </div>
              </div>
              <Typography variant="lead" className="text-gray-700 mb-3 font-medium leading-relaxed text-lg">
                {field.value}
              </Typography>
              {!isSet && (
                <Typography variant="small" className="text-gray-500 italic font-medium">
                  Click "Edit Profile" to add this information
                </Typography>
              )}
            </div>
          </div>
        </CardBody>
      </Card>
    );
  };

  const hasProfessionalData = professionalFields.some(field => field.value !== 'Not set');
  const hasContactData = contactFields.some(field => field.value !== 'Not set');
  const hasPersonalData = personalFields.some(field => field.value !== 'Not set');

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {hasProfessionalData && (
          <Card className="text-center p-8 bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-100 border-l-4 border-blue-500 shadow-xl hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-indigo-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl w-16 h-16 mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300">
                <BriefcaseIcon className="h-8 w-8 text-white mx-auto" />
              </div>
              <Typography variant="h2" className="font-bold text-blue-800 mb-3 text-4xl">
                {professionalFields.filter(field => field.value !== 'Not set').length}
              </Typography>
              <Typography variant="small" className="font-bold text-blue-700 text-base">
                Professional Details
              </Typography>
            </div>
          </Card>
        )}
        {hasContactData && (
          <Card className="text-center p-8 bg-gradient-to-br from-green-50 via-green-100 to-emerald-100 border-l-4 border-green-500 shadow-xl hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-green-600/5 to-emerald-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="p-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl w-16 h-16 mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300">
                <PhoneIcon className="h-8 w-8 text-white mx-auto" />
              </div>
              <Typography variant="h2" className="font-bold text-green-800 mb-3 text-4xl">
                {contactFields.filter(field => field.value !== 'Not set').length}
              </Typography>
              <Typography variant="small" className="font-bold text-green-700 text-base">
                Contact Information
              </Typography>
            </div>
          </Card>
        )}
        {hasPersonalData && (
          <Card className="text-center p-8 bg-gradient-to-br from-purple-50 via-purple-100 to-indigo-100 border-l-4 border-purple-500 shadow-xl hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/5 to-indigo-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="p-4 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl w-16 h-16 mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300">
                <UserIcon className="h-8 w-8 text-white mx-auto" />
              </div>
              <Typography variant="h2" className="font-bold text-purple-800 mb-3 text-4xl">
                {personalFields.filter(field => field.value !== 'Not set').length}
              </Typography>
              <Typography variant="small" className="font-bold text-purple-700 text-base">
                Personal Information
              </Typography>
            </div>
          </Card>
        )}
        <Card className="text-center p-8 bg-gradient-to-br from-orange-50 via-orange-100 to-amber-100 border-l-4 border-orange-500 shadow-xl hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-orange-600/5 to-amber-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div className="relative">
            <div className="p-4 bg-gradient-to-r from-orange-600 to-amber-600 rounded-2xl w-16 h-16 mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300">
              <CameraIcon className="h-8 w-8 text-white mx-auto" />
            </div>
            <Typography variant="h2" className="font-bold text-orange-800 mb-3 text-4xl">
              {profile.profile_picture_url ? '1' : '0'}
            </Typography>
            <Typography variant="small" className="font-bold text-orange-700 text-base">
              Profile Picture
            </Typography>
          </div>
        </Card>
      </div>

      {/* Key Information Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {hasProfessionalData && (
          <div>
            <Typography variant="h4" className="mb-6 flex items-center gap-3 font-bold text-gray-900">
              <BriefcaseIcon className="h-6 w-6 text-blue-600" />
              Professional Information
            </Typography>
            <div className="space-y-4">
              {professionalFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
            </div>
          </div>
        )}
        {hasContactData && (
          <div>
            <Typography variant="h4" className="mb-6 flex items-center gap-3 font-bold text-gray-900">
              <PhoneIcon className="h-6 w-6 text-green-600" />
              Contact Information
            </Typography>
            <div className="space-y-4">
              {contactFields.filter(field => field.value !== 'Not set').slice(0, 2).map(renderField)}
            </div>
          </div>
        )}
      </div>

      {/* Additional Information */}
      {(hasPersonalData || contactFields.filter(field => field.value !== 'Not set').slice(2).length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {hasPersonalData && (
            <div>
              <Typography variant="h4" className="mb-6 flex items-center gap-3 font-bold text-gray-900">
                <UserIcon className="h-6 w-6 text-purple-600" />
                Personal Information
              </Typography>
              <div className="space-y-4">
                {personalFields.filter(field => field.value !== 'Not set').map(renderField)}
              </div>
            </div>
          )}
          {contactFields.filter(field => field.value !== 'Not set').slice(2).length > 0 && (
            <div>
              <Typography variant="h4" className="mb-6 flex items-center gap-3 font-bold text-gray-900">
                <MapPinIcon className="h-6 w-6 text-orange-600" />
                Location & Emergency
              </Typography>
              <div className="space-y-4">
                {contactFields.filter(field => field.value !== 'Not set').slice(2).map(renderField)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* No data message */}
      {!hasProfessionalData && !hasContactData && !hasPersonalData && (
        <Card className="p-12 text-center bg-gradient-to-br from-gray-50 to-blue-50 border-2 border-dashed border-gray-300">
          <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <Typography variant="h5" className="text-gray-600 mb-2">
            No profile information available
          </Typography>
          <Typography className="text-gray-500">
            Click "Edit Profile" to add your professional information
          </Typography>
        </Card>
      )}
    </div>
  );

  const renderPersonal = () => (
    <div>
      <Typography variant="h4" className="mb-8 flex items-center gap-3 font-bold text-gray-900">
        <UserIcon className="h-6 w-6 text-purple-600" />
        Personal Information
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {personalFields.map(renderField)}
      </div>
    </div>
  );

  const renderContact = () => (
    <div>
      <Typography variant="h4" className="mb-8 flex items-center gap-3 font-bold text-gray-900">
        <PhoneIcon className="h-6 w-6 text-green-600" />
        Contact Details
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {contactFields.map(renderField)}
      </div>
    </div>
  );

  const renderProfessional = () => (
    <div>
      <Typography variant="h4" className="mb-8 flex items-center gap-3 font-bold text-gray-900">
        <BriefcaseIcon className="h-6 w-6 text-blue-600" />
        Professional Information
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {professionalFields.map(renderField)}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (view) {
      case 'personal':
        return renderPersonal();
      case 'contact':
        return renderContact();
      case 'professional':
        return renderProfessional();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="space-y-8">
      {renderContent()}
    </div>
  );
};

export default ProfileProfessional;
