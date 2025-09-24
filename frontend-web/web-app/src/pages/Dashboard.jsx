import React, { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { useAuth, api } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import DashboardCharts from '../components/DashboardCharts';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState({
    total_employees: 0,
    active_tasks: 0,
    pending_leaves: 0,
    shifts_today: 0,
  });
  const [taskStatusData, setTaskStatusData] = useState([]);
  const [employeeDistributionData, setEmployeeDistributionData] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [kpisRes, taskStatusRes, employeeDistRes, activitiesRes] = await Promise.all([
          api.get('/dashboard/kpis'),
          api.get('/dashboard/charts/task-status'),
          api.get('/dashboard/charts/employee-distribution'),
          api.get('/dashboard/recent-activities'),
        ]);

        setKpis(kpisRes.data);
        setTaskStatusData(taskStatusRes.data);
        setEmployeeDistributionData(employeeDistRes.data);
        setRecentActivities(activitiesRes.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Handle card click navigation
  const handleCardClick = (cardType) => {
    switch (cardType) {
      case 'total_tasks':
        navigate('/tasks');
        break;
      case 'active_tasks':
        navigate('/tasks?filter=active');
        break;
      case 'completed_tasks':
        navigate('/tasks?filter=completed');
        break;
      case 'pending_approvals':
        navigate('/approvals');
        break;
      case 'active_teams':
        navigate('/directory'); // Fallback to directory if teams route doesn't exist
        break;
      default:
        break;
    }
  };

  // Handle activity click navigation
  const handleActivityClick = (activity) => {
    const { type, entity_id } = activity;

    // Fallback to dashboard if entity_id is missing
    if (!entity_id) {
      navigate('/dashboard');
      return;
    }

    switch (type) {
      case 'TaskCreated':
      case 'TaskUpdated':
      case 'TaskCompleted':
        navigate(`/tasks/${entity_id}`);
        break;
      case 'ApprovalRequested':
      case 'ApprovalGranted':
      case 'ApprovalRejected':
        navigate(`/approvals/${entity_id}`);
        break;
      case 'TeamJoined':
        navigate('/directory'); // Fallback to directory if teams route doesn't exist
        break;
      default:
        navigate('/dashboard'); // Fallback for unknown activity types
        break;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-3">
          <div className="w-6 h-6 border-2 border-accent-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-neutral-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-danger-50 border border-danger-200 rounded-linear shadow-linear p-6 max-w-md">
          <h3 className="text-lg font-semibold text-danger-800 mb-2">Error loading dashboard</h3>
          <p className="text-danger-600">{error}</p>
        </div>
      </div>
    );
  }

  // Check user role for role-based rendering
  const userRole = user?.role || 'Employee';

  // Employee-specific dashboard
  if (userRole === 'Employee') {
    return (
      <div className="space-y-8">
        {/* Welcome Message */}
        <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
            Welcome back, {user?.name || 'User'}!
          </h2>
          <p className="text-neutral-600">
            Here's what's happening with your tasks today.
          </p>
        </div>

        {/* Employee KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <div
            className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-accent-200 transition-all duration-200 group"
            onClick={() => handleCardClick('total_tasks')}
          >
            <div className="text-center">
              <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Total Tasks</h3>
              <p className="text-3xl font-bold text-accent-600">{kpis.total_tasks || 0}</p>
            </div>
          </div>
          <div
            className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-success-200 transition-all duration-200 group"
            onClick={() => handleCardClick('active_tasks')}
          >
            <div className="text-center">
              <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Active Tasks</h3>
              <p className="text-3xl font-bold text-success-600">{kpis.active_tasks || 0}</p>
            </div>
          </div>
          <div
            className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-primary-200 transition-all duration-200 group"
            onClick={() => handleCardClick('completed_tasks')}
          >
            <div className="text-center">
              <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Completed Tasks</h3>
              <p className="text-3xl font-bold text-primary-600">{kpis.completed_tasks || 0}</p>
            </div>
          </div>
          <div
            className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-warning-200 transition-all duration-200 group"
            onClick={() => handleCardClick('pending_approvals')}
          >
            <div className="text-center">
              <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Pending Approvals</h3>
              <p className="text-3xl font-bold text-warning-600">{kpis.pending_approvals || 0}</p>
            </div>
          </div>
          <div
            className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-accent-200 transition-all duration-200 group"
            onClick={() => handleCardClick('active_teams')}
          >
            <div className="text-center">
              <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Active Teams</h3>
              <p className="text-3xl font-bold text-accent-600">{kpis.active_teams || 0}</p>
            </div>
          </div>
        </div>

        {/* Employee Charts */}
        <div>
          <DashboardCharts />
        </div>

        {/* Recent Activities */}
        <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Recent Activities</h3>
          </div>
          <div className="space-y-4">
            {recentActivities.length > 0 ? (
              recentActivities.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 bg-neutral-50 rounded-linear cursor-pointer hover:bg-neutral-100 transition-colors duration-200 group"
                  onClick={() => handleActivityClick(activity)}
                >
                  <div className={`w-3 h-3 rounded-full mt-2 flex-shrink-0 ${
                    activity.type.includes('Task') ? 'bg-accent-500' :
                    activity.type.includes('Approval') ? 'bg-success-500' :
                    'bg-primary-500'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 group-hover:text-neutral-700">
                      {activity.title}
                    </p>
                    <p className="text-sm text-neutral-600 mt-1">
                      {activity.description}
                    </p>
                    <p className="text-xs text-neutral-500 mt-2">
                      Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <p className="text-neutral-500">
                  No recent activities to display.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Manager, CompanyAdmin, and SuperAdmin dashboard (Linear-inspired layout)
  return (
    <div className="space-y-8">
      {/* Welcome Message */}
      <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
        <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
          Welcome back, {user?.name || 'User'}!
        </h2>
        <p className="text-neutral-600">
          Here's what's happening with your workforce today.
        </p>
      </div>

      {/* Manager KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-accent-200 transition-all duration-200 group"
          onClick={() => handleCardClick('total_employees')}
        >
          <div className="text-center">
            <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Total Employees</h3>
            <p className="text-3xl font-bold text-accent-600">{kpis.total_employees || 0}</p>
          </div>
        </div>
        <div
          className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-success-200 transition-all duration-200 group"
          onClick={() => handleCardClick('active_tasks')}
        >
          <div className="text-center">
            <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Active Tasks</h3>
            <p className="text-3xl font-bold text-success-600">{kpis.active_tasks || 0}</p>
          </div>
        </div>
        <div
          className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-warning-200 transition-all duration-200 group"
          onClick={() => handleCardClick('pending_approvals')}
        >
          <div className="text-center">
            <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Pending Leaves</h3>
            <p className="text-3xl font-bold text-warning-600">{kpis.pending_leaves || 0}</p>
          </div>
        </div>
        <div
          className="bg-surface rounded-linear border border-border shadow-linear p-6 cursor-pointer hover:shadow-linear-lg hover:border-primary-200 transition-all duration-200 group"
          onClick={() => handleCardClick('team_performance')}
        >
          <div className="text-center">
            <h3 className="text-sm font-medium text-neutral-600 mb-2 group-hover:text-neutral-700">Shifts Today</h3>
            <p className="text-3xl font-bold text-primary-600">{kpis.shifts_today || 0}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Task Status Distribution</h3>
          </div>
          <div className="h-64">
            <Doughnut data={{
              labels: taskStatusData.map(item => item.name),
              datasets: [{
                data: taskStatusData.map(item => item.value),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40'],
                hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40']
              }]
            }} />
          </div>
        </div>

        <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Employee Role Distribution</h3>
          </div>
          <div className="h-64">
            <Doughnut data={{
              labels: employeeDistributionData.map(item => item.name),
              datasets: [{
                data: employeeDistributionData.map(item => item.value),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
              }]
            }} />
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-neutral-900">Recent Activities</h3>
        </div>
        <div className="space-y-4">
          {recentActivities.length > 0 ? (
            recentActivities.map((activity, index) => (
              <div
                key={index}
                className="flex items-start space-x-4 p-4 bg-neutral-50 rounded-linear cursor-pointer hover:bg-neutral-100 transition-colors duration-200 group"
                onClick={() => handleActivityClick(activity)}
              >
                <div className={`w-3 h-3 rounded-full mt-2 flex-shrink-0 ${
                  activity.type.includes('Task') ? 'bg-accent-500' :
                  activity.type.includes('Approval') ? 'bg-success-500' :
                  'bg-primary-500'
                }`}></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900 group-hover:text-neutral-700">
                    {activity.title}
                  </p>
                  <p className="text-sm text-neutral-600 mt-1">
                    {activity.description}
                  </p>
                  <p className="text-xs text-neutral-500 mt-2">
                    Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-neutral-500">
                No recent activities to display.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
