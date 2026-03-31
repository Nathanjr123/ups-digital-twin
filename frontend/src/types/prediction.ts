/**
 * TypeScript types for ML predictions
 */

export interface ContributingFactor {
  feature: string;
  value: number;
  expected_range?: string;
  deviation_pct?: number;
  importance?: number;
  status: "normal" | "below_normal" | "above_normal" | "high_risk";
}

export interface AnomalyPrediction {
  ups_id: string;
  timestamp: string;
  is_anomaly: boolean;
  anomaly_score: number;
  confidence: number;
  severity: "info" | "warning" | "high" | "critical";
  contributing_factors: ContributingFactor[];
}

export interface FailurePrediction {
  ups_id: string;
  timestamp: string;
  will_fail: boolean;
  failure_probability: number;
  confidence: number;
  time_to_failure_days: number;
  risk_level: "low" | "medium" | "high" | "critical";
  risk_factors: ContributingFactor[];
  prediction_horizon: string;
}

export interface CombinedPrediction {
  ups_id: string;
  timestamp: string;
  anomaly: AnomalyPrediction;
  failure: FailurePrediction;
  overall_risk_score: number;
}

export interface ModelPerformance {
  model_name: string;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  samples_trained: number;
  last_trained: string;
  feature_importance: Record<string, number>;
}
