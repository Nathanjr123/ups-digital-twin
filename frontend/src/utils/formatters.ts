/**
 * Utility Functions
 */

import clsx, { ClassValue } from 'clsx';

// Combine class names
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Format numbers
export function formatNumber(value: number, decimals: number = 1): string {
  return value.toFixed(decimals);
}

// Format date/time
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

// Get color based on health status
export function getHealthColor(status: string): string {
  switch (status) {
    case 'healthy':
    case 'normal':
      return 'text-success-500';
    case 'warning':
      return 'text-warning-500';
    case 'critical':
    case 'failure':
      return 'text-danger-500';
    default:
      return 'text-gray-500';
  }
}

export function getHealthBgColor(status: string): string {
  switch (status) {
    case 'healthy':
    case 'normal':
      return 'bg-success-500';
    case 'warning':
      return 'bg-warning-500';
    case 'critical':
    case 'failure':
      return 'bg-danger-500';
    default:
      return 'bg-gray-500';
  }
}

// Get severity color
export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'info':
      return 'text-blue-500';
    case 'warning':
      return 'text-warning-500';
    case 'high':
      return 'text-orange-500';
    case 'critical':
      return 'text-danger-500';
    default:
      return 'text-gray-500';
  }
}

export function getSeverityBgColor(severity: string): string {
  switch (severity) {
    case 'info':
      return 'bg-blue-500';
    case 'warning':
      return 'bg-warning-500';
    case 'high':
      return 'bg-orange-500';
    case 'critical':
      return 'bg-danger-500';
    default:
      return 'bg-gray-500';
  }
}

// Calculate percentage
export function calculatePercentage(value: number, max: number): number {
  return Math.min(100, Math.max(0, (value / max) * 100));
}

// Format alert type to readable string
export function formatAlertType(type: string): string {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
