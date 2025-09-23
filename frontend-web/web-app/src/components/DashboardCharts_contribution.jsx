import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { api } from '../contexts/AuthContext';
import { Card, CardBody, Typography, Spinner, Alert } from '@material-tailwind/react';
import { useNavigate } from 'react-router-dom';

const DashboardCharts = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [taskStatusData, setTaskStatusData] = useState([]);
  const [reportsData, setReportsData] = useState([]);
  const [contributionData, setContributionData] = useState({
    tasksCompleted: [],
    tasksCreated: [],
    productivity: []
  });
  const [error, setError] = useState(null);
  const [userRole, setUserRole] = useState('Employee');

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        // Get user role first
        const userResponse = await api.get('/auth/me');
        const role = userResponse.data.role || 'Employee';
        setUserRole(role);

        const [taskStatusRes] = await Promise.all([
          api.get('/dashboard/charts/task-status'),
        ]);

        setTaskStatusData(taskStatusRes.data);

        // Fetch different data based on user role
        if (role === 'Employee') {
          // For employees, fetch contribution data
          const [tasksCompletedRes, tasksCreatedRes, productivityRes] = await Promise.all([
            api.get('/dashboard/charts/contribution/tasks-completed'),
            api.get('/dashboard/charts/contribution/tasks-created'),
            api.get('/dashboard/charts/contribution/productivity'),
          ]);

          setContributionData({
            tasksCompleted: tasksCompletedRes.data,
            tasksCreated: tasksCreatedRes.data,
            productivity: productivityRes.data
          });
        } else {
          // For managers/admins, fetch reports data
          const reportsRes = await api.get('/dashboard/charts/reports');
          setReportsData(reportsRes.data);
        }
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

  const handleContributionClick = (data, chartType) => {
    if (data && data.name) {
      if (chartType === 'tasksCompleted') {
        navigate(`/tasks?filter=completed`);
      } else if (chartType === 'tasksCreated') {
        navigate(`/tasks?filter=created`);
      } else if (chartType === 'productivity') {
        navigate(`/tasks`);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner className="h-8 w-8" />
        <Typography variant="small" className="ml-2">Loading charts...</Typography>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert color="red" className="max-w-md">
          <Typography variant="h5" className="mb-2">Error loading charts</Typography>
          <Typography variant="small">{error}</Typography>
        </Alert>
      </div>
    );
  }

  // Colors for charts
  const COLORS = {
    taskStatus: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
    reports: ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'],
    contribution: {
      tasksCompleted: ['#10B981', '#059669', '#047857', '#065F46'],
      tasksCreated: ['#3B82F6', '#2563EB', '#1D4ED8', '#1E40AF'],
      productivity: ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6']
    }
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

  // Custom tooltip for contribution charts
  const ContributionTooltip = ({ active, payload, chartType }) => {
    if (active && payload && payload.length) {
      let description = '';
      switch (chartType) {
        case 'tasksCompleted':
          description = 'Click to view completed tasks';
          break;
        case 'tasksCreated':
          description = 'Click to view created tasks';
          break;
        case 'productivity':
          description = 'Click to view all tasks';
          break;
        default:
          description = 'Click to view tasks';
      }

      return (
        <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
          <p className="font-medium">{`${payload[0].name}: ${payload[0].value}`}</p>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Task Status Chart */}
      <Card>
        <CardBody>
          <Typography variant="h5" color="blue-gray" className="mb-4">
            Task Status Distribution
          </Typography>
          <div className="h-64">
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
          </div>
          <Typography variant="small" color="gray" className="mt-2 text-center">
            Click on segments to view tasks by status
          </Typography>
        </CardBody>
      </Card>

      {/* Contribution Charts for Employees or Reports Chart for Others */}
      {userRole === 'Employee' ? (
        <>
          {/* Tasks Completed Over Time */}
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-4">
                Tasks Completed Over Time
              </Typography>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={contributionData.tasksCompleted}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip content={<ContributionTooltip chartType="tasksCompleted" />} />
                    <Bar
                      dataKey="value"
                      fill="#10B981"
                      onClick={(data) => handleContributionClick(data, 'tasksCompleted')}
                      style={{ cursor: 'pointer' }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <Typography variant="small" color="gray" className="mt-2 text-center">
                Click on bars to view completed tasks
              </Typography>
            </CardBody>
          </Card>

          {/* Tasks Created */}
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-4">
                Tasks Created by Status
              </Typography>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={contributionData.tasksCreated}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      onClick={(data) => handleContributionClick(data, 'tasksCreated')}
                      style={{ cursor: 'pointer' }}
                    >
                      {contributionData.tasksCreated.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS.contribution.tasksCreated[index % COLORS.contribution.tasksCreated.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<ContributionTooltip chartType="tasksCreated" />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <Typography variant="small" color="gray" className="mt-2 text-center">
                Click on segments to view created tasks
              </Typography>
            </CardBody>
          </Card>

          {/* Productivity Metrics */}
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-4">
                Productivity Overview
              </Typography>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={contributionData.productivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip content={<ContributionTooltip chartType="productivity" />} />
                    <Bar
                      dataKey="value"
                      fill="#8B5CF6"
                      onClick={(data) => handleContributionClick(data, 'productivity')}
                      style={{ cursor: 'pointer' }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <Typography variant="small" color="gray" className="mt-2 text-center">
                Click on bars to view all tasks
              </Typography>
            </CardBody>
          </Card>
        </>
      ) : (
        /* Reports Chart for Managers/Admins */
        <Card>
          <CardBody>
            <Typography variant="h5" color="blue-gray" className="mb-4">
              Reports & Requests
            </Typography>
            <div className="h-64">
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
            </div>
            <Typography variant="small" color="gray" className="mt-2 text-center">
              Click on bars to view requests by status
            </Typography>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

export default DashboardCharts;
