import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { predictionService } from '@/services/api';
import { ContributingFactorsList } from './ContributingFactorsList';
import { StatusBadge } from '@/components/common/StatusBadge';
import type { CombinedPrediction } from '@/types/prediction';
import type { UPSTelemetry } from '@/types/ups';
import { AlertTriangle, TrendingUp, ExternalLink, Loader2 } from 'lucide-react';

interface Props {
  upsId: string;
  telemetry: UPSTelemetry;
}

export function DiagnosticPanel({ upsId, telemetry }: Props) {
  const [prediction, setPrediction] = useState<CombinedPrediction | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    predictionService.getPredictions(upsId)
      .then(res => { if (!cancelled) setPrediction(res.data); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [upsId]);

  return (
    <div className="bg-gray-50 border-t border-gray-200 px-4 py-4 space-y-4">
      {/* Quick Telemetry */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MiniMetric label="Input Voltage" value={`${telemetry.input_voltage.toFixed(1)} V`} />
        <MiniMetric label="Output Voltage" value={`${telemetry.output_voltage.toFixed(1)} V`} />
        <MiniMetric label="Battery Temp" value={`${telemetry.battery_temperature.toFixed(1)} °C`}
          warn={telemetry.battery_temperature > 35} critical={telemetry.battery_temperature > 45} />
        <MiniMetric label="Inverter Temp" value={`${telemetry.inverter_temperature.toFixed(1)} °C`}
          warn={telemetry.inverter_temperature > 55} critical={telemetry.inverter_temperature > 65} />
        <MiniMetric label="Battery SOC" value={`${telemetry.battery_soc.toFixed(1)}%`}
          warn={telemetry.battery_soc < 80} critical={telemetry.battery_soc < 60} />
        <MiniMetric label="Load" value={`${telemetry.load_percentage.toFixed(1)}%`}
          warn={telemetry.load_percentage > 85} critical={telemetry.load_percentage > 95} />
        <MiniMetric label="Runtime" value={`${telemetry.runtime_remaining} min`}
          warn={telemetry.runtime_remaining < 30} critical={telemetry.runtime_remaining < 10} />
        <MiniMetric label="Health" value={`${telemetry.health_score.toFixed(1)}%`}
          warn={telemetry.health_score < 70} critical={telemetry.health_score < 50} />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-4 text-gray-400">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          Loading diagnostics...
        </div>
      ) : prediction ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Failure Prediction */}
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-semibold text-gray-900">Failure Prediction</span>
              </div>
              <StatusBadge status={prediction.failure.risk_level} type="severity" />
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs mb-3">
              <div>
                <span className="text-gray-500">Probability</span>
                <p className="font-bold text-gray-900">{(prediction.failure.failure_probability * 100).toFixed(1)}%</p>
              </div>
              <div>
                <span className="text-gray-500">Time to Failure</span>
                <p className="font-bold text-gray-900">{prediction.failure.time_to_failure_days}d</p>
              </div>
              <div>
                <span className="text-gray-500">Risk Score</span>
                <p className="font-bold text-gray-900">{prediction.overall_risk_score.toFixed(0)}%</p>
              </div>
            </div>
            {prediction.failure.risk_factors.length > 0 && (
              <>
                <p className="text-xs font-medium text-gray-600 mb-1.5">Risk Factors:</p>
                <ContributingFactorsList factors={prediction.failure.risk_factors} compact />
              </>
            )}
          </div>

          {/* Anomaly Detection */}
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${prediction.anomaly.is_anomaly ? 'text-orange-500' : 'text-gray-400'}`} />
                <span className="text-sm font-semibold text-gray-900">Anomaly Detection</span>
              </div>
              {prediction.anomaly.is_anomaly ? (
                <StatusBadge status={prediction.anomaly.severity} type="severity" />
              ) : (
                <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">Normal</span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div>
                <span className="text-gray-500">Anomaly Score</span>
                <p className="font-bold text-gray-900">{prediction.anomaly.anomaly_score.toFixed(3)}</p>
              </div>
              <div>
                <span className="text-gray-500">Confidence</span>
                <p className="font-bold text-gray-900">{prediction.anomaly.confidence.toFixed(1)}%</p>
              </div>
            </div>
            {prediction.anomaly.contributing_factors.length > 0 && (
              <>
                <p className="text-xs font-medium text-gray-600 mb-1.5">Contributing Factors:</p>
                <ContributingFactorsList factors={prediction.anomaly.contributing_factors} compact />
              </>
            )}
            {!prediction.anomaly.is_anomaly && prediction.anomaly.contributing_factors.length === 0 && (
              <p className="text-xs text-gray-400 py-2">No anomalies detected. All parameters within normal range.</p>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-400 text-center py-2">Could not load predictions</p>
      )}

      <div className="text-right">
        <Link
          to={`/ups/${upsId}`}
          className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700"
        >
          Full Details <ExternalLink className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}

function MiniMetric({ label, value, warn, critical }: { label: string; value: string; warn?: boolean; critical?: boolean }) {
  const color = critical ? 'text-red-600' : warn ? 'text-orange-600' : 'text-gray-900';
  const bg = critical ? 'bg-red-50 border-red-200' : warn ? 'bg-orange-50 border-orange-200' : 'bg-white border-gray-200';
  return (
    <div className={`rounded-lg p-2 border ${bg}`}>
      <p className="text-xs text-gray-500 truncate">{label}</p>
      <p className={`text-sm font-bold ${color}`}>{value}</p>
    </div>
  );
}
