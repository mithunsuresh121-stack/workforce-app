import React, { useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

const Leave = () => {
  const [leaves, setLeaves] = useState([]);

  useEffect(() => {
    // Fetch leaves
    axios.get('/api/leaves').then(res => setLeaves(res.data)).catch(() => {
      setLeaves([
        { id: 1, type: 'Vacation', startDate: '2023-10-01', endDate: '2023-10-05', status: 'Approved' },
      ]);
    });
  }, []);

  const validationSchema = Yup.object({
    type: Yup.string().required('Type is required'),
    startDate: Yup.date().required('Start date is required'),
    endDate: Yup.date().required('End date is required'),
  });

  const handleSubmit = (values) => {
    // Submit leave request
    axios.post('/api/leaves', values).then(() => {
      alert('Leave request submitted');
      // Refresh list
      axios.get('/api/leaves').then(res => setLeaves(res.data));
    }).catch(() => alert('Submission failed'));
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Leave</h1>
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Request Leave</h2>
        <Formik
          initialValues={{ type: '', startDate: '', endDate: '' }}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ errors, touched }) => (
            <Form>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <Field as="select" name="type" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                  <option value="">Select type</option>
                  <option value="Vacation">Vacation</option>
                  <option value="Sick">Sick</option>
                </Field>
                {errors.type && touched.type && <p className="mt-1 text-sm text-red-600">{errors.type}</p>}
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Start Date</label>
                <Field name="startDate" type="date" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
                {errors.startDate && touched.startDate && <p className="mt-1 text-sm text-red-600">{errors.startDate}</p>}
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">End Date</label>
                <Field name="endDate" type="date" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
                {errors.endDate && touched.endDate && <p className="mt-1 text-sm text-red-600">{errors.endDate}</p>}
              </div>
              <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Submit Request</button>
            </Form>
          )}
        </Formik>
      </div>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <h2 className="text-xl font-semibold p-6">Leave History</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">End Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leaves.map((leave) => (
              <tr key={leave.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{leave.type}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{leave.startDate}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{leave.endDate}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{leave.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leave;
