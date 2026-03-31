/**
 * MetricCard Component
 * Displays a single metric with label and optional trend indicator
 */

import { ReactNode } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/utils/formatters';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: 'up' | 'down';
  trendValue?: string;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'gray';
  className?: string;
}

const colorClasses = {
  primary: 'bg-blue-50 text-blue-600',
  success: 'bg-green-50 text-green-600',
  warning: 'bg-yellow-50 text-yellow-600',
  danger: 'bg-red-50 text-red-600',
  gray: 'bg-gray-50 text-gray-600',
};

export function MetricCard({
  label,
  value,
  icon,
  trend,
  trendValue,
  color = 'primary',
  className,
}: MetricCardProps) {
  return (
    <div className={cn('bg-white rounded-lg shadow p-6', className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          
          {trend && trendValue && (
            <div className="mt-2 flex items-center text-sm">
              {trend === 'up' ? (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
                {trendValue}
              </span>
            </div>
          )}
        </div>
        
        {icon && (
          <div className={cn('p-3 rounded-full', colorClasses[color])}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
