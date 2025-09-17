import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { useAuth } from '../contexts/AuthContext';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard = () => {
  const { user } = useAuth();
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
          axios.get('/api/dashboard/kpis'),
          axios.get('/api/dashboard/charts/task-status'),
          axios.get('/api/dashboard/charts/employee-distribution'),
          axios.get('/api/dashboard/recent-activities'),
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <div className="ml-2">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <h5 className="text-xl font-semibold mb-2">Error loading dashboard</h5>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const taskStatusChartData = {
    labels: taskStatusData.map(item => item.name),
    datasets: [{
      data: taskStatusData.map(item => item.value),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40']
    }]
  };

  const employeeDistributionChartData = {
    labels: employeeDistributionData.map(item => item.name),
    datasets: [{
      data: employeeDistributionData.map(item => item.value),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
    }]
  };

  return (
    <div className="space-y-6">
      {/* Welcome Message */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2">
          Welcome back, {user?.name || 'User'}!
        </h3>
        <p className="text-gray-600">
          Here's what's happening with your workforce today.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h5 className="text-lg font-semibold text-gray-700 mb-2">Total Employees</h5>
          <p className="text-3xl font-bold text-blue-600">{kpis.total_employees}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h5 className="text-lg font-semibold text-gray-700 mb-2">Active Tasks</h5>
          <p className="text-3xl font-bold text-green-600">{kpis.active_tasks}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h5 className="text-lg font-semibold text-gray-700 mb-2">Pending Leaves</h5>
          <p className="text-3xl font-bold text-orange-600">{kpis.pending_leaves}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h5 className="text-lg font-semibold text-gray-700 mb-2">Shifts Today</h5>
          <p className="text-3xl font-bold text-purple-600">{kpis.shifts_today}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="mb-4">
            <h5 className="text-lg font-semibold text-gray-700">Task Status Distribution</h5>
          </div>
          <div className="h-64">
            <Doughnut data={taskStatusChartData} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="mb-4">
            <h5 className="text-lg font-semibold text-gray-700">Employee Role Distribution</h5>
          </div>
          <div className="h-64">
            <Doughnut data={employeeDistributionChartData} />
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white p-6 rounded-lg shadow-md border">
        <div className="mb-4">
          <h5 className="text-lg font-semibold text-gray-700">Recent Activities</h5>
        </div>
        <div className="space-y-4">
          {recentActivities.map((activity, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-3 h-3 rounded-full mt-1 ${activity.type === 'task' ? 'bg-blue-500' : 'bg-green-500'
                }`}></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">
                  {activity.title}
                </p>
                <p className="text-sm text-gray-600">
                  {activity.description}
                </p>
                <p className="text-sm text-gray-500">
                  Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
