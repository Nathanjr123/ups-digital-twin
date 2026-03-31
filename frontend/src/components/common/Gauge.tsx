/**
 * Gauge Component
 * Circular gauge for displaying metrics with color-coded ranges
 */

import { cn, formatNumber } from '@/utils/formatters';

interface GaugeProps {
  value: number;
  max?: number;
  min?: number;
  label: string;
  unit?: string;
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
  warningThreshold?: number;
  criticalThreshold?: number;
}

export function Gauge({
  value,
  max = 100,
  min = 0,
  label,
  unit = '',
  size = 'md',
  showValue = true,
  warningThreshold,
  criticalThreshold,
}: GaugeProps) {
  const percentage = ((value - min) / (max - min)) * 100;
  
  // Determine color based on thresholds
  let color = 'text-success-500';
  let strokeColor = '#10b981'; // green
  
  if (criticalThreshold && value >= criticalThreshold) {
    color = 'text-danger-500';
    strokeColor = '#ef4444'; // red
  } else if (warningThreshold && value >= warningThreshold) {
    color = 'text-warning-500';
    strokeColor = '#f59e0b'; // yellow
  }
  
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-40 h-40',
  };
  
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  return (
    <div className="flex flex-col items-center">
      <div className={cn('relative', sizeClasses[size])}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        
        {showValue && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn('text-2xl font-bold', color)}>
              {formatNumber(value, 0)}
            </span>
            {unit && <span className="text-xs text-gray-500">{unit}</span>}
          </div>
        )}
      </div>
      
      <p className="mt-2 text-sm font-medium text-gray-700">{label}</p>
    </div>
  );
}
