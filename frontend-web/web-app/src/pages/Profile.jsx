import React, { useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import { Card, CardBody, CardHeader, Typography, Input, Button, Alert, Avatar, Spinner } from '@material-tailwind/react';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user: authUser, login } = useAuth();
  const [user, setUser] = useState({ name: '', email: '', role: '', avatar: '' });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setLoading(true);
        // Try to fetch from API, fallback to auth context
        const response = await axios.get('/api/user/profile');
        setUser(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        // Fallback to auth context data
        setUser({
          name: authUser?.name || 'John Doe',
          email: authUser?.email || 'john@example.com',
          role: authUser?.role || 'Employee',
          avatar: authUser?.avatar || 'https://via.placeholder.com/150'
        });
      } finally {
        setLoading(false);
      }
    };

    if (authUser) {
      fetchUserProfile();
    }
  }, [authUser]);

  const validationSchema = Yup.object({
    name: Yup.string().required('Name is required'),
    email: Yup.string().email('Invalid email').required('Email is required'),
  });

  const handleSubmit = async (values) => {
    try {
      setUpdating(true);
      setAlert({ show: false });

      // Update profile via API
      const response = await axios.put('/api/user/profile', values);
      setUser(response.data);

      // Update auth context if needed
      login({ ...authUser, ...response.data });

      setAlert({ show: true, message: 'Profile updated successfully!', type: 'success' });
    } catch (error) {
      console.error('Error updating profile:', error);
      setAlert({ show: true, message: 'Failed to update profile. Please try again.', type: 'error' });
    } finally {
      setUpdating(false);
    }
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
        {/* Profile Picture Card */}
        <Card className="lg:col-span-1">
          <CardBody className="text-center">
            <Avatar
              src={user.avatar}
              alt={user.name}
              size="xl"
              className="mx-auto mb-4"
            />
            <Typography variant="h5" color="blue-gray" className="mb-2">
              {user.name}
            </Typography>
            <Typography variant="small" color="gray">
              {user.role}
            </Typography>
          </CardBody>
        </Card>

        {/* Profile Form Card */}
        <Card className="lg:col-span-2">
          <CardHeader floated={false} shadow={false} color="transparent">
            <Typography variant="h5" color="blue-gray">
              Edit Profile
            </Typography>
          </CardHeader>
          <CardBody>
            <Formik
              initialValues={user}
              validationSchema={validationSchema}
              onSubmit={handleSubmit}
              enableReinitialize
            >
              {({ errors, touched, setFieldValue }) => (
                <Form className="space-y-6">
                  <div>
                    <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                      Full Name
                    </Typography>
                    <Input
                      size="lg"
                      name="name"
                      value={user.name}
                      onChange={(e) => setFieldValue('name', e.target.value)}
                      error={touched.name && errors.name}
                    />
                    {touched.name && errors.name && (
                      <Typography variant="small" color="red" className="mt-1">
                        {errors.name}
                      </Typography>
                    )}
                  </div>

                  <div>
                    <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                      Email Address
                    </Typography>
                    <Input
                      size="lg"
                      type="email"
                      name="email"
                      value={user.email}
                      onChange={(e) => setFieldValue('email', e.target.value)}
                      error={touched.email && errors.email}
                    />
                    {touched.email && errors.email && (
                      <Typography variant="small" color="red" className="mt-1">
                        {errors.email}
                      </Typography>
                    )}
                  </div>

                  <div>
                    <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                      Role
                    </Typography>
                    <Input
                      size="lg"
                      name="role"
                      value={user.role}
                      disabled
                      className="bg-gray-50"
                    />
                    <Typography variant="small" color="gray" className="mt-1">
                      Role cannot be changed from this page
                    </Typography>
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    loading={updating}
                    disabled={updating}
                  >
                    {updating ? 'Updating...' : 'Update Profile'}
                  </Button>
                </Form>
              )}
            </Formik>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
