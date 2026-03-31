/**
 * UPS Detail Page
 * Detailed view of a single UPS with real-time metrics, history charts, and predictions
 */

import { useEffect, useState, Component, type ReactNode, type ErrorInfo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from '@/components/common/Card';
import { Gauge } from '@/components/common/Gauge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { ContributingFactorsList } from '@/components/diagnostics/ContributingFactorsList';
import { TelemetryChart, CHART_GROUPS } from '@/components/charts/TelemetryChart';
import { useWebSocket } from '@/hooks/useWebSocket';
import { upsService, predictionService } from '@/services/api';
import type { UPSInfo, UPSTelemetry, TelemetryHistory } from '@/types/ups';
import type { CombinedPrediction } from '@/types/prediction';
import { ArrowLeft, AlertTriangle, TrendingUp, Activity, Clock, RefreshCw } from 'lucide-react';

// Error boundary to prevent white screens
class DetailErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: string }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UPSDetail render error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-orange-500 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h2>
            <p className="text-sm text-gray-500 mb-4">{this.state.error}</p>
            <button
              onClick={() => { this.setState({ hasError: false, error: '' }); window.location.reload(); }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <RefreshCw className="w-4 h-4" /> Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const CHART_LABELS: Record<string, string> = {
  voltage: 'Voltage',
  temperature: 'Temperature',
  battery: 'Battery',
  load: 'Load & Health',
};

function safeNum(val: any, fallback = 0): number {
  const n = Number(val);
  return isNaN(n) || !isFinite(n) ? fallback : n;
}

export function UPSDetail() {
  return (
    <DetailErrorBoundary>
      <UPSDetailInner />
    </DetailErrorBoundary>
  );
}

function UPSDetailInner() {
  const { id } = useParams<{ id: string }>();
  const { telemetryData } = useWebSocket();
  const [upsInfo, setUpsInfo] = useState<UPSInfo | null>(null);
  const [prediction, setPrediction] = useState<CombinedPrediction | null>(null);
  const [history, setHistory] = useState<TelemetryHistory | null>(null);
  const [historyHours, setHistoryHours] = useState(24);
  const [activeChart, setActiveChart] = useState<string>('voltage');
  const [error, setError] = useState<string | null>(null);

  // Get telemetry from WebSocket, fall back to REST API data
  const wsTelemetry = telemetryData.find(t => t.ups_id === id);
  const currentTelemetry: UPSTelemetry | null = wsTelemetry ?? upsInfo?.latest_telemetry ?? null;

  // Fetch UPS info
  useEffect(() => {
    if (!id) return;
    upsService.getUPS(id)
      .then(r => setUpsInfo(r.data))
      .catch(err => {
        console.error('Error fetching UPS info:', err);
        setError('Failed to load UPS data');
      });
  }, [id]);

  // Fetch predictions
  useEffect(() => {
    if (!id) return;
    const fetchPred = () => predictionService.getPredictions(id).then(r => setPrediction(r.data)).catch(console.error);
    fetchPred();
    const interval = setInterval(fetchPred, 10000);
    return () => clearInterval(interval);
  }, [id]);

  // Fetch telemetry history
  useEffect(() => {
    if (!id) return;
    upsService.getUPSHistory(id, historyHours)
      .then(r => setHistory(r.data))
      .catch(console.error);
  }, [id, historyHours]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-orange-500 mx-auto mb-3" />
          <p className="text-gray-600">{error}</p>
          <Link to="/fleet" className="mt-4 inline-block text-indigo-600 hover:text-indigo-700">Back to Fleet</Link>
        </div>
      </div>
    );
  }

  if (!currentTelemetry && !upsInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-3 animate-spin" />
          <p className="text-gray-500">Loading UPS data...</p>
        </div>
      </div>
    );
  }

  // Use whatever telemetry we have
  const t = currentTelemetry!;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link to="/fleet" className="flex items-center text-primary-600 hover:text-primary-700 mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Fleet
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t.ups_id}</h1>
              {upsInfo && <p className="mt-1 text-sm text-gray-500">{upsInfo.metadata.location}</p>}
              {upsInfo && <p className="text-sm text-gray-500">{upsInfo.metadata.model}</p>}
            </div>
            <div className="flex items-center gap-3">
              {prediction && (
                <div className="text-right mr-3">
                  <p className="text-xs text-gray-500">Risk Score</p>
                  <p className={`text-2xl font-bold ${
                    prediction.overall_risk_score < 30 ? 'text-green-600' :
                    prediction.overall_risk_score < 60 ? 'text-orange-600' : 'text-red-600'
                  }`}>
                    {safeNum(prediction.overall_risk_score).toFixed(0)}%
                  </p>
                </div>
              )}
              <StatusBadge status={t.status} type="health" />
            </div>
          </div>
        </div>

        {/* Gauges */}
        <Card className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <Gauge value={safeNum(t.battery_soc)} max={100} label="Battery SOC" unit="%" warningThreshold={80} criticalThreshold={60} />
            <Gauge value={safeNum(t.load_percentage)} max={100} label="Load" unit="%" warningThreshold={85} criticalThreshold={95} />
            <Gauge value={safeNum(t.battery_temperature)} max={80} label="Battery Temp" unit="°C" warningThreshold={35} criticalThreshold={45} />
            <Gauge value={safeNum(t.inverter_temperature)} max={100} label="Inverter Temp" unit="°C" warningThreshold={55} criticalThreshold={65} />
          </div>
        </Card>

        {/* Telemetry History Charts */}
        <Card
          className="mb-8"
          header={
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-gray-500" />
                <h2 className="text-lg font-semibold text-gray-900">Telemetry History</h2>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex bg-gray-100 rounded-lg p-0.5">
                  {CHART_GROUPS.map(g => (
                    <button
                      key={g}
                      onClick={() => setActiveChart(g)}
                      className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                        activeChart === g ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      {CHART_LABELS[g]}
                    </button>
                  ))}
                </div>
                <div className="flex bg-gray-100 rounded-lg p-0.5 ml-2">
                  {[24, 48, 168].map(h => (
                    <button
                      key={h}
                      onClick={() => setHistoryHours(h)}
                      className={`px-2 py-1.5 text-xs font-medium rounded-md transition-colors ${
                        historyHours === h ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      {h === 168 ? '7d' : `${h}h`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          }
        >
          {history && history.data_points && history.data_points.length > 0 ? (
            <TelemetryChart data={history.data_points} group={activeChart} />
          ) : (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <Clock className="w-5 h-5 mr-2" />
              Loading history...
            </div>
          )}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Metrics */}
          <Card header={<h2 className="text-lg font-semibold text-gray-900">Current Metrics</h2>}>
            <div className="space-y-4">
              <MetricRow label="Input Voltage" value={`${safeNum(t.input_voltage).toFixed(1)} V`} />
              <MetricRow label="Output Voltage" value={`${safeNum(t.output_voltage).toFixed(1)} V`} />
              <MetricRow label="Battery Voltage" value={`${safeNum(t.battery_voltage).toFixed(1)} V`} />
              <MetricRow label="Battery Current" value={`${safeNum(t.battery_current).toFixed(1)} A`} />
              <MetricRow label="Input Frequency" value={`${safeNum(t.input_frequency).toFixed(1)} Hz`} />
              <MetricRow label="Output Frequency" value={`${safeNum(t.output_frequency).toFixed(1)} Hz`} />
              <MetricRow label="Ambient Temp" value={`${safeNum(t.ambient_temperature).toFixed(1)} °C`} />
              <MetricRow label="Runtime Remaining" value={`${safeNum(t.runtime_remaining)} min`} />
              <MetricRow label="Health Score" value={`${safeNum(t.health_score).toFixed(1)}%`} />
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">On Battery</span>
                <span className={`text-sm font-medium ${t.on_battery ? 'text-warning-600' : 'text-success-600'}`}>
                  {t.on_battery ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </Card>

          {/* Predictions & Risk */}
          {prediction && (
            <div className="space-y-8">
              {/* Failure Prediction */}
              <Card
                header={
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-gray-500" />
                      <h2 className="text-lg font-semibold text-gray-900">Failure Prediction</h2>
                    </div>
                    <StatusBadge status={prediction.failure.risk_level} type="severity" />
                  </div>
                }
              >
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Overall Risk Score</span>
                      <span className="text-2xl font-bold text-gray-900">{safeNum(prediction.overall_risk_score).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full transition-all ${
                          prediction.overall_risk_score < 30 ? 'bg-green-500' :
                          prediction.overall_risk_score < 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(100, safeNum(prediction.overall_risk_score))}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 py-3 border-y border-gray-100">
                    <div>
                      <p className="text-xs text-gray-500">Probability</p>
                      <p className="text-lg font-bold text-gray-900">{(safeNum(prediction.failure.failure_probability) * 100).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Time to Failure</p>
                      <p className="text-lg font-bold text-gray-900">{safeNum(prediction.failure.time_to_failure_days)} days</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-lg font-bold text-gray-900">{safeNum(prediction.failure.confidence).toFixed(1)}%</p>
                    </div>
                  </div>

                  {prediction.failure.risk_factors && prediction.failure.risk_factors.length > 0 && (
                    <div>
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Risk Factors ({prediction.failure.risk_factors.length})
                      </p>
                      <ContributingFactorsList factors={prediction.failure.risk_factors} />
                    </div>
                  )}
                </div>
              </Card>

              {/* Anomaly Detection */}
              <Card
                header={
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className={`w-5 h-5 ${prediction.anomaly.is_anomaly ? 'text-orange-500' : 'text-gray-400'}`} />
                      <h2 className="text-lg font-semibold text-gray-900">Anomaly Detection</h2>
                    </div>
                    {prediction.anomaly.is_anomaly ? (
                      <StatusBadge status={prediction.anomaly.severity} type="severity" />
                    ) : (
                      <span className="text-xs px-2.5 py-1 rounded-full bg-green-100 text-green-700 font-medium">Normal</span>
                    )}
                  </div>
                }
              >
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 py-3 border-b border-gray-100">
                    <div>
                      <p className="text-xs text-gray-500">Status</p>
                      <p className={`text-lg font-bold ${prediction.anomaly.is_anomaly ? 'text-orange-600' : 'text-green-600'}`}>
                        {prediction.anomaly.is_anomaly ? 'Anomaly' : 'Normal'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Anomaly Score</p>
                      <p className="text-lg font-bold text-gray-900">{safeNum(prediction.anomaly.anomaly_score).toFixed(3)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-lg font-bold text-gray-900">{safeNum(prediction.anomaly.confidence).toFixed(1)}%</p>
                    </div>
                  </div>

                  {prediction.anomaly.contributing_factors && prediction.anomaly.contributing_factors.length > 0 ? (
                    <div>
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Contributing Factors ({prediction.anomaly.contributing_factors.length})
                      </p>
                      <ContributingFactorsList factors={prediction.anomaly.contributing_factors} />
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 py-2">All parameters within normal range.</p>
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Metadata */}
        {upsInfo && (
          <Card className="mt-8" header={<h2 className="text-lg font-semibold text-gray-900">System Information</h2>}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-gray-600">Model</p>
                <p className="mt-1 text-sm font-medium text-gray-900">{upsInfo.metadata.model}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Location</p>
                <p className="mt-1 text-sm font-medium text-gray-900">{upsInfo.metadata.location}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Installation Date</p>
                <p className="mt-1 text-sm font-medium text-gray-900">{new Date(upsInfo.metadata.installation_date).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Maintenance</p>
                <p className="mt-1 text-sm font-medium text-gray-900">{new Date(upsInfo.metadata.last_maintenance).toLocaleDateString()}</p>
              </div>
              {upsInfo.metadata.capacity_kva && (
                <div>
                  <p className="text-sm text-gray-600">Capacity</p>
                  <p className="mt-1 text-sm font-medium text-gray-900">{upsInfo.metadata.capacity_kva} kVA</p>
                </div>
              )}
              {upsInfo.metadata.serial_number && (
                <div>
                  <p className="text-sm text-gray-600">Serial Number</p>
                  <p className="mt-1 text-sm font-medium text-gray-900">{upsInfo.metadata.serial_number}</p>
                </div>
              )}
              {upsInfo.metadata.firmware_version && (
                <div>
                  <p className="text-sm text-gray-600">Firmware</p>
                  <p className="mt-1 text-sm font-medium text-gray-900">{upsInfo.metadata.firmware_version}</p>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900">{value}</span>
    </div>
  );
}
