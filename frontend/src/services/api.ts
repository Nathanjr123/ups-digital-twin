/**
 * API Client
 * Handles all HTTP requests to the backend API
 */

import axios from 'axios';
import type { UPSInfo, FleetSummary, UPSTelemetry, TelemetryHistory } from '@/types/ups';
import type { CombinedPrediction, ModelPerformance } from '@/types/prediction';
import type { Alert, AlertList, AlertStats } from '@/types/alert';
import type { StrategySettings, StrategyImpact, SimulationRequest, SimulationResult } from '@/types/simulation';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// UPS Endpoints
export const upsService = {
  getAllUPS: () => api.get<UPSInfo[]>('/api/ups/'),
  
  getFleetSummary: () => api.get<FleetSummary>('/api/ups/fleet-summary'),
  
  getUPS: (upsId: string) => api.get<UPSInfo>(`/api/ups/${upsId}`),
  
  getUPSTelemetry: (upsId: string) => api.get<UPSTelemetry>(`/api/ups/${upsId}/telemetry`),
  
  getUPSHistory: (upsId: string, hours: number = 24) =>
    api.get<TelemetryHistory>(`/api/ups/${upsId}/history?hours=${hours}`),
};

// Prediction Endpoints
export const predictionService = {
  getPredictions: (upsId: string) =>
    api.get<CombinedPrediction>(`/api/predictions/${upsId}`),
  
  runPredictions: () =>
    api.post<CombinedPrediction[]>('/api/predictions/run'),
  
  getModelPerformance: () =>
    api.get<ModelPerformance[]>('/api/predictions/analytics/model-performance'),
};

// Alert Endpoints
export const alertService = {
  getAlerts: (params?: {
    ups_id?: string;
    severity?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => api.get<AlertList>('/api/alerts/', { params }),
  
  getAlertStats: () => api.get<AlertStats>('/api/alerts/statistics'),
  
  getAlert: (alertId: string) => api.get<Alert>(`/api/alerts/${alertId}`),
  
  updateAlert: (alertId: string, update: { status?: string; acknowledged_by?: string; resolved_by?: string }) =>
    api.patch<Alert>(`/api/alerts/${alertId}`, update),
};

// Simulation Endpoints
export const simulationService = {
  getStrategy: () => api.get<StrategySettings>('/api/simulation/strategy'),

  setStrategy: (settings: StrategySettings) =>
    api.post<StrategyImpact>('/api/simulation/strategy', settings),

  previewStrategy: (settings: StrategySettings) =>
    api.post<StrategyImpact>('/api/simulation/strategy/preview', settings),

  runSimulation: (request: SimulationRequest) =>
    api.post<SimulationResult>('/api/simulation/run', request),
};

export default api;
