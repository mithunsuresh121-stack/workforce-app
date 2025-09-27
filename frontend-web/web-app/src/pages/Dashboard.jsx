import React, { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { useAuth, api } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import DashboardCharts from '../components/DashboardCharts';
import { theme } from '../theme';

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

  const cardStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid ${theme.colors.border}`,
    boxShadow: theme.components.card,
    padding: theme.spacing.xl,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    marginBottom: theme.spacing.md,
  };

  const cardHoverStyle = {
    boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    borderColor: theme.colors.primary,
  };

  const textCenterStyle = {
    textAlign: 'center',
  };

  const titleStyle = {
    fontSize: '1.875rem',
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.md,
  };

  const subtitleStyle = {
    color: theme.colors.textSecondary,
  };

  const kpiTitleStyle = {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: theme.colors.textSecondary,
    marginBottom: '0.5rem',
  };

  const kpiValueStyle = {
    fontSize: '2.25rem',
    fontWeight: '700',
    color: theme.colors.primary,
  };

  const activityItemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  };

  const activityTitleStyle = {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: theme.colors.textPrimary,
  };

  const activityDescriptionStyle = {
    fontSize: '0.875rem',
    color: theme.colors.textSecondary,
    marginTop: '0.25rem',
  };

  const activityMetaStyle = {
    fontSize: '0.75rem',
    color: theme.colors.neutral,
    marginTop: '0.5rem',
  };

  const chartContainerStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid ${theme.colors.border}`,
    boxShadow: theme.components.card,
    padding: theme.spacing.xl,
    height: '16rem',
  };

  const chartTitleStyle = {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.lg,
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
          <div style={{ width: '1.5rem', height: '1.5rem', border: `2px solid ${theme.colors.primary}`, borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ color: theme.colors.textSecondary, fontWeight: '500' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{ backgroundColor: '#FEF2F2', border: `1px solid ${theme.colors.danger}`, borderRadius: theme.borderRadius.lg, boxShadow: theme.components.card, padding: theme.spacing.xl, maxWidth: '28rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: theme.colors.danger, marginBottom: '0.5rem' }}>Error loading dashboard</h3>
          <p style={{ color: theme.colors.danger }}>{error}</p>
        </div>
      </div>
    );
  }

  // Check user role for role-based rendering
  const userRole = user?.role || 'Employee';

  // Employee-specific dashboard
  if (userRole === 'Employee') {
    return (
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.xl }}>
        {/* Welcome Message */}
        <div style={cardStyle}>
          <h2 style={titleStyle}>
            Welcome back, {user?.name || 'User'}!
          </h2>
          <p style={subtitleStyle}>
            Here's what's happening with your tasks today.
          </p>
        </div>

        {/* Employee KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(15rem, 1fr))', gap: theme.spacing.lg }}>
          <div
            style={{ ...cardStyle, ':hover': cardHoverStyle }}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
            onClick={() => handleCardClick('total_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Total Tasks</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.total_tasks || 0}</p>
            </div>
          </div>
          <div
            style={{ ...cardStyle, ':hover': cardHoverStyle }}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
            onClick={() => handleCardClick('active_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Active Tasks</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.success }}>{kpis.active_tasks || 0}</p>
            </div>
          </div>
          <div
            style={{ ...cardStyle, ':hover': cardHoverStyle }}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
            onClick={() => handleCardClick('completed_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Completed Tasks</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.primary }}>{kpis.completed_tasks || 0}</p>
            </div>
          </div>
          <div
            style={{ ...cardStyle, ':hover': cardHoverStyle }}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
            onClick={() => handleCardClick('pending_approvals')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Pending Approvals</h3>
              <p style={{ ...kpiValueStyle, color: '#F59E0B' }}>{kpis.pending_approvals || 0}</p>
            </div>
          </div>
          <div
            style={{ ...cardStyle, ':hover': cardHoverStyle }}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
            onClick={() => handleCardClick('active_teams')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Active Teams</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.active_teams || 0}</p>
            </div>
          </div>
        </div>

        {/* Employee Charts */}
        <div>
          <DashboardCharts />
        </div>

        {/* Recent Activities */}
        <div style={cardStyle}>
          <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={chartTitleStyle}>Recent Activities</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
            {recentActivities.length > 0 ? (
              recentActivities.map((activity, index) => (
                <div
                  key={index}
                  style={activityItemStyle}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#F3F4F6'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = theme.colors.background; }}
                  onClick={() => handleActivityClick(activity)}
                >
                  <div style={{
                    width: '0.75rem',
                    height: '0.75rem',
                    borderRadius: '50%',
                    marginTop: '0.5rem',
                    flexShrink: '0',
                    backgroundColor: activity.type.includes('Task') ? theme.colors.accent : activity.type.includes('Approval') ? theme.colors.success : theme.colors.primary
                  }}></div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={activityTitleStyle}>
                      {activity.title}
                    </p>
                    <p style={activityDescriptionStyle}>
                      {activity.description}
                    </p>
                    <p style={activityMetaStyle}>
                      Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>
                <p style={{ color: theme.colors.neutral }}>
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
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.xl }}>
      {/* Welcome Message */}
      <div style={cardStyle}>
        <h2 style={titleStyle}>
          Welcome back, {user?.name || 'User'}!
        </h2>
        <p style={subtitleStyle}>
          Here's what's happening with your workforce today.
        </p>
      </div>

      {/* Manager KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(15rem, 1fr))', gap: theme.spacing.lg }}>
        <div
          style={{ ...cardStyle, ':hover': cardHoverStyle }}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
          onClick={() => handleCardClick('total_employees')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Total Employees</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.total_employees || 0}</p>
          </div>
        </div>
        <div
          style={{ ...cardStyle, ':hover': cardHoverStyle }}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
          onClick={() => handleCardClick('active_tasks')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Active Tasks</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.success }}>{kpis.active_tasks || 0}</p>
          </div>
        </div>
        <div
          style={{ ...cardStyle, ':hover': cardHoverStyle }}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
          onClick={() => handleCardClick('pending_approvals')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Pending Leaves</h3>
            <p style={{ ...kpiValueStyle, color: '#F59E0B' }}>{kpis.pending_leaves || 0}</p>
          </div>
        </div>
        <div
          style={{ ...cardStyle, ':hover': cardHoverStyle }}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; }}
          onClick={() => handleCardClick('team_performance')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Shifts Today</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.primary }}>{kpis.shifts_today || 0}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: theme.spacing.lg }}>
        <div style={chartContainerStyle}>
          <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={chartTitleStyle}>Task Status Distribution</h3>
          </div>
          <div style={{ height: '16rem' }}>
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

        <div style={chartContainerStyle}>
          <div style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={chartTitleStyle}>Employee Role Distribution</h3>
          </div>
          <div style={{ height: '16rem' }}>
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
      <div style={cardStyle}>
        <div style={{ marginBottom: theme.spacing.lg }}>
          <h3 style={chartTitleStyle}>Recent Activities</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
          {recentActivities.length > 0 ? (
            recentActivities.map((activity, index) => (
              <div
                key={index}
                style={activityItemStyle}
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#F3F4F6'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = theme.colors.background; }}
                onClick={() => handleActivityClick(activity)}
              >
                <div style={{
                  width: '0.75rem',
                  height: '0.75rem',
                  borderRadius: '50%',
                  marginTop: '0.5rem',
                  flexShrink: '0',
                  backgroundColor: activity.type.includes('Task') ? theme.colors.accent : activity.type.includes('Approval') ? theme.colors.success : theme.colors.primary
                }}></div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={activityTitleStyle}>
                    {activity.title}
                  </p>
                  <p style={activityDescriptionStyle}>
                    {activity.description}
                  </p>
                  <p style={activityMetaStyle}>
                    Status: {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: theme.spacing.xl }}>
              <p style={{ color: theme.colors.neutral }}>
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
