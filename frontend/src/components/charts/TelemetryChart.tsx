import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { UPSTelemetry } from '@/types/ups';

interface MetricConfig {
  key: keyof UPSTelemetry;
  label: string;
  color: string;
  unit: string;
}

const METRIC_GROUPS: Record<string, MetricConfig[]> = {
  voltage: [
    { key: 'input_voltage', label: 'Input Voltage', color: '#6366f1', unit: 'V' },
    { key: 'output_voltage', label: 'Output Voltage', color: '#06b6d4', unit: 'V' },
    { key: 'battery_voltage', label: 'Battery Voltage', color: '#f59e0b', unit: 'V' },
  ],
  temperature: [
    { key: 'battery_temperature', label: 'Battery Temp', color: '#ef4444', unit: '°C' },
    { key: 'inverter_temperature', label: 'Inverter Temp', color: '#f97316', unit: '°C' },
    { key: 'ambient_temperature', label: 'Ambient Temp', color: '#22c55e', unit: '°C' },
  ],
  battery: [
    { key: 'battery_soc', label: 'SOC', color: '#10b981', unit: '%' },
    { key: 'battery_current', label: 'Current', color: '#8b5cf6', unit: 'A' },
  ],
  load: [
    { key: 'load_percentage', label: 'Load', color: '#3b82f6', unit: '%' },
    { key: 'health_score', label: 'Health Score', color: '#22c55e', unit: '%' },
  ],
};

interface Props {
  data: UPSTelemetry[];
  group: keyof typeof METRIC_GROUPS;
  height?: number;
}

export function TelemetryChart({ data, group, height = 280 }: Props) {
  const metrics = METRIC_GROUPS[group];

  const chartData = data.map(d => ({
    time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    ...metrics.reduce((acc, m) => ({ ...acc, [m.label]: Number((d[m.key] as number)?.toFixed(2)) }), {}),
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="time" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
          formatter={(value: number, name: string) => {
            const metric = metrics.find(m => m.label === name);
            return [`${value} ${metric?.unit || ''}`, name];
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {metrics.map(m => (
          <Line
            key={m.label}
            type="monotone"
            dataKey={m.label}
            stroke={m.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export const CHART_GROUPS = Object.keys(METRIC_GROUPS) as (keyof typeof METRIC_GROUPS)[];
