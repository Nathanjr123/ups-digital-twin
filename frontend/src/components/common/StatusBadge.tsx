/**
 * StatusBadge Component
 * Displays a colored badge for status indicators
 */

import { cn, getHealthBgColor, getSeverityBgColor } from '@/utils/formatters';

interface StatusBadgeProps {
  status: string;
  type?: 'health' | 'severity' | 'custom';
  className?: string;
}

export function StatusBadge({ status, type = 'health', className }: StatusBadgeProps) {
  const bgColor = type === 'health' 
    ? getHealthBgColor(status)
    : type === 'severity'
    ? getSeverityBgColor(status)
    : 'bg-gray-500';

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white',
        bgColor,
        className
      )}
    >
      {status}
    </span>
  );
}
