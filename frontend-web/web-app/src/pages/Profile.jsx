import React, { useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

const Profile = () => {
  const [user, setUser] = useState({ name: '', email: '', role: '' });

  useEffect(() => {
    // Fetch user data
    axios.get('/api/user').then(res => setUser(res.data)).catch(() => {
      setUser({ name: 'John Doe', email: 'john@example.com', role: 'Employee' });
    });
  }, []);

  const validationSchema = Yup.object({
    name: Yup.string().required('Name is required'),
    email: Yup.string().email('Invalid email').required('Email is required'),
  });

  const handleSubmit = (values) => {
    // Update user
    axios.put('/api/user', values).then(() => alert('Profile updated')).catch(() => alert('Update failed'));
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Profile</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <Formik
          initialValues={user}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
          enableReinitialize
        >
          {({ errors, touched }) => (
            <Form>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <Field name="name" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
                {errors.name && touched.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <Field name="email" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
                {errors.email && touched.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Role</label>
                <Field name="role" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50" disabled />
              </div>
              <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Update Profile</button>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default Profile;
