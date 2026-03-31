/**
 * Application Constants
 */

// App info
export const APP_NAME = 'UPS Digital Twin';
export const APP_VERSION = '1.0.0';

// Navigation routes
export const ROUTES = {
  HOME: '/',
  OVERVIEW: '/overview',
  FLEET: '/fleet',
  UPS_DETAIL: '/ups/:id',
  ANALYTICS: '/analytics',
  ALERTS: '/alerts',
} as const;

// Refresh intervals (milliseconds)
export const REFRESH_INTERVALS = {
  TELEMETRY: 2000,
  FLEET_SUMMARY: 5000,
  ALERTS: 10000,
} as const;

// Chart colors
export const CHART_COLORS = {
  PRIMARY: '#3b82f6',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#06b6d4',
  GRAY: '#6b7280',
} as const;

// Health status thresholds
export const HEALTH_THRESHOLDS = {
  BATTERY_SOC_WARNING: 80,
  BATTERY_SOC_CRITICAL: 60,
  BATTERY_TEMP_WARNING: 35,
  BATTERY_TEMP_CRITICAL: 45,
  INVERTER_TEMP_WARNING: 55,
  INVERTER_TEMP_CRITICAL: 65,
  LOAD_WARNING: 85,
  LOAD_CRITICAL: 95,
} as const;

// Alert severity levels
export const SEVERITY_LEVELS = ['info', 'warning', 'high', 'critical'] as const;

// Alert status options
export const ALERT_STATUSES = ['active', 'acknowledged', 'resolved'] as const;
