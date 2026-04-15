export type StrategyMode = 'safety' | 'balanced' | 'profit';

export interface StrategySettings {
  mode: StrategyMode;
  aggressiveness: number; // 0-100
}

export interface StrategyImpact {
  mode: string;
  aggressiveness: number;
  projected_revenue_change_pct: number;
  battery_degradation_impact_pct: number;
  backup_headroom_minutes: number;
  recommended_min_soc: number;
  max_discharge_rate: number;
  risk_level: string;
  recommendations: string[];
}

export type ScenarioType =
  | 'price_spike'
  | 'load_surge'
  | 'grid_failure'
  | 'battery_degradation';

export interface SimulationRequest {
  scenario_type: ScenarioType;
  ups_ids?: string[];
  parameters?: Record<string, number>;
}

export interface UnitScenarioResult {
  ups_id: string;
  current_health: number;
  projected_health: number;
  current_runtime_minutes: number;
  projected_runtime_minutes: number;
  current_risk_level: string;
  projected_risk_level: string;
  current_failure_probability: number;
  projected_failure_probability: number;
  time_to_critical_minutes: number | null;
  delta_health: number;
  delta_runtime: number;
  alerts_triggered: string[];
  mitigation_actions: string[];
  severity: string;
}

export interface SimulationResult {
  scenario_type: string;
  scenario_title: string;
  scenario_description: string;
  fleet_units_affected: number;
  fleet_units_going_critical: number;
  estimated_first_failure_minutes: number | null;
  fleet_avg_health_current: number;
  fleet_avg_health_projected: number;
  fleet_avg_runtime_current: number;
  fleet_avg_runtime_projected: number;
  unit_results: UnitScenarioResult[];
  recommendations: string[];
}
