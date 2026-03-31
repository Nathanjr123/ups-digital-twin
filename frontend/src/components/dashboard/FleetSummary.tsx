/**
 * FleetSummary Component
 * Displays fleet-wide summary metrics
 */

import { Activity, Battery, AlertTriangle, CheckCircle } from 'lucide-react';
import { MetricCard } from '@/components/common/MetricCard';
import type { FleetSummary } from '@/types/ups';

interface FleetSummaryProps {
  summary: FleetSummary;
}

export function FleetSummaryCards({ summary }: FleetSummaryProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        label="Total UPS Units"
        value={summary.total_units}
        icon={<Activity className="w-6 h-6" />}
        color="primary"
      />
      
      <MetricCard
        label="Healthy Units"
        value={summary.healthy_units}
        icon={<CheckCircle className="w-6 h-6" />}
        color="success"
      />
      
      <MetricCard
        label="Units with Warnings"
        value={summary.warning_units}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="warning"
      />
      
      <MetricCard
        label="Critical Units"
        value={summary.critical_units}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="danger"
      />
      
      <MetricCard
        label="Avg Health Score"
        value={`${summary.average_health_score.toFixed(1)}%`}
        icon={<Activity className="w-6 h-6" />}
        color={summary.average_health_score > 80 ? 'success' : summary.average_health_score > 60 ? 'warning' : 'danger'}
      />
      
      <MetricCard
        label="Avg Battery SOC"
        value={`${summary.average_battery_soc.toFixed(1)}%`}
        icon={<Battery className="w-6 h-6" />}
        color={summary.average_battery_soc > 80 ? 'success' : summary.average_battery_soc > 60 ? 'warning' : 'danger'}
      />
      
      <MetricCard
        label="Total Load"
        value={`${summary.total_load_kw.toFixed(1)} kW`}
        icon={<Activity className="w-6 h-6" />}
        color="primary"
      />
      
      <MetricCard
        label="On Battery"
        value={summary.units_on_battery}
        icon={<Battery className="w-6 h-6" />}
        color={summary.units_on_battery > 0 ? 'warning' : 'success'}
      />
    </div>
  );
}
