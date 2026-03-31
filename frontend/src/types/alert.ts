/**
 * TypeScript types for alerts
 */

export type AlertType =
  | "anomaly_detected"
  | "failure_predicted"
  | "high_temperature"
  | "low_battery"
  | "overload"
  | "input_power_issue"
  | "maintenance_required";

export type AlertSeverity = "info" | "warning" | "high" | "critical";
export type AlertStatus = "active" | "acknowledged" | "resolved";

export interface Alert {
  alert_id: string;
  ups_id: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  message: string;
  details?: string;
  timestamp: string;
  status: AlertStatus;
  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved_at?: string;
  resolved_by?: string;
  recommended_action?: string;
  related_metrics?: Record<string, any>;
}

export interface AlertStats {
  total_alerts: number;
  active_alerts: number;
  acknowledged_alerts: number;
  resolved_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  warning_alerts: number;
  info_alerts: number;
  alerts_by_type: Record<string, number>;
  alerts_by_ups: Record<string, number>;
}

export interface AlertList {
  alerts: Alert[];
  total: number;
  page: number;
  page_size: number;
}
