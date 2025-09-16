import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Card, CardBody, Typography, CardHeader, Spinner } from '@material-tailwind/react';
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
        <Spinner className="h-8 w-8" />
        <div className="ml-2">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <Typography variant="h5">Error loading dashboard</Typography>
          <Typography variant="body1">{error}</Typography>
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
        <Card>
          <CardBody>
            <Typography variant="h5" color="blue-gray">Total Employees</Typography>
            <Typography variant="h3" color="blue">{kpis.total_employees}</Typography>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Typography variant="h5" color="blue-gray">Active Tasks</Typography>
            <Typography variant="h3" color="green">{kpis.active_tasks}</Typography>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Typography variant="h5" color="blue-gray">Pending Leaves</Typography>
            <Typography variant="h3" color="orange">{kpis.pending_leaves}</Typography>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Typography variant="h5" color="blue-gray">Shifts Today</Typography>
            <Typography variant="h3" color="purple">{kpis.shifts_today}</Typography>
          </CardBody>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader floated={false} shadow={false} color="transparent">
            <Typography variant="h5" color="blue-gray">Task Status Distribution</Typography>
          </CardHeader>
          <CardBody>
            <Doughnut data={taskStatusChartData} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader floated={false} shadow={false} color="transparent">
            <Typography variant="h5" color="blue-gray">Employee Role Distribution</Typography>
          </CardHeader>
          <CardBody>
            <Doughnut data={employeeDistributionChartData} />
          </CardBody>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card>
        <CardHeader floated={false} shadow={false} color="transparent">
          <Typography variant="h5" color="blue-gray">Recent Activities</Typography>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-3 h-3 rounded-full mt-1 ${activity.type === 'task' ? 'bg-blue-500' : 'bg-green-500'
                  }`}></div>
                <div className="flex-1">
                  <Typography variant="small" color="blue-gray" className="font-medium">
                    {activity.title}
                  </Typography>
                  <Typography variant="small" color="gray">
                    {activity.description}
                  </Typography>
                  <Typography variant="small" color="gray">
                    Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                  </Typography>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default Dashboard;
