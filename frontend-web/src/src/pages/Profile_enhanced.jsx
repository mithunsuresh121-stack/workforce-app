import React, { useState, useEffect } from 'react';
import {
  Typography,
  Alert,
  Spinner,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Button,
  Card,
  CardBody,
  Tabs,
  TabsHeader,
  TabsBody,
  Tab,
  TabPanel,
  Chip,
  Progress,
  IconButton,
  Tooltip,
  Breadcrumbs,
  Badge
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
  HomeIcon,
  ChevronRightIcon,
  ArrowLeftIcon,
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { useAuth, api } from '../contexts/AuthContext';
import ProfileCard from '../components/ProfileCard_linear';
import ProfileDetails from '../components/ProfileDetails_linear';
import EditProfileForm from '../components/EditProfileForm_linear';

const Profile = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

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
    { label: 'Overview', value: 'overview', icon: UserIcon },
    { label: 'Personal Info', value: 'personal', icon: UserIcon },
    { label: 'Contact Details', value: 'contact', icon: PhoneIcon },
    { label: 'Work Info', value: 'work', icon: CalendarIcon },
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        // Fetch employee profile from backend
        const response = await api.get('/profile/me');
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        setAlert({ show: true, message: 'Failed to load profile. Please try again.', type: 'error' });
      } finally {
        setLoading(false);
      }
    };

    if (authUser) {
      fetchProfile();
    }
  }, [authUser]);

  const handleEditSuccess = () => {
    setEditing(false);
    setAlert({ show: true, message: 'Profile update request submitted successfully! It will be reviewed by an administrator.', type: 'success' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex justify-center items-center">
        <div className="text-center bg-white p-8 rounded-2xl shadow-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <Typography variant="h6" color="blue-gray" className="mb-2">
            Loading Profile...
          </Typography>
          <Typography variant="small" color="gray">
            Please wait while we fetch your information
          </Typography>
        </div>
      </div>
    );
  }

  const profileCompletion = calculateProfileCompletion(profile);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Modern Header Section */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            {/* Breadcrumb Navigation */}
            <Breadcrumbs className="mb-4">
              <a href="/" className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
                <HomeIcon className="h-4 w-4" />
                Dashboard
              </a>
              <span className="flex items-center gap-2 text-blue-600">
                <UserIcon className="h-4 w-4" />
                Employee Profile
              </span>
            </Breadcrumbs>

            {/* Header Content */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <Typography variant="h3" color="blue-gray" className="mb-2 font-bold">
                  Employee Profile
                </Typography>
                <Typography variant="lead" color="gray" className="flex items-center gap-2">
                  <DocumentTextIcon className="h-5 w-5" />
                  Manage your personal and professional information
                </Typography>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Tooltip content="Export Profile">
                  <IconButton variant="outlined" size="lg" className="flex items-center gap-2">
                    <ShareIcon className="h-5 w-5" />
                    <span className="hidden sm:inline">Export</span>
                  </IconButton>
                </Tooltip>
                <Button
                  onClick={() => setEditing(true)}
                  size="lg"
                  className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <PencilIcon className="h-5 w-5" />
                  Edit Profile
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Completion Status */}
        <Card className="mb-8 shadow-lg border-0 bg-gradient-to-r from-white to-blue-50">
          <CardBody className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-3">
                  <Typography variant="h6" color="blue-gray" className="flex items-center gap-2">
                    <ChartBarIcon className="h-6 w-6" />
                    Profile Completion
                  </Typography>
                  <Badge
                    color={profileCompletion === 100 ? 'green' : profileCompletion >= 75 ? 'blue' : 'amber'}
                    className="px-3 py-1"
                  >
                    {profileCompletion}% Complete
                  </Badge>
                </div>
                <Progress
                  value={profileCompletion}
                  color={profileCompletion === 100 ? 'green' : 'blue'}
                  className="h-3 mb-2"
                />
                <Typography variant="small" color="gray">
                  {profileCompletion === 100
                    ? '🎉 Your profile is complete! Great job maintaining your information.'
                    : `📝 ${100 - profileCompletion}% of fields need to be filled to complete your profile.`
                  }
                </Typography>
              </div>
              {profileCompletion < 100 && (
                <div className="flex-shrink-0">
                  <Button
                    variant="outlined"
                    size="sm"
                    onClick={() => setEditing(true)}
                    className="flex items-center gap-2"
                  >
                    <PencilIcon className="h-4 w-4" />
                    Complete Profile
                  </Button>
                </div>
              )}
            </div>
          </CardBody>
        </Card>

        {alert.show && (
          <Alert
            color={alert.type === 'success' ? 'green' : 'red'}
            className="mb-6 shadow-lg"
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
              <ProfileCard
                user={user}
                profile={profile}
                onEdit={() => setEditing(true)}
              />
            </div>
          </div>

          {/* Profile Details - Main Content */}
          <div className="xl:col-span-3">
            <Card className="shadow-lg border-0 overflow-hidden">
              <CardBody className="p-0">
                <Tabs value={activeTab} onChange={setActiveTab}>
                  <TabsHeader className="bg-gradient-to-r from-gray-50 to-blue-50 border-b border-blue-gray-100">
                    {tabs.map(({ label, value, icon: Icon }) => (
                      <Tab
                        key={value}
                        value={value}
                        onClick={() => setActiveTab(value)}
                        className={`transition-all duration-300 ${
                          activeTab === value
                            ? 'text-blue-600 bg-white shadow-sm'
                            : 'text-gray-600 hover:text-blue-500 hover:bg-blue-50'
                        }`}
                      >
                        <div className="flex items-center gap-2 px-4 py-3">
                          <Icon className="w-5 h-5" />
                          <span className="font-medium">{label}</span>
                        </div>
                      </Tab>
                    ))}
                  </TabsHeader>
                  <TabsBody className="bg-white">
                    <TabPanel value="overview" className="p-6">
                      <ProfileDetails profile={profile} view="overview" />
                    </TabPanel>
                    <TabPanel value="personal" className="p-6">
                      <ProfileDetails profile={profile} view="personal" />
                    </TabPanel>
                    <TabPanel value="contact" className="p-6">
                      <ProfileDetails profile={profile} view="contact" />
                    </TabPanel>
                    <TabPanel value="work" className="p-6">
                      <ProfileDetails profile={profile} view="work" />
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
        <DialogHeader className="flex items-center justify-between bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <div>
            <Typography variant="h4" className="text-white">
              Edit Profile
            </Typography>
            <Typography variant="small" className="text-blue-100">
              Request changes to your profile information
            </Typography>
          </div>
          <Badge color="white" className="bg-white text-blue-600">
            <ClockIcon className="h-4 w-4 mr-1" />
            Pending Admin Review
          </Badge>
        </DialogHeader>
        <DialogBody className="px-6 py-4">
          <EditProfileForm
            profile={profile}
            onClose={() => setEditing(false)}
            onSuccess={handleEditSuccess}
          />
        </DialogBody>
        <DialogFooter className="px-6 pb-6 bg-gray-50">
          <Button
            variant="text"
            color="red"
            onClick={() => setEditing(false)}
            className="mr-3"
          >
            Cancel
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

export default Profile;
