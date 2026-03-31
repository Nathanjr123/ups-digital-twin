/**
 * Fleet Page
 * Grid view of all UPS units with filtering, sorting, and expandable diagnostics
 */

import { useEffect, useState } from 'react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { DiagnosticPanel } from '@/components/diagnostics/DiagnosticPanel';
import { useWebSocket } from '@/hooks/useWebSocket';
import { predictionService } from '@/services/api';
import type { CombinedPrediction } from '@/types/prediction';
import { Battery, Zap, Thermometer, ChevronDown, ChevronUp, ArrowUpDown } from 'lucide-react';

function safeNum(val: any, fallback = 0): number {
  const n = Number(val);
  return isNaN(n) || !isFinite(n) ? fallback : n;
}

type SortBy = 'name' | 'health' | 'risk';

export function Fleet() {
  const { telemetryData } = useWebSocket();
  const [filter, setFilter] = useState<'all' | 'healthy' | 'warning' | 'critical'>('all');
  const [expandedUps, setExpandedUps] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [predictions, setPredictions] = useState<Record<string, CombinedPrediction>>({});

  // Fetch all predictions for sorting by risk
  useEffect(() => {
    predictionService.runPredictions()
      .then(res => {
        const map: Record<string, CombinedPrediction> = {};
        res.data.forEach(p => { map[p.ups_id] = p; });
        setPredictions(map);
      })
      .catch(console.error);

    const interval = setInterval(() => {
      predictionService.runPredictions()
        .then(res => {
          const map: Record<string, CombinedPrediction> = {};
          res.data.forEach(p => { map[p.ups_id] = p; });
          setPredictions(map);
        })
        .catch(() => {});
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const filteredData = telemetryData.filter((ups) => {
    if (filter === 'all') return true;
    if (filter === 'healthy') return ups.status === 'normal';
    if (filter === 'warning') return ups.status === 'warning';
    if (filter === 'critical') return ups.status === 'critical';
    return true;
  });

  const sortedData = [...filteredData].sort((a, b) => {
    if (sortBy === 'health') return a.health_score - b.health_score;
    if (sortBy === 'risk') {
      const riskA = predictions[a.ups_id]?.overall_risk_score ?? 0;
      const riskB = predictions[b.ups_id]?.overall_risk_score ?? 0;
      return riskB - riskA;
    }
    return a.ups_id.localeCompare(b.ups_id);
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Fleet Monitoring</h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time monitoring of all {telemetryData.length} UPS units — click any card to expand diagnostics
          </p>
        </div>

        {/* Filters & Sort */}
        <div className="mb-6 flex flex-wrap gap-4">
          <div className="flex space-x-2">
            {(['all', 'healthy', 'warning', 'critical'] as const).map(f => {
              const colors: Record<string, string> = {
                all: 'bg-primary-600', healthy: 'bg-success-600', warning: 'bg-warning-600', critical: 'bg-danger-600',
              };
              return (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${
                    filter === f ? `${colors[f]} text-white` : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {f === 'all' ? 'All Units' : f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-4 h-4 text-gray-400" />
            <div className="flex bg-gray-100 rounded-lg p-0.5">
              {(['name', 'health', 'risk'] as const).map(s => (
                <button
                  key={s}
                  onClick={() => setSortBy(s)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    sortBy === s ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {s === 'name' ? 'Name' : s === 'health' ? 'Worst Health' : 'Highest Risk'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* UPS Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedData.map((ups) => {
            const isExpanded = expandedUps === ups.ups_id;
            const pred = predictions[ups.ups_id];

            return (
              <div key={ups.ups_id} className="rounded-xl overflow-hidden shadow-sm border border-gray-200 bg-white hover:shadow-lg transition-shadow">
                <div
                  onClick={() => setExpandedUps(isExpanded ? null : ups.ups_id)}
                  className="cursor-pointer"
                >
                  <div className="p-5 space-y-4">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{ups.ups_id}</h3>
                        <p className="text-sm text-gray-500">Health: {safeNum(ups.health_score).toFixed(0)}%</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {pred && (
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            pred.overall_risk_score < 30 ? 'bg-green-100 text-green-700' :
                            pred.overall_risk_score < 60 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            Risk: {safeNum(pred.overall_risk_score).toFixed(0)}%
                          </span>
                        )}
                        <StatusBadge status={ups.status} type="health" />
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <Battery className="w-4 h-4 text-gray-500 mx-auto mb-1" />
                        <p className="text-2xl font-bold text-gray-900">{safeNum(ups.battery_soc).toFixed(0)}%</p>
                        <p className="text-xs text-gray-500">Battery</p>
                      </div>
                      <div className="text-center">
                        <Zap className="w-4 h-4 text-gray-500 mx-auto mb-1" />
                        <p className="text-2xl font-bold text-gray-900">{safeNum(ups.load_percentage).toFixed(0)}%</p>
                        <p className="text-xs text-gray-500">Load</p>
                      </div>
                      <div className="text-center">
                        <Thermometer className="w-4 h-4 text-gray-500 mx-auto mb-1" />
                        <p className="text-2xl font-bold text-gray-900">{safeNum(ups.battery_temperature).toFixed(0)}°C</p>
                        <p className="text-xs text-gray-500">Temp</p>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="pt-4 border-t border-gray-200 flex justify-between items-center text-sm">
                      <span className="text-gray-500">{safeNum(ups.output_voltage).toFixed(0)}V Output</span>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">{safeNum(ups.runtime_remaining)} min runtime</span>
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                      </div>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <DiagnosticPanel upsId={ups.ups_id} telemetry={ups} />
                )}
              </div>
            );
          })}
        </div>

        {sortedData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No UPS units found with this filter</p>
          </div>
        )}
      </div>
    </div>
  );
}
