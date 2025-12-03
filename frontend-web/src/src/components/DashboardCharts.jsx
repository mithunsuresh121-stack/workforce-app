import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const DashboardCharts = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [taskStatusData, setTaskStatusData] = useState([]);
  const [reportsData, setReportsData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        console.log('Fetching chart data...');
        const [taskStatusRes, reportsRes] = await Promise.all([
          api.get('/dashboard/charts/task-status'),
          api.get('/dashboard/charts/reports'),
        ]);

        console.log('Task Status Data:', taskStatusRes.data);
        console.log('Reports Data:', reportsRes.data);

        setTaskStatusData(taskStatusRes.data);
        setReportsData(reportsRes.data);
      } catch (err) {
        console.error('Error fetching chart data:', err);
        setError('Failed to load chart data');
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, []);

  // Handle chart segment click navigation
  const handleTaskStatusClick = (data) => {
    if (data && data.name) {
      const status = data.name.toLowerCase().replace(' ', '-');
      navigate(`/tasks?filter=${status}`);
    }
  };

  const handleReportsClick = (data) => {
    if (data && data.name) {
      const status = data.name.toLowerCase().replace(' ', '-');
      navigate(`/approvals?filter=${status}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="w-8 h-8 border-2 border-accent-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="ml-2 text-sm text-neutral-600">Loading charts...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="max-w-md bg-danger-50 border border-danger-200 rounded-lg p-4">
          <h5 className="text-lg font-semibold text-danger-800 mb-2">Error loading charts</h5>
          <p className="text-sm text-danger-700">{error}</p>
        </div>
      </div>
    );
  }

  // Colors for charts
  const COLORS = {
    taskStatus: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
    reports: ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c']
  };

  // Custom tooltip for task status chart
  const TaskStatusTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
          <p className="font-medium">{`${payload[0].name}: ${payload[0].value}`}</p>
          <p className="text-sm text-gray-600">Click to view tasks</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for reports chart
  const ReportsTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
          <p className="font-medium">{`${payload[0].name}: ${payload[0].value}`}</p>
          <p className="text-sm text-gray-600">Click to view requests</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Task Status Chart */}
      <div className="bg-surface border border-border rounded-lg shadow-linear-sm">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-neutral-900 mb-4">
            Task Status Distribution
          </h5>
          <div className="h-64">
            {taskStatusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={taskStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    onClick={handleTaskStatusClick}
                    style={{ cursor: 'pointer' }}
                  >
                    {taskStatusData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS.taskStatus[index % COLORS.taskStatus.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<TaskStatusTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <span className="text-sm text-gray-500">
                  No task data available
                </span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">
            Click on segments to view tasks by status
          </p>
        </div>
      </div>

      {/* Reports Chart */}
      <div className="bg-surface border border-border rounded-lg shadow-linear-sm">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-neutral-900 mb-4">
            Reports & Requests
          </h5>
          <div className="h-64">
            {reportsData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={reportsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip content={<ReportsTooltip />} />
                  <Legend />
                  <Bar
                    dataKey="value"
                    fill="#8884d8"
                    onClick={handleReportsClick}
                    style={{ cursor: 'pointer' }}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <span className="text-sm text-gray-500">
                  No reports data available
                </span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">
            Click on bars to view requests by status
          </p>
        </div>
      </div>
    </div>
  );
};

export default DashboardCharts;
