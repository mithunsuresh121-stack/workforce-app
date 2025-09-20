import React, { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { useAuth, api } from '../contexts/AuthContext';
import { Card, CardBody, Typography, Spinner, Alert } from '@material-tailwind/react';

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner className="h-8 w-8" />
        <Typography variant="small" className="ml-2">Loading dashboard...</Typography>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Alert color="red" className="max-w-md">
          <Typography variant="h5" className="mb-2">Error loading dashboard</Typography>
          <Typography variant="small">{error}</Typography>
        </Alert>
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
    <div className="p-4">
        {/* Welcome Message */}
        <div className="mb-6">
          <Typography variant="h3" color="blue-gray" className="mb-2">
            Welcome back, {user?.name || 'User'}!
          </Typography>
          <Typography variant="small" color="gray">
            Here's what's happening with your workforce today.
          </Typography>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-2">Total Employees</Typography>
              <Typography variant="h3" color="blue">{kpis.total_employees}</Typography>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-2">Active Tasks</Typography>
              <Typography variant="h3" color="green">{kpis.active_tasks}</Typography>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-2">Pending Leaves</Typography>
              <Typography variant="h3" color="orange">{kpis.pending_leaves}</Typography>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Typography variant="h5" color="blue-gray" className="mb-2">Shifts Today</Typography>
              <Typography variant="h3" color="purple">{kpis.shifts_today}</Typography>
            </CardBody>
          </Card>
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
