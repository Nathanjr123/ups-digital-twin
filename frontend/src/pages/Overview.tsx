/**
 * Overview Page
 * Main dashboard showing fleet summary with expandable diagnostics per unit
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FleetSummaryCards } from '@/components/dashboard/FleetSummary';
import { Card } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { DiagnosticPanel } from '@/components/diagnostics/DiagnosticPanel';
import { useWebSocket } from '@/hooks/useWebSocket';
import { upsService, alertService } from '@/services/api';
import type { FleetSummary } from '@/types/ups';
import type { Alert } from '@/types/alert';
import { formatTimeAgo, formatAlertType } from '@/utils/formatters';
import { AlertCircle, ChevronDown, ChevronUp, Wifi, WifiOff } from 'lucide-react';

export function Overview() {
  const [fleetSummary, setFleetSummary] = useState<FleetSummary | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [expandedUps, setExpandedUps] = useState<string | null>(null);
  const { telemetryData, isConnected } = useWebSocket();

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await upsService.getFleetSummary();
        setFleetSummary(response.data);
      } catch (error) {
        console.error('Error fetching fleet summary:', error);
      }
    };
    fetchSummary();
    const interval = setInterval(fetchSummary, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await alertService.getAlerts({ limit: 10 });
        setRecentAlerts(response.data.alerts);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  // Sort: critical first, then warning, then normal
  const sortedTelemetry = [...telemetryData].sort((a, b) => {
    const order: Record<string, number> = { critical: 0, failure: 0, anomaly_detected: 1, warning: 1, normal: 2 };
    return (order[a.status] ?? 2) - (order[b.status] ?? 2);
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
              <p className="mt-1 text-sm text-gray-500">Real-time monitoring of UPS fleet</p>
            </div>
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-green-600 font-medium">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">Disconnected</span>
                </>
              )}
            </div>
          </div>
        </div>

        {fleetSummary && (
          <div className="mb-8">
            <FleetSummaryCards summary={fleetSummary} />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Fleet Status - Expandable */}
          <Card
            header={
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Fleet Status</h2>
                <Link to="/fleet" className="text-sm text-primary-600 hover:text-primary-700">View All</Link>
              </div>
            }
          >
            <div className="space-y-1">
              <p className="text-xs text-gray-400 mb-2">Click any unit to expand diagnostics</p>
              {sortedTelemetry.slice(0, 8).map((ups) => (
                <div key={ups.ups_id} className="rounded-lg overflow-hidden border border-gray-100">
                  <div
                    onClick={() => setExpandedUps(expandedUps === ups.ups_id ? null : ups.ups_id)}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <StatusBadge status={ups.status} type="health" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{ups.ups_id}</p>
                        <p className="text-xs text-gray-500">
                          Battery: {ups.battery_soc.toFixed(0)}% | Load: {ups.load_percentage.toFixed(0)}% | Temp: {ups.battery_temperature.toFixed(0)}°C
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{ups.health_score.toFixed(0)}%</p>
                        <p className="text-xs text-gray-500">Health</p>
                      </div>
                      {expandedUps === ups.ups_id ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {expandedUps === ups.ups_id && (
                    <DiagnosticPanel upsId={ups.ups_id} telemetry={ups} />
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Alerts with expandable metrics */}
          <Card
            header={
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Alerts</h2>
                <Link to="/alerts" className="text-sm text-primary-600 hover:text-primary-700">View All</Link>
              </div>
            }
          >
            {recentAlerts.length > 0 ? (
              <div className="space-y-3">
                {recentAlerts.map((alert) => (
                  <AlertRow key={alert.alert_id} alert={alert} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No recent alerts</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

function AlertRow({ alert }: { alert: Alert }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-gray-100 overflow-hidden">
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-start space-x-3 p-3 hover:bg-gray-50 cursor-pointer"
      >
        <AlertCircle
          className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
            alert.severity === 'critical' ? 'text-danger-500' :
            alert.severity === 'high' ? 'text-orange-500' :
            alert.severity === 'warning' ? 'text-warning-500' : 'text-blue-500'
          }`}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-900 truncate">{alert.ups_id}</p>
            <div className="flex items-center gap-2">
              <StatusBadge status={alert.severity} type="severity" />
              {expanded ? <ChevronUp className="w-3 h-3 text-gray-400" /> : <ChevronDown className="w-3 h-3 text-gray-400" />}
            </div>
          </div>
          <p className="mt-1 text-sm text-gray-600">{alert.message}</p>
          <p className="mt-1 text-xs text-gray-500">{formatTimeAgo(alert.timestamp)}</p>
        </div>
      </div>

      {expanded && alert.related_metrics && Object.keys(alert.related_metrics).length > 0 && (
        <div className="bg-gray-50 border-t border-gray-100 px-4 py-3">
          <p className="text-xs font-semibold text-gray-600 mb-2">Triggering Metrics:</p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(alert.related_metrics).map(([key, value]) => (
              <div key={key} className="bg-white rounded px-2 py-1.5 border border-gray-200">
                <p className="text-xs text-gray-500">{formatAlertType(key)}</p>
                <p className="text-sm font-semibold text-gray-900">
                  {typeof value === 'number' ? value.toFixed(2) : String(value)}
                </p>
              </div>
            ))}
          </div>
          {alert.recommended_action && (
            <div className="mt-2 p-2 bg-blue-50 rounded">
              <p className="text-xs text-blue-800"><strong>Action:</strong> {alert.recommended_action}</p>
            </div>
          )}
          <div className="mt-2 text-right">
            <Link to={`/ups/${alert.ups_id}`} className="text-xs font-medium text-indigo-600 hover:text-indigo-700">
              View Unit Details →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
