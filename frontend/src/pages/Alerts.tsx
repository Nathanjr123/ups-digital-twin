/**
 * Alerts Page
 * View and manage system alerts with expandable diagnostic details
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { alertService } from '@/services/api';
import type { Alert, AlertStats } from '@/types/alert';
import { AlertCircle, CheckCircle, Clock, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { formatTimeAgo, formatAlertType } from '@/utils/formatters';

export function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'acknowledged' | 'resolved'>('all');
  const [severityFilter, setSeverityFilter] = useState<'all' | 'critical' | 'high' | 'warning'>('all');
  const [expandedAlert, setExpandedAlert] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const params: any = { limit: 50 };
        if (filter !== 'all') params.status = filter;
        if (severityFilter !== 'all') params.severity = severityFilter;
        const response = await alertService.getAlerts(params);
        setAlerts(response.data.alerts);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, [filter, severityFilter]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await alertService.getAlertStats();
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching alert stats:', error);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await alertService.updateAlert(alertId, { status: 'acknowledged', acknowledged_by: 'user' });
      const response = await alertService.getAlerts({ limit: 50 });
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await alertService.updateAlert(alertId, { status: 'resolved', resolved_by: 'user' });
      const response = await alertService.getAlerts({ limit: 50 });
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage system alerts — click any alert to see triggering metrics
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Alerts</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stats.total_alerts}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-gray-400" />
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active</p>
                  <p className="mt-2 text-3xl font-bold text-danger-600">{stats.active_alerts}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-danger-500" />
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Acknowledged</p>
                  <p className="mt-2 text-3xl font-bold text-warning-600">{stats.acknowledged_alerts}</p>
                </div>
                <Clock className="w-8 h-8 text-warning-500" />
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Resolved</p>
                  <p className="mt-2 text-3xl font-bold text-success-600">{stats.resolved_alerts}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-success-500" />
              </div>
            </Card>
          </div>
        )}

        {/* Per-UPS Alert Breakdown */}
        {stats && Object.keys(stats.alerts_by_ups).length > 0 && (
          <Card className="mb-8">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Alerts by Equipment</h3>
            <div className="flex flex-wrap gap-2">
              {Object.entries(stats.alerts_by_ups)
                .sort(([, a], [, b]) => b - a)
                .map(([upsId, count]) => (
                  <Link
                    key={upsId}
                    to={`/ups/${upsId}`}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors hover:shadow-sm ${
                      count >= 5 ? 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' :
                      count >= 3 ? 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100' :
                      'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    {upsId}
                    <span className="bg-white rounded-full px-1.5 py-0.5 text-[10px] font-bold">{count}</span>
                  </Link>
                ))}
            </div>
          </Card>
        )}

        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex space-x-2">
            {([
              { key: 'all', label: 'All', color: 'bg-primary-600' },
              { key: 'active', label: 'Active', color: 'bg-danger-600' },
              { key: 'acknowledged', label: 'Acknowledged', color: 'bg-warning-600' },
              { key: 'resolved', label: 'Resolved', color: 'bg-success-600' },
            ] as const).map(f => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  filter === f.key ? `${f.color} text-white` : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div className="flex space-x-2">
            {([
              { key: 'all', label: 'All Severity', color: 'bg-gray-600' },
              { key: 'critical', label: 'Critical', color: 'bg-danger-600' },
              { key: 'high', label: 'High', color: 'bg-orange-600' },
              { key: 'warning', label: 'Warning', color: 'bg-warning-600' },
            ] as const).map(f => (
              <button
                key={f.key}
                onClick={() => setSeverityFilter(f.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  severityFilter === f.key ? `${f.color} text-white` : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Alerts List */}
        <Card>
          <div className="space-y-4">
            {alerts.length > 0 ? (
              alerts.map((alert) => {
                const isExpanded = expandedAlert === alert.alert_id;
                const hasMetrics = alert.related_metrics && Object.keys(alert.related_metrics).length > 0;

                return (
                  <div
                    key={alert.alert_id}
                    className="border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-colors"
                  >
                    {/* Alert Header */}
                    <div
                      onClick={() => setExpandedAlert(isExpanded ? null : alert.alert_id)}
                      className="p-4 cursor-pointer hover:bg-gray-50"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <StatusBadge status={alert.severity} type="severity" />
                            <StatusBadge status={alert.status} type="custom" />
                            <Link
                              to={`/ups/${alert.ups_id}`}
                              onClick={e => e.stopPropagation()}
                              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                            >
                              {alert.ups_id} <ExternalLink className="w-3 h-3" />
                            </Link>
                          </div>

                          <h3 className="text-base font-semibold text-gray-900 mb-1">
                            {formatAlertType(alert.alert_type)}
                          </h3>
                          <p className="text-sm text-gray-700 mb-1">{alert.message}</p>
                          <p className="text-xs text-gray-500">{formatTimeAgo(alert.timestamp)}</p>
                        </div>

                        <div className="ml-4 flex items-center gap-3">
                          <div className="flex flex-col space-y-2">
                            {alert.status === 'active' && (
                              <button
                                onClick={(e) => { e.stopPropagation(); handleAcknowledge(alert.alert_id); }}
                                className="px-3 py-1 text-sm bg-warning-600 text-white rounded hover:bg-warning-700"
                              >
                                Acknowledge
                              </button>
                            )}
                            {alert.status === 'acknowledged' && (
                              <button
                                onClick={(e) => { e.stopPropagation(); handleResolve(alert.alert_id); }}
                                className="px-3 py-1 text-sm bg-success-600 text-white rounded hover:bg-success-700"
                              >
                                Resolve
                              </button>
                            )}
                          </div>
                          {hasMetrics ? (
                            isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />
                          ) : null}
                        </div>
                      </div>
                    </div>

                    {/* Expanded: Related Metrics & Details */}
                    {isExpanded && (
                      <div className="bg-gray-50 border-t border-gray-200 px-4 py-4 space-y-3">
                        {alert.details && (
                          <div>
                            <p className="text-xs font-semibold text-gray-600 mb-1">Details</p>
                            <p className="text-sm text-gray-700">{alert.details}</p>
                          </div>
                        )}

                        {hasMetrics && (
                          <div>
                            <p className="text-xs font-semibold text-gray-600 mb-2">Triggering Metrics</p>
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                              {Object.entries(alert.related_metrics!).map(([key, value]) => {
                                const numVal = typeof value === 'number' ? value : null;
                                const isTemp = key.includes('temperature');
                                const isBattery = key.includes('battery_soc');
                                const isLoad = key.includes('load');

                                let highlight = '';
                                if (numVal !== null) {
                                  if (isTemp && numVal > 40) highlight = 'border-red-300 bg-red-50';
                                  else if (isBattery && numVal < 70) highlight = 'border-red-300 bg-red-50';
                                  else if (isLoad && numVal > 85) highlight = 'border-orange-300 bg-orange-50';
                                }

                                return (
                                  <div key={key} className={`rounded-lg px-3 py-2 border ${highlight || 'border-gray-200 bg-white'}`}>
                                    <p className="text-xs text-gray-500 truncate">{formatAlertType(key)}</p>
                                    <p className="text-sm font-bold text-gray-900">
                                      {numVal !== null ? numVal.toFixed(2) : String(value)}
                                      {isTemp ? ' °C' : isBattery || isLoad ? '%' : ''}
                                    </p>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {alert.recommended_action && (
                          <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                            <p className="text-sm text-blue-800">
                              <strong>Recommended Action:</strong> {alert.recommended_action}
                            </p>
                          </div>
                        )}

                        <div className="text-right pt-1">
                          <Link
                            to={`/ups/${alert.ups_id}`}
                            className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700"
                          >
                            View {alert.ups_id} Full Details <ExternalLink className="w-3 h-3" />
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-gray-500">No alerts found</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
