import React, { useState, useEffect } from 'react';
import { Typography, Alert, Spinner, Dialog, DialogHeader, DialogBody, DialogFooter, Button } from '@material-tailwind/react';
import { useAuth, api } from '../contexts/AuthContext';
import ProfileCard from '../components/ProfileCard';
import ProfileDetails from '../components/ProfileDetails';
import EditProfileForm from '../components/EditProfileForm';

const Profile = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);

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
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="p-4">
      <Typography variant="h3" color="blue-gray" className="mb-6">
        Profile
      </Typography>

      {alert.show && (
        <Alert color={alert.type === 'success' ? 'green' : 'red'} className="mb-6">
          {alert.message}
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="lg:col-span-1">
          <ProfileCard
            user={user}
            onEdit={() => setEditing(true)}
          />
        </div>

        {/* Profile Details */}
        <div className="lg:col-span-2">
          <ProfileDetails profile={profile} />
        </div>
      </div>

      {/* Edit Profile Dialog */}
      <Dialog open={editing} handler={setEditing} size="xl">
        <DialogHeader>Edit Profile</DialogHeader>
        <DialogBody>
          <EditProfileForm
            profile={profile}
            onClose={() => setEditing(false)}
            onSuccess={handleEditSuccess}
          />
        </DialogBody>
        <DialogFooter>
          <Button variant="text" color="red" onClick={() => setEditing(false)}>
            Cancel
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

export default Profile;
