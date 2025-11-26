import { useState, useEffect, useCallback } from 'react';

const METRICS_ENDPOINT = '/metrics';
const POLL_INTERVAL = 5000; // 5 seconds

// Parse Prometheus metrics format
const parsePrometheusMetrics = (text) => {
  const lines = text.split('\n');
  const metrics = {};

  for (const line of lines) {
    if (line.startsWith('#') || line.trim() === '') continue;

    // Match metric lines like: workforce_messages_sent_total 42
    const match = line.match(/^(\w+)\s+([\d.]+)$/);
    if (match) {
      const [, name, value] = match;
      metrics[name] = parseFloat(value);
    }
  }

  return metrics;
};

// Determine alert level based on metric values
const getAlertLevel = (metricName, value) => {
  switch (metricName) {
    case 'workforce_messages_sent_total':
      return value > 1000 ? 'critical' : value > 500 ? 'warning' : 'normal';
    case 'workforce_meetings_joined_total':
      return value > 100 ? 'critical' : value > 50 ? 'warning' : 'normal';
    case 'redis_pubsub_messages_total':
      return value > 10000 ? 'critical' : value > 5000 ? 'warning' : 'normal';
    case 'redis_pubsub_subscribers_active':
      return value === 0 ? 'critical' : value < 5 ? 'warning' : 'normal';
    default:
      return 'normal';
  }
};

export default function useMetrics() {
  const [metrics, setMetrics] = useState({
    workforce_messages_sent_total: 0,
    workforce_meetings_joined_total: 0,
    redis_pubsub_messages_total: 0,
    redis_pubsub_subscribers_active: 0,
  });
  const [alerts, setAlerts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch(METRICS_ENDPOINT);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const text = await response.text();
      const parsedMetrics = parsePrometheusMetrics(text);

      // Update metrics state
      const newMetrics = {
        workforce_messages_sent_total: parsedMetrics.workforce_messages_sent_total || 0,
        workforce_meetings_joined_total: parsedMetrics.workforce_meetings_joined_total || 0,
        redis_pubsub_messages_total: parsedMetrics.redis_pubsub_messages_total || 0,
        redis_pubsub_subscribers_active: parsedMetrics.redis_pubsub_subscribers_active || 0,
      };

      setMetrics(newMetrics);

      // Calculate alerts
      const newAlerts = {};
      Object.entries(newMetrics).forEach(([key, value]) => {
        newAlerts[key] = getAlertLevel(key, value);
      });
      setAlerts(newAlerts);

      setError(null);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching metrics:', err);
      setError(err.message);

      // Set fallback values when metrics are unavailable
      setMetrics({
        workforce_messages_sent_total: 0,
        workforce_meetings_joined_total: 0,
        redis_pubsub_messages_total: 0,
        redis_pubsub_subscribers_active: 0,
      });

      setAlerts({
        workforce_messages_sent_total: 'critical',
        workforce_meetings_joined_total: 'critical',
        redis_pubsub_messages_total: 'critical',
        redis_pubsub_subscribers_active: 'critical',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchMetrics();

    // Set up polling
    const interval = setInterval(fetchMetrics, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchMetrics]);

  return {
    metrics,
    alerts,
    loading,
    error,
    lastUpdate,
    refetch: fetchMetrics,
  };
}
