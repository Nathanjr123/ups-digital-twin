/**
 * TypeScript types for UPS data structures
 */

export interface UPSTelemetry {
  ups_id: string;
  timestamp: string;
  input_voltage: number;
  input_current: number;
  input_frequency: number;
  output_voltage: number;
  output_current: number;
  output_frequency: number;
  battery_voltage: number;
  battery_current: number;
  battery_soc: number;
  battery_temperature: number;
  runtime_remaining: number;
  load_percentage: number;
  inverter_temperature: number;
  ambient_temperature: number;
  health_score: number;
  status: "normal" | "warning" | "critical" | "anomaly_detected" | "failure";
  on_battery: boolean;
}

export interface UPSMetadata {
  ups_id: string;
  location: string;
  model: string;
  installation_date: string;
  last_maintenance: string;
  capacity_kva?: number;
  serial_number?: string;
  firmware_version?: string;
}

export interface UPSInfo {
  metadata: UPSMetadata;
  latest_telemetry: UPSTelemetry;
  health_status: "healthy" | "warning" | "critical";
}

export interface FleetSummary {
  total_units: number;
  healthy_units: number;
  warning_units: number;
  critical_units: number;
  average_health_score: number;
  average_battery_soc: number;
  total_load_kw: number;
  units_on_battery: number;
}

export interface TelemetryHistory {
  ups_id: string;
  start_time: string;
  end_time: string;
  data_points: UPSTelemetry[];
  interval_minutes: number;
}
