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
    borderRadius: theme.borderRadius.md,
    border: `1px solid ${theme.colors.borderLight}`,
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
    padding: theme.spacing.lg,
    cursor: 'pointer',
    transition: 'all 0.15s ease-in-out',
    marginBottom: theme.spacing.sm,
  };

  const cardHoverStyle = {
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    borderColor: theme.colors.primaryLight,
    transform: 'translateY(-1px)',
  };

  const textCenterStyle = {
    textAlign: 'center',
  };

  const titleStyle = {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.sm,
    lineHeight: '1.25',
  };

  const subtitleStyle = {
    color: theme.colors.textSecondary,
    fontSize: '0.875rem',
    lineHeight: '1.4',
  };

  const kpiTitleStyle = {
    fontSize: '0.75rem',
    fontWeight: '500',
    color: theme.colors.textMuted,
    marginBottom: '0.25rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const kpiValueStyle = {
    fontSize: '2rem',
    fontWeight: '700',
    color: theme.colors.primary,
    lineHeight: '1.1',
  };

  const activityItemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.sm,
    cursor: 'pointer',
    transition: 'all 0.15s ease-in-out',
    borderLeft: `3px solid ${theme.colors.borderLight}`,
  };

  const activityTitleStyle = {
    fontSize: '0.875rem',
    fontWeight: '600',
    color: theme.colors.textPrimary,
    lineHeight: '1.3',
  };

  const activityDescriptionStyle = {
    fontSize: '0.875rem',
    color: theme.colors.textSecondary,
    marginTop: '0.125rem',
    lineHeight: '1.4',
  };

  const activityMetaStyle = {
    fontSize: '0.75rem',
    color: theme.colors.textMuted,
    marginTop: '0.5rem',
    fontWeight: '400',
  };

  const chartContainerStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    border: `1px solid ${theme.colors.borderLight}`,
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
    padding: theme.spacing.lg,
    height: 'auto',
    minHeight: '16rem',
  };

  const chartTitleStyle = {
    fontSize: '1rem',
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.md,
    lineHeight: '1.25',
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: theme.spacing.xl }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md, backgroundColor: theme.colors.surface, padding: theme.spacing.lg, borderRadius: theme.borderRadius.md, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)' }}>
          <div style={{ width: '1.25rem', height: '1.25rem', border: `2px solid ${theme.colors.primaryLight}`, borderTopColor: theme.colors.primary, borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ color: theme.colors.textSecondary, fontWeight: '500', margin: 0 }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: theme.spacing.xl }}>
        <div style={{ backgroundColor: theme.colors.dangerLight, border: `1px solid ${theme.colors.dangerLight}`, borderRadius: theme.borderRadius.md, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)', padding: theme.spacing.lg, maxWidth: '28rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: theme.colors.danger, marginBottom: theme.spacing.sm, lineHeight: '1.25' }}>Error loading dashboard</h3>
          <p style={{ color: theme.colors.textSecondary, margin: 0, lineHeight: '1.4' }}>{error}</p>
        </div>
      </div>
    );
  }

  // Check user role for role-based rendering
  const userRole = user?.role || 'Employee';

  // Employee-specific dashboard (Linear-inspired: minimal cards, subtle interactions)
  if (userRole === 'Employee') {
    return (
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
        {/* Welcome Message */}
        <div style={cardStyle}>
          <h2 style={titleStyle}>
            Welcome back, {user?.full_name || 'User'}!
          </h2>
          <p style={subtitleStyle}>
            Here's what's happening with your tasks today.
          </p>
        </div>

        {/* Employee KPI Cards - Compact grid for focus */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(12rem, 1fr))', gap: theme.spacing.md }}>
          <div
            style={cardStyle}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
            onClick={() => handleCardClick('total_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Total Tasks</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.total_tasks || 0}</p>
            </div>
          </div>
          <div
            style={cardStyle}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
            onClick={() => handleCardClick('active_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Active Tasks</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.success }}>{kpis.active_tasks || 0}</p>
            </div>
          </div>
          <div
            style={cardStyle}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
            onClick={() => handleCardClick('completed_tasks')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Completed</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.primary }}>{kpis.completed_tasks || 0}</p>
            </div>
          </div>
          <div
            style={cardStyle}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
            onClick={() => handleCardClick('pending_approvals')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Pending</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.warning }}>{kpis.pending_approvals || 0}</p>
            </div>
          </div>
          <div
            style={cardStyle}
            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
            onClick={() => handleCardClick('active_teams')}
          >
            <div style={textCenterStyle}>
              <h3 style={kpiTitleStyle}>Teams</h3>
              <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.active_teams || 0}</p>
            </div>
          </div>
        </div>

        {/* Employee Charts - Integrated for minimalism */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: theme.spacing.md }}>
          <DashboardCharts />
        </div>

        {/* Recent Activities - List-like for Linear feel */}
        <div style={cardStyle}>
          <div style={{ marginBottom: theme.spacing.md }}>
            <h3 style={chartTitleStyle}>Recent Activities</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.sm }}>
            {recentActivities.length > 0 ? (
              recentActivities.map((activity, index) => (
                <div
                  key={index}
                  style={activityItemStyle}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = theme.colors.surfaceHover; e.currentTarget.style.borderLeftColor = theme.colors.primaryLight; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = theme.colors.background; e.currentTarget.style.borderLeftColor = theme.colors.borderLight; }}
                  onClick={() => handleActivityClick(activity)}
                >
                  <div style={{
                    width: '0.5rem',
                    height: '0.5rem',
                    borderRadius: '50%',
                    marginTop: '0.625rem',
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
                      {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: theme.spacing.lg }}>
                <p style={{ color: theme.colors.textMuted, fontSize: '0.875rem' }}>
                  No recent activities to display.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Manager, CompanyAdmin, and SuperAdmin dashboard (Enhanced Linear-inspired: clean, focused, minimal)
  return (
    <div style={{ maxWidth: '80rem', margin: '0 auto', padding: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Welcome Message */}
      <div style={cardStyle}>
        <h2 style={titleStyle}>
          Welcome back, {user?.full_name || 'User'}!
        </h2>
        <p style={subtitleStyle}>
          Here's what's happening with your workforce today.
        </p>
      </div>

      {/* Manager KPI Cards - Compact for overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(12rem, 1fr))', gap: theme.spacing.md }}>
        <div
          style={cardStyle}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
          onClick={() => handleCardClick('total_employees')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Employees</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.accent }}>{kpis.total_employees || 0}</p>
          </div>
        </div>
        <div
          style={cardStyle}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
          onClick={() => handleCardClick('active_tasks')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Active Tasks</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.success }}>{kpis.active_tasks || 0}</p>
          </div>
        </div>
        <div
          style={cardStyle}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
          onClick={() => handleCardClick('pending_approvals')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Pending Leaves</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.warning }}>{kpis.pending_leaves || 0}</p>
          </div>
        </div>
        <div
          style={cardStyle}
          onMouseEnter={(e) => { e.currentTarget.style.boxShadow = cardHoverStyle.boxShadow; e.currentTarget.style.borderColor = cardHoverStyle.borderColor; e.currentTarget.style.transform = cardHoverStyle.transform; }}
          onMouseLeave={(e) => { e.currentTarget.style.boxShadow = cardStyle.boxShadow; e.currentTarget.style.borderColor = cardStyle.border; e.currentTarget.style.transform = 'none'; }}
          onClick={() => handleCardClick('team_performance')}
        >
          <div style={textCenterStyle}>
            <h3 style={kpiTitleStyle}>Shifts Today</h3>
            <p style={{ ...kpiValueStyle, color: theme.colors.primary }}>{kpis.shifts_today || 0}</p>
          </div>
        </div>
      </div>

      {/* Charts - Side-by-side for efficiency, minimal padding */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing.md }}>
        <div style={chartContainerStyle}>
          <div style={{ marginBottom: theme.spacing.md }}>
            <h3 style={chartTitleStyle}>Task Status</h3>
          </div>
          <div style={{ height: '14rem' }}>
            <Doughnut data={{
              labels: taskStatusData.map(item => item.name),
              datasets: [{
                data: taskStatusData.map(item => item.value),
                backgroundColor: ['#EF4444', '#3B82F6', '#F59E0B', '#10B981'],
                hoverBackgroundColor: ['#EF4444', '#3B82F6', '#F59E0B', '#10B981'],
                borderWidth: 0,
              }]
            }} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>

        <div style={chartContainerStyle}>
          <div style={{ marginBottom: theme.spacing.md }}>
            <h3 style={chartTitleStyle}>Employee Roles</h3>
          </div>
          <div style={{ height: '14rem' }}>
            <Doughnut data={{
              labels: employeeDistributionData.map(item => item.name),
              datasets: [{
                data: employeeDistributionData.map(item => item.value),
                backgroundColor: ['#EF4444', '#3B82F6', '#F59E0B', '#10B981'],
                hoverBackgroundColor: ['#EF4444', '#3B82F6', '#F59E0B', '#10B981'],
                borderWidth: 0,
              }]
            }} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div style={cardStyle}>
        <div style={{ marginBottom: theme.spacing.md }}>
          <h3 style={chartTitleStyle}>Recent Activities</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.sm }}>
          {recentActivities.length > 0 ? (
            recentActivities.map((activity, index) => (
              <div
                key={index}
                style={activityItemStyle}
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = theme.colors.surfaceHover; e.currentTarget.style.borderLeftColor = theme.colors.primaryLight; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = theme.colors.background; e.currentTarget.style.borderLeftColor = theme.colors.borderLight; }}
                onClick={() => handleActivityClick(activity)}
              >
                <div style={{
                  width: '0.5rem',
                  height: '0.5rem',
                  borderRadius: '50%',
                  marginTop: '0.625rem',
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
                    {activity.status} • {new Date(activity.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: theme.spacing.lg }}>
              <p style={{ color: theme.colors.textMuted, fontSize: '0.875rem' }}>
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
