import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import useMetrics from '../hooks/useMetrics';

const MetricsPanel = () => {
  const { metrics, alerts, loading, error, lastUpdate } = useMetrics();

  // Mock historical data for sparklines (in real implementation, you'd track history)
  const [history, setHistory] = React.useState([]);

  React.useEffect(() => {
    if (lastUpdate && !loading) {
      setHistory(prev => {
        const newEntry = {
          timestamp: lastUpdate.getTime(),
          messages: metrics.workforce_messages_sent_total,
          meetings: metrics.workforce_meetings_joined_total,
          redisMessages: metrics.redis_pubsub_messages_total,
          redisSubs: metrics.redis_pubsub_subscribers_active,
        };

        // Keep only last 20 data points for sparkline
        const updated = [...prev, newEntry].slice(-20);
        return updated;
      });
    }
  }, [metrics, lastUpdate, loading]);

  const getAlertColor = (alertLevel) => {
    switch (alertLevel) {
      case 'critical': return 'border-danger-500 bg-danger-50';
      case 'warning': return 'border-warning-500 bg-warning-50';
      case 'normal': return 'border-success-500 bg-success-50';
      default: return 'border-neutral-300 bg-neutral-50';
    }
  };

  const getAlertTextColor = (alertLevel) => {
    switch (alertLevel) {
      case 'critical': return 'text-danger-700';
      case 'warning': return 'text-warning-700';
      case 'normal': return 'text-success-700';
      default: return 'text-neutral-700';
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const MetricCard = ({ title, value, alertLevel, icon, description }) => (
    <div className={`rounded-linear border-2 p-4 transition-all duration-200 ${getAlertColor(alertLevel)}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{icon}</span>
          <h3 className={`font-semibold ${getAlertTextColor(alertLevel)}`}>{title}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${
          alertLevel === 'critical' ? 'bg-danger-500' :
          alertLevel === 'warning' ? 'bg-warning-500' : 'bg-success-500'
        }`}></div>
      </div>

      <div className="mb-2">
        <p className={`text-2xl font-bold ${getAlertTextColor(alertLevel)}`}>
          {formatNumber(value)}
        </p>
        <p className="text-sm text-neutral-600">{description}</p>
      </div>

      {/* Mini sparkline */}
      <div className="h-8">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history}>
            <Line
              type="monotone"
              dataKey={title.toLowerCase().replace(/\s+/g, '')}
              stroke={alertLevel === 'critical' ? '#EF4444' : alertLevel === 'warning' ? '#F59E0B' : '#10B981'}
              strokeWidth={1}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  if (loading && history.length === 0) {
    return (
      <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 border-2 border-accent-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-neutral-600 font-medium">Loading metrics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && history.length === 0) {
    return (
      <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
        <div className="text-center py-8">
          <div className="text-danger-500 mb-2">
            <span className="text-2xl">⚠️</span>
          </div>
          <h3 className="text-lg font-semibold text-danger-800 mb-2">Metrics Unavailable</h3>
          <p className="text-danger-600">{error}</p>
          <p className="text-sm text-neutral-600 mt-2">
            Real-time metrics will be available once the backend is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-linear border border-border shadow-linear p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900">Real-time Metrics</h2>
          <p className="text-sm text-neutral-600">
            Live workforce activity monitoring
            {lastUpdate && (
              <span className="ml-2 text-xs">
                • Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        {error && (
          <div className="flex items-center space-x-2 text-warning-600">
            <span className="text-sm">⚠️ Using cached data</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Messages Sent"
          value={metrics.workforce_messages_sent_total}
          alertLevel={alerts.workforce_messages_sent_total}
          icon="💬"
          description="Total chat messages"
        />

        <MetricCard
          title="Meetings Joined"
          value={metrics.workforce_meetings_joined_total}
          alertLevel={alerts.workforce_meetings_joined_total}
          icon="👥"
          description="Total meeting participants"
        />

        <MetricCard
          title="Redis Messages"
          value={metrics.redis_pubsub_messages_total}
          alertLevel={alerts.redis_pubsub_messages_total}
          icon="📡"
          description="Pub/sub message volume"
        />

        <MetricCard
          title="Active Subscribers"
          value={metrics.redis_pubsub_subscribers_active}
          alertLevel={alerts.redis_pubsub_subscribers_active}
          icon="🔗"
          description="Redis pub/sub connections"
        />
      </div>

      {/* Alert Summary */}
      <div className="mt-6 p-4 bg-neutral-50 rounded-linear">
        <h4 className="font-medium text-neutral-900 mb-2">System Status</h4>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="text-neutral-700">
              Normal: {Object.values(alerts).filter(a => a === 'normal').length} metrics
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
            <span className="text-neutral-700">
              Warning: {Object.values(alerts).filter(a => a === 'warning').length} metrics
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-danger-500 rounded-full"></div>
            <span className="text-neutral-700">
              Critical: {Object.values(alerts).filter(a => a === 'critical').length} metrics
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;
