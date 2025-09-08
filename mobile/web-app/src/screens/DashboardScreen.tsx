import React, { useEffect, useState } from 'react';
import { fetchDashboardData } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getAuthToken } from '../utils/auth';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Alert, { AlertDescription, AlertTitle } from '../components/ui/Alert';
import Skeleton from '../components/ui/skeleton';
import { Edit, Save, X, TrendingUp, TrendingDown, Users, Calendar, FileText, Clock } from 'lucide-react';

const DashboardScreen: React.FC = () => {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState<any>(null);
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingKpi, setEditingKpi] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  useEffect(() => {
    const authToken = getAuthToken();
    if (!authToken) {
      navigate('/login');
      return;
    }

    const getDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchDashboardData();
        if (response) {
          setKpis(response.kpis);
          setActivities(response.activities);
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    getDashboardData();
  }, [navigate]);

  const handleEditKpi = (kpiKey: string, currentValue: number) => {
    setEditingKpi(kpiKey);
    setEditValue(currentValue.toString());
  };

  const handleSaveKpi = async (kpiKey: string) => {
    try {
      // Here you would call an API to update the KPI
      // For now, we'll just update locally
      setKpis((prev: any) => ({
        ...prev,
        [kpiKey]: parseInt(editValue)
      }));
      setEditingKpi(null);
    } catch (error) {
      console.error('Failed to update KPI:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditingKpi(null);
    setEditValue('');
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else if (trend < 0) {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <Skeleton className="h-10 w-32" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((item) => (
            <Card key={item} className="kpi-card">
              <CardHeader className="pb-2">
                <Skeleton className="h-6 w-3/4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-1/2" />
                <Skeleton className="h-4 w-3/4 mt-2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const kpiCards = [
    {
      key: 'total_employees',
      title: 'Total Employees',
      value: kpis?.total_employees || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      trend: 12
    },
    {
      key: 'active_tasks',
      title: 'Active Tasks',
      value: kpis?.active_tasks || 0,
      icon: Calendar,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      trend: -3
    },
    {
      key: 'pending_leaves',
      title: 'Pending Leave Requests',
      value: kpis?.pending_leaves || 0,
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      trend: 5
    },
    {
      key: 'shifts_today',
      title: 'Shifts Today',
      value: kpis?.shifts_today || 0,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      trend: 2
    }
  ];

  const chartData = [
    { name: 'Completed', value: kpis?.taskStatus?.[0]?.value || 25, color: '#10B981' },
    { name: 'In Progress', value: kpis?.taskStatus?.[1]?.value || 15, color: '#F59E0B' },
    { name: 'Pending', value: kpis?.taskStatus?.[2]?.value || 10, color: '#EF4444' }
  ];

  const performanceData = [
    { month: 'Jan', productivity: 85, attendance: 92 },
    { month: 'Feb', productivity: 78, attendance: 88 },
    { month: 'Mar', productivity: 92, attendance: 95 },
    { month: 'Apr', productivity: 88, attendance: 90 },
    { month: 'May', productivity: 95, attendance: 93 },
    { month: 'Jun', productivity: 82, attendance: 87 }
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's what's happening today.</p>
        </div>
        <div className="flex items-center space-x-4">
          <select className="input-field py-2 px-3">
            <option>Today</option>
            <option>This Week</option>
            <option>This Month</option>
            <option>This Quarter</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.key} className="kpi-card group">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {kpi.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${kpi.bgColor}`}>
                  <Icon className={`h-4 w-4 ${kpi.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-baseline space-x-2">
                    {editingKpi === kpi.key ? (
                      <input
                        type="number"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="text-2xl font-bold w-20 border border-gray-300 rounded px-2 py-1"
                        autoFocus
                      />
                    ) : (
                      <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
                    )}
                    <div className="flex items-center text-sm text-gray-500">
                      {getTrendIcon(kpi.trend)}
                      <span className={`ml-1 ${kpi.trend > 0 ? 'text-green-600' : kpi.trend < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                        {Math.abs(kpi.trend)}%
                      </span>
                    </div>
                  </div>
                  {editingKpi === kpi.key ? (
                    <div className="flex space-x-1">
                      <button
                        onClick={() => handleSaveKpi(kpi.key)}
                        className="p-1 text-green-600 hover:text-green-700"
                      >
                        <Save className="h-4 w-4" />
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="p-1 text-red-600 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleEditKpi(kpi.key, kpi.value)}
                      className="p-1 text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">vs. previous period</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts and Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Status Chart */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle>Task Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Performance Chart */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle>Team Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="productivity" fill="#3B82F6" name="Productivity (%)" />
                  <Bar dataKey="attendance" fill="#10B981" name="Attendance (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {activities.length > 0 ? (
              activities.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <p className="text-sm text-gray-700">{activity.description}</p>
                  <span className="text-xs text-gray-400 ml-auto">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No recent activities</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardScreen;
