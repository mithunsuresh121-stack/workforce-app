import React, { useState } from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { Card, CardBody, CardHeader, Typography, Input, Button, Alert, Select, Option, Textarea } from '@material-tailwind/react';
import { api } from '../contexts/AuthContext';

const EditProfileForm = ({ profile, onClose, onSuccess }) => {
  const [updating, setUpdating] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });

  const validationSchema = Yup.object({
    department: Yup.string(),
    position: Yup.string(),
    phone: Yup.string(),
    hire_date: Yup.date(),
    gender: Yup.string(),
    address: Yup.string(),
    city: Yup.string(),
    emergency_contact: Yup.string(),
    employee_id: Yup.string(),
    profile_picture_url: Yup.string().url('Invalid URL'),
  });

  const handleSubmit = async (values) => {
    try {
      setUpdating(true);
      setAlert({ show: false });

      // Create profile update request
      const payload = {
        request_type: 'update',
        payload: values
      };

      await api.post('/profile/request-update', payload);

      setAlert({ show: true, message: 'Profile update request submitted successfully! It will be reviewed by an administrator.', type: 'success' });

      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Error submitting profile update request:', error);
      setAlert({ show: true, message: 'Failed to submit request. Please try again.', type: 'error' });
    } finally {
      setUpdating(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader floated={false} shadow={false} color="transparent">
        <Typography variant="h5" color="blue-gray">
          Request Profile Update
        </Typography>
        <Typography variant="small" color="gray">
          Changes will be reviewed by an administrator before being applied.
        </Typography>
      </CardHeader>
      <CardBody>
        {alert.show && (
          <Alert color={alert.type === 'success' ? 'green' : 'red'} className="mb-6">
            {alert.message}
          </Alert>
        )}

        <Formik
          initialValues={{
            department: profile?.department || '',
            position: profile?.position || '',
            phone: profile?.phone || '',
            hire_date: profile?.hire_date ? new Date(profile.hire_date).toISOString().split('T')[0] : '',
            gender: profile?.gender || '',
            address: profile?.address || '',
            city: profile?.city || '',
            emergency_contact: profile?.emergency_contact || '',
            employee_id: profile?.employee_id || '',
            profile_picture_url: profile?.profile_picture_url || '',
          }}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ errors, touched, setFieldValue, values }) => (
            <Form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Department
                  </Typography>
                  <Input
                    size="lg"
                    name="department"
                    value={values.department}
                    onChange={(e) => setFieldValue('department', e.target.value)}
                    error={touched.department && errors.department}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Position
                  </Typography>
                  <Input
                    size="lg"
                    name="position"
                    value={values.position}
                    onChange={(e) => setFieldValue('position', e.target.value)}
                    error={touched.position && errors.position}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Phone
                  </Typography>
                  <Input
                    size="lg"
                    name="phone"
                    value={values.phone}
                    onChange={(e) => setFieldValue('phone', e.target.value)}
                    error={touched.phone && errors.phone}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Hire Date
                  </Typography>
                  <Input
                    size="lg"
                    type="date"
                    name="hire_date"
                    value={values.hire_date}
                    onChange={(e) => setFieldValue('hire_date', e.target.value)}
                    error={touched.hire_date && errors.hire_date}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Gender
                  </Typography>
                  <Select
                    size="lg"
                    name="gender"
                    value={values.gender}
                    onChange={(value) => setFieldValue('gender', value)}
                  >
                    <Option value="">Select Gender</Option>
                    <Option value="Male">Male</Option>
                    <Option value="Female">Female</Option>
                    <Option value="Other">Other</Option>
                  </Select>
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Employee ID
                  </Typography>
                  <Input
                    size="lg"
                    name="employee_id"
                    value={values.employee_id}
                    onChange={(e) => setFieldValue('employee_id', e.target.value)}
                    error={touched.employee_id && errors.employee_id}
                  />
                </div>

                <div className="md:col-span-2">
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Address
                  </Typography>
                  <Textarea
                    size="lg"
                    name="address"
                    value={values.address}
                    onChange={(e) => setFieldValue('address', e.target.value)}
                    error={touched.address && errors.address}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    City
                  </Typography>
                  <Input
                    size="lg"
                    name="city"
                    value={values.city}
                    onChange={(e) => setFieldValue('city', e.target.value)}
                    error={touched.city && errors.city}
                  />
                </div>

                <div>
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Emergency Contact
                  </Typography>
                  <Input
                    size="lg"
                    name="emergency_contact"
                    value={values.emergency_contact}
                    onChange={(e) => setFieldValue('emergency_contact', e.target.value)}
                    error={touched.emergency_contact && errors.emergency_contact}
                  />
                </div>

                <div className="md:col-span-2">
                  <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                    Profile Picture URL
                  </Typography>
                  <Input
                    size="lg"
                    name="profile_picture_url"
                    value={values.profile_picture_url}
                    onChange={(e) => setFieldValue('profile_picture_url', e.target.value)}
                    error={touched.profile_picture_url && errors.profile_picture_url}
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <Button
                  type="submit"
                  className="flex-1"
                  loading={updating}
                  disabled={updating}
                >
                  {updating ? 'Submitting...' : 'Submit Request'}
                </Button>
                <Button
                  type="button"
                  variant="outlined"
                  className="flex-1"
                  onClick={onClose}
                  disabled={updating}
                >
                  Cancel
                </Button>
              </div>
            </Form>
          )}
        </Formik>
      </CardBody>
    </Card>
  );
};

export default EditProfileForm;
