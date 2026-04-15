/**
 * Simulation Page
 * Profit vs Safety strategy controls + What-If scenario engine
 */

import { useEffect, useState, useCallback } from 'react';
import { simulationService } from '@/services/api';
import type {
  StrategyMode, StrategySettings, StrategyImpact,
  ScenarioType, SimulationResult, UnitScenarioResult,
} from '@/types/simulation';
import {
  DollarSign, Shield, Sliders, Zap, Battery,
  AlertTriangle, TrendingUp, Clock, ChevronDown,
  ChevronUp, Play, Loader2, CheckCircle,
} from 'lucide-react';

// ------------------------------------------------------------------ //
//  Helpers                                                             //
// ------------------------------------------------------------------ //

function safeNum(val: any, fallback = 0): number {
  const n = Number(val);
  return isNaN(n) || !isFinite(n) ? fallback : n;
}

function riskColor(level: string) {
  switch (level) {
    case 'critical': return 'text-red-600';
    case 'high':     return 'text-orange-600';
    case 'medium':   return 'text-yellow-600';
    default:         return 'text-green-600';
  }
}

function riskBg(level: string) {
  switch (level) {
    case 'critical': return 'bg-red-100 text-red-700 border-red-200';
    case 'high':     return 'bg-orange-100 text-orange-700 border-orange-200';
    case 'medium':   return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    default:         return 'bg-green-100 text-green-700 border-green-200';
  }
}

function deltaArrow(val: number, invertGood = false) {
  const bad = invertGood ? val > 0 : val < 0;
  if (Math.abs(val) < 0.5) return <span className="text-gray-400 text-xs">—</span>;
  return bad
    ? <span className="text-red-500 text-xs font-bold">▼ {Math.abs(val).toFixed(1)}</span>
    : <span className="text-green-500 text-xs font-bold">▲ {Math.abs(val).toFixed(1)}</span>;
}

// ------------------------------------------------------------------ //
//  Strategy Mode Panel                                                 //
// ------------------------------------------------------------------ //

const MODES: { id: StrategyMode; label: string; icon: typeof Shield; desc: string; color: string; activeColor: string }[] = [
  {
    id: 'safety',
    label: 'Safety Mode',
    icon: Shield,
    desc: 'Maximise backup headroom. Conservative SOC floor. No arbitrage.',
    color: 'border-blue-200 hover:border-blue-400',
    activeColor: 'border-blue-500 bg-blue-50 ring-2 ring-blue-400',
  },
  {
    id: 'balanced',
    label: 'Balanced',
    icon: Sliders,
    desc: 'Moderate arbitrage with maintained backup protection.',
    color: 'border-indigo-200 hover:border-indigo-400',
    activeColor: 'border-indigo-500 bg-indigo-50 ring-2 ring-indigo-400',
  },
  {
    id: 'profit',
    label: 'Profit Mode',
    icon: DollarSign,
    desc: 'Aggressive discharge at peak prices. Higher revenue, higher wear.',
    color: 'border-amber-200 hover:border-amber-400',
    activeColor: 'border-amber-500 bg-amber-50 ring-2 ring-amber-400',
  },
];

function StrategyPanel() {
  const [settings, setSettings] = useState<StrategySettings>({ mode: 'balanced', aggressiveness: 50 });
  const [impact, setImpact] = useState<StrategyImpact | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Load current strategy on mount
  useEffect(() => {
    simulationService.getStrategy()
      .then(r => setSettings(r.data))
      .catch(() => {});
  }, []);

  // Live preview as slider/mode changes
  useEffect(() => {
    const t = setTimeout(() => {
      setLoading(true);
      simulationService.previewStrategy(settings)
        .then(r => setImpact(r.data))
        .catch(() => {})
        .finally(() => setLoading(false));
    }, 200);
    return () => clearTimeout(t);
  }, [settings]);

  const handleApply = async () => {
    setSaving(true);
    try {
      const r = await simulationService.setStrategy(settings);
      setImpact(r.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {}
    setSaving(false);
  };

  const agg = settings.aggressiveness;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-100 rounded-lg">
          <Sliders className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Profit vs Safety Strategy</h2>
          <p className="text-sm text-gray-500">Toggle how the AI manages battery discharge — from aggressive revenue generation to maximum backup protection.</p>
        </div>
      </div>

      {/* Mode toggle */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {MODES.map(m => {
          const Icon = m.icon;
          const active = settings.mode === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setSettings(s => ({ ...s, mode: m.id }))}
              className={`flex flex-col items-center p-4 rounded-xl border-2 transition-all cursor-pointer text-left ${active ? m.activeColor : m.color + ' bg-white'}`}
            >
              <Icon className={`w-6 h-6 mb-2 ${active ? 'text-current' : 'text-gray-400'}`} />
              <span className="text-sm font-semibold text-gray-900">{m.label}</span>
              <span className="text-xs text-gray-500 mt-1 text-center leading-tight">{m.desc}</span>
            </button>
          );
        })}
      </div>

      {/* Aggressiveness slider */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-gray-600">Pure Safety</span>
          </div>
          <div className="text-center">
            <span className="text-2xl font-bold text-gray-900">{agg}</span>
            <span className="text-sm text-gray-500 ml-1">/ 100</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Pure Profit</span>
            <DollarSign className="w-4 h-4 text-amber-500" />
          </div>
        </div>
        <div className="relative">
          <div className="w-full h-3 rounded-full bg-gradient-to-r from-blue-400 via-indigo-400 to-amber-400 opacity-30 absolute top-1/2 -translate-y-1/2" />
          <input
            type="range"
            min={0}
            max={100}
            value={agg}
            onChange={e => setSettings(s => ({ ...s, aggressiveness: Number(e.target.value) }))}
            className="relative w-full h-3 appearance-none bg-transparent cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-indigo-600 [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-white [&::-webkit-slider-runnable-track]:h-3 [&::-webkit-slider-runnable-track]:rounded-full [&::-webkit-slider-runnable-track]:bg-gradient-to-r [&::-webkit-slider-runnable-track]:from-blue-200 [&::-webkit-slider-runnable-track]:via-indigo-200 [&::-webkit-slider-runnable-track]:to-amber-200"
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>0</span><span>25</span><span>50</span><span>75</span><span>100</span>
        </div>
      </div>

      {/* Impact cards */}
      {loading && (
        <div className="flex items-center gap-2 text-gray-400 py-4 justify-center">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Calculating impact…</span>
        </div>
      )}

      {!loading && impact && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <ImpactCard
            label="Revenue Change"
            value={`+${safeNum(impact.projected_revenue_change_pct).toFixed(1)}%`}
            sub="vs baseline"
            icon={<TrendingUp className="w-4 h-4 text-green-500" />}
            valueColor={impact.projected_revenue_change_pct > 0 ? 'text-green-600' : 'text-gray-600'}
          />
          <ImpactCard
            label="Battery Wear"
            value={`+${safeNum(impact.battery_degradation_impact_pct).toFixed(1)}%`}
            sub="increased degradation"
            icon={<Battery className="w-4 h-4 text-orange-500" />}
            valueColor={impact.battery_degradation_impact_pct > 25 ? 'text-red-600' : impact.battery_degradation_impact_pct > 10 ? 'text-orange-600' : 'text-gray-600'}
          />
          <ImpactCard
            label="Backup Headroom"
            value={`${safeNum(impact.backup_headroom_minutes).toFixed(0)} min`}
            sub="available runtime"
            icon={<Clock className="w-4 h-4 text-blue-500" />}
            valueColor={impact.backup_headroom_minutes < 30 ? 'text-red-600' : impact.backup_headroom_minutes < 60 ? 'text-orange-600' : 'text-blue-600'}
          />
          <ImpactCard
            label="Risk Level"
            value={impact.risk_level.charAt(0).toUpperCase() + impact.risk_level.slice(1)}
            sub={`Min SOC: ${impact.recommended_min_soc}%`}
            icon={<AlertTriangle className={`w-4 h-4 ${riskColor(impact.risk_level)}`} />}
            valueColor={riskColor(impact.risk_level)}
          />
        </div>
      )}

      {!loading && impact && (
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">Recommendations</p>
          <ul className="space-y-1">
            {impact.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={handleApply}
        disabled={saving}
        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
      >
        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <CheckCircle className="w-4 h-4" /> : null}
        {saved ? 'Strategy Applied!' : saving ? 'Applying…' : 'Apply Strategy'}
      </button>
    </div>
  );
}

function ImpactCard({ label, value, sub, icon, valueColor }: {
  label: string; value: string; sub: string; icon: React.ReactNode; valueColor: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
      <div className="flex justify-center mb-1">{icon}</div>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-xl font-bold ${valueColor}`}>{value}</p>
      <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
    </div>
  );
}

// ------------------------------------------------------------------ //
//  Scenario cards                                                      //
// ------------------------------------------------------------------ //

const SCENARIOS: {
  type: ScenarioType;
  title: string;
  subtitle: string;
  icon: typeof Zap;
  color: string;
  parameters: Record<string, number>;
}[] = [
  {
    type: 'price_spike',
    title: 'Energy Price Spike 3×',
    subtitle: 'What if prices triple tomorrow?',
    icon: DollarSign,
    color: 'from-amber-50 to-yellow-50 border-amber-200',
    parameters: { price_multiplier: 3 },
  },
  {
    type: 'load_surge',
    title: 'Critical Load Doubles',
    subtitle: 'What if load surges in 10 min?',
    icon: Zap,
    color: 'from-orange-50 to-red-50 border-orange-200',
    parameters: { surge_factor: 2 },
  },
  {
    type: 'grid_failure',
    title: 'Grid Failure at 2 PM',
    subtitle: 'What if grid drops at peak time?',
    icon: AlertTriangle,
    color: 'from-red-50 to-rose-50 border-red-200',
    parameters: { failure_duration_minutes: 30 },
  },
  {
    type: 'battery_degradation',
    title: 'Battery SoH → 85%',
    subtitle: 'What if batteries degrade now?',
    icon: Battery,
    color: 'from-purple-50 to-indigo-50 border-purple-200',
    parameters: { target_soh_pct: 85 },
  },
];

function ScenarioEngine() {
  const [running, setRunning] = useState<ScenarioType | null>(null);
  const [results, setResults] = useState<Partial<Record<ScenarioType, SimulationResult>>>({});
  const [expanded, setExpanded] = useState<ScenarioType | null>(null);

  const run = useCallback(async (scenario: typeof SCENARIOS[0]) => {
    setRunning(scenario.type);
    try {
      const r = await simulationService.runSimulation({
        scenario_type: scenario.type,
        parameters: scenario.parameters,
      });
      setResults(prev => ({ ...prev, [scenario.type]: r.data }));
      setExpanded(scenario.type);
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(null);
    }
  }, []);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-orange-100 rounded-lg">
          <Play className="w-5 h-5 text-orange-600" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">What-If Simulation Engine</h2>
          <p className="text-sm text-gray-500">Explore scenarios against live fleet telemetry to see projected impact before it happens.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {SCENARIOS.map(scenario => {
          const Icon = scenario.icon;
          const result = results[scenario.type];
          const isRunning = running === scenario.type;
          const isExpanded = expanded === scenario.type;

          return (
            <div key={scenario.type} className={`rounded-xl border bg-gradient-to-br ${scenario.color} overflow-hidden`}>
              {/* Header */}
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/60 rounded-lg">
                      <Icon className="w-5 h-5 text-gray-700" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-sm">{scenario.title}</h3>
                      <p className="text-xs text-gray-500">{scenario.subtitle}</p>
                    </div>
                  </div>
                  {result && (
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${riskBg(result.fleet_units_going_critical > 3 ? 'critical' : result.fleet_units_going_critical > 1 ? 'high' : result.fleet_units_going_critical > 0 ? 'medium' : 'low')}`}>
                      {result.fleet_units_going_critical > 0 ? `${result.fleet_units_going_critical} critical` : 'Fleet OK'}
                    </span>
                  )}
                </div>

                {/* Result summary */}
                {result && (
                  <div className="grid grid-cols-3 gap-3 mb-3">
                    <MiniStat
                      label="Units Affected"
                      value={String(result.fleet_units_affected)}
                      warn={result.fleet_units_affected > 4}
                    />
                    <MiniStat
                      label="Avg Health Δ"
                      value={`${(result.fleet_avg_health_projected - result.fleet_avg_health_current).toFixed(1)}%`}
                      warn={(result.fleet_avg_health_projected - result.fleet_avg_health_current) < -5}
                    />
                    <MiniStat
                      label="First Failure"
                      value={result.estimated_first_failure_minutes != null ? `${result.estimated_first_failure_minutes.toFixed(0)} min` : 'N/A'}
                      warn={result.estimated_first_failure_minutes != null && result.estimated_first_failure_minutes < 30}
                    />
                  </div>
                )}

                {/* Run button */}
                <button
                  onClick={() => run(scenario)}
                  disabled={isRunning}
                  className="w-full py-2 bg-white/70 hover:bg-white border border-white/80 text-gray-800 text-sm font-medium rounded-lg transition-all disabled:opacity-60 flex items-center justify-center gap-2"
                >
                  {isRunning ? (
                    <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Simulating…</>
                  ) : result ? (
                    <><Play className="w-3.5 h-3.5" /> Re-run Simulation</>
                  ) : (
                    <><Play className="w-3.5 h-3.5" /> Run Simulation</>
                  )}
                </button>
              </div>

              {/* Expandable results */}
              {result && (
                <>
                  <button
                    onClick={() => setExpanded(isExpanded ? null : scenario.type)}
                    className="w-full flex items-center justify-between px-5 py-2.5 bg-white/40 border-t border-white/60 text-sm font-medium text-gray-700 hover:bg-white/60 transition-colors"
                  >
                    <span>Per-unit breakdown ({result.unit_results.length} units)</span>
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {isExpanded && (
                    <div className="bg-white/70 px-4 py-4 border-t border-white/60 space-y-3">
                      {/* Description */}
                      <p className="text-xs text-gray-600 leading-relaxed">{result.scenario_description}</p>

                      {/* Unit table */}
                      <div className="overflow-x-auto rounded-lg border border-white/80">
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="bg-white/60 text-gray-500 uppercase tracking-wide">
                              <th className="text-left px-3 py-2">Unit</th>
                              <th className="px-3 py-2 text-right">Health</th>
                              <th className="px-3 py-2 text-right">Runtime</th>
                              <th className="px-3 py-2 text-center">Risk</th>
                              <th className="px-3 py-2 text-center">Severity</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/60">
                            {result.unit_results.map((u, i) => (
                              <UnitRow key={i} unit={u} />
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Recommendations */}
                      <div className="bg-white/50 rounded-lg p-3">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Recommended Actions</p>
                        <ul className="space-y-1">
                          {result.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                              <CheckCircle className="w-3 h-3 text-indigo-400 mt-0.5 flex-shrink-0" />
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function MiniStat({ label, value, warn }: { label: string; value: string; warn?: boolean }) {
  return (
    <div className="bg-white/50 rounded-lg p-2 text-center">
      <p className="text-gray-500 text-xs">{label}</p>
      <p className={`font-bold text-sm ${warn ? 'text-red-600' : 'text-gray-800'}`}>{value}</p>
    </div>
  );
}

function UnitRow({ unit }: { unit: UnitScenarioResult }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <tr
        className="hover:bg-white/40 cursor-pointer transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        <td className="px-3 py-2 font-medium text-gray-900">{unit.ups_id}</td>
        <td className="px-3 py-2 text-right">
          <span className="text-gray-500">{unit.current_health.toFixed(0)}%</span>
          <span className="mx-1 text-gray-300">→</span>
          <span className={unit.delta_health < -5 ? 'text-red-600 font-semibold' : 'text-gray-700'}>
            {unit.projected_health.toFixed(0)}%
          </span>
          <span className="ml-1">{deltaArrow(unit.delta_health)}</span>
        </td>
        <td className="px-3 py-2 text-right">
          <span className="text-gray-500">{unit.current_runtime_minutes.toFixed(0)}m</span>
          <span className="mx-1 text-gray-300">→</span>
          <span className={unit.delta_runtime < -10 ? 'text-red-600 font-semibold' : 'text-gray-700'}>
            {unit.projected_runtime_minutes.toFixed(0)}m
          </span>
        </td>
        <td className="px-3 py-2 text-center">
          <span className={`text-xs font-medium ${riskColor(unit.projected_risk_level)}`}>
            {unit.projected_risk_level}
          </span>
        </td>
        <td className="px-3 py-2 text-center">
          <span className={`text-xs px-1.5 py-0.5 rounded-full border font-medium ${riskBg(unit.severity)}`}>
            {unit.severity}
          </span>
        </td>
      </tr>
      {open && (unit.alerts_triggered.length > 0 || unit.mitigation_actions.length > 0) && (
        <tr>
          <td colSpan={5} className="px-3 py-3 bg-white/30">
            {unit.alerts_triggered.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-semibold text-red-700 mb-1">Alerts</p>
                {unit.alerts_triggered.map((a, i) => (
                  <p key={i} className="text-xs text-red-600 flex items-start gap-1.5 mb-0.5">
                    <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" /> {a}
                  </p>
                ))}
              </div>
            )}
            {unit.mitigation_actions.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-indigo-700 mb-1">Mitigations</p>
                {unit.mitigation_actions.map((m, i) => (
                  <p key={i} className="text-xs text-indigo-600 flex items-start gap-1.5 mb-0.5">
                    <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" /> {m}
                  </p>
                ))}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

// ------------------------------------------------------------------ //
//  Page                                                               //
// ------------------------------------------------------------------ //

export function Simulation() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Strategy & Simulation</h1>
          <p className="mt-1 text-sm text-gray-500">
            Configure your AI battery strategy and run what-if scenarios against live fleet data.
          </p>
        </div>

        <StrategyPanel />
        <ScenarioEngine />
      </div>
    </div>
  );
}
