import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Card, CardBody, Typography, CardHeader, Spinner } from '@material-tailwind/react';
import { useAuth } from '../contexts/AuthContext';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard = () => {
  const { user } = useAuth();
  const [kpis, setKpis] = useState({ total_employees: 0, active_tasks: 0, pending_leaves: 0, shifts_today: 0 });
  const [taskStatusData, setTaskStatusData] = useState([]);
  const [employeeDistributionData, setEmployeeDistributionData] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        // Fetch KPIs
        const kpisResponse = await axios.get('/api/dashboard/kpis');
        setKpis(kpisResponse.data);

        // Fetch task status chart data
        const taskStatusResponse = await axios.get('/api/dashboard/charts/task-status');
        setTaskStatusData(taskStatusResponse.data);

        // Fetch employee distribution chart data
        const employeeDistResponse = await axios.get('/api/dashboard/charts/employee-distribution');
        setEmployeeDistributionData(employeeDistResponse.data);

        // Fetch recent activities
        const activitiesResponse = await axios.get('/api/dashboard/recent-activities?limit=5');
        setRecentActivities(activitiesResponse.data);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Fallback dummy data for development
        setKpis({ total_employees: 150, active_tasks: 45, pending_leaves: 12, shifts_today: 8 });
        setTaskStatusData([
          { name: 'Pending', value: 10 },
          { name: 'In Progress', value: 25 },
          { name: 'Completed', value: 30 },
          { name: 'Overdue', value: 5 }
        ]);
        setEmployeeDistributionData([
          { name: 'Super Admin', value: 1 },
          { name: 'Company Admin', value: 2 },
          { name: 'Manager', value: 5 },
          { name: 'Employee', value: 142 }
        ]);
        setRecentActivities([
          { type: 'task', title: 'Complete project documentation', description: 'Finish writing the API docs', status: 'completed', timestamp: new Date().toISOString() },
          { type: 'leave', title: 'Annual leave request', description: 'John Doe requested 3 days leave', status: 'pending', timestamp: new Date().toISOString() },
          { type: 'task', title: 'Review code changes', description: 'PR #123 needs review', status: 'in_progress', timestamp: new Date().toISOString() },
          { type: 'leave', title: 'Sick leave approval', description: 'Jane Smith approved sick leave', status: 'approved', timestamp: new Date().toISOString() },
          { type: 'task', title: 'Update database schema', description: 'Add new fields to employee table', status: 'pending', timestamp: new Date().toISOString() }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Message */}
      <div className="mb-6">
        <Typography variant="h3" color="blue-gray" className="mb-2">
          Welcome back, {user?.name || 'User'}!
        </Typography>
        <Typography variant="lead" color="gray">
          Here's what's happening with your workforce today.
        </Typography>
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
                <div className={`w-3 h-3 rounded-full mt-1 ${
                  activity.type === 'task' ? 'bg-blue-500' : 'bg-green-500'
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
