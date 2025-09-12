import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [stats, setStats] = useState({ users: 0, tasks: 0, leaves: 0 });

  useEffect(() => {
    // Replace with your API endpoint
    axios.get('/api/dashboard-stats').then(res => setStats(res.data)).catch(() => {
      // Fallback dummy data
      setStats({ users: 150, tasks: 45, leaves: 12 });
    });
  }, []);

  const data = {
    labels: ['Users', 'Tasks', 'Leaves'],
    datasets: [{
      label: 'Count',
      data: [stats.users, stats.tasks, stats.leaves],
      backgroundColor: ['rgba(59, 130, 246, 0.5)', 'rgba(16, 185, 129, 0.5)', 'rgba(245, 158, 11, 0.5)'],
    }],
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-800">Total Users</h2>
          <p className="text-3xl font-bold text-blue-600">{stats.users}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-800">Active Tasks</h2>
          <p className="text-3xl font-bold text-green-600">{stats.tasks}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-800">Pending Leaves</h2>
          <p className="text-3xl font-bold text-yellow-600">{stats.leaves}</p>
        </div>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Statistics Chart</h2>
        <Bar data={data} />
      </div>
    </div>
  );
};

export default Dashboard;
