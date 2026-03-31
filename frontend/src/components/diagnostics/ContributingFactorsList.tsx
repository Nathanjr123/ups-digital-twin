import type { ContributingFactor } from '@/types/prediction';
import { formatAlertType } from '@/utils/formatters';

interface Props {
  factors: ContributingFactor[];
  maxItems?: number;
  compact?: boolean;
}

function getDeviationColor(pct: number): string {
  if (pct < 10) return 'text-green-600 bg-green-50';
  if (pct < 25) return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'normal': return 'bg-green-100 text-green-700';
    case 'below_normal': return 'bg-blue-100 text-blue-700';
    case 'above_normal': return 'bg-orange-100 text-orange-700';
    case 'high_risk': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
}

export function ContributingFactorsList({ factors, maxItems, compact }: Props) {
  const items = maxItems ? factors.slice(0, maxItems) : factors;

  if (items.length === 0) return null;

  return (
    <div className="space-y-2">
      {items.map((factor, idx) => (
        <div
          key={idx}
          className={`rounded-lg border border-gray-100 ${compact ? 'p-2' : 'p-3'} bg-white`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-900">
              {formatAlertType(factor.feature)}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getStatusColor(factor.status)}`}>
              {formatAlertType(factor.status)}
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs text-gray-600">
            <span>
              Value: <span className="font-semibold text-gray-900">{(typeof factor.value === 'number' && isFinite(factor.value)) ? factor.value.toFixed(2) : '—'}</span>
            </span>
            {factor.expected_range && (
              <span>
                Expected: <span className="text-gray-700">{factor.expected_range}</span>
              </span>
            )}
          </div>

          {(factor.deviation_pct !== undefined || factor.importance !== undefined) && (
            <div className="flex items-center gap-3 mt-1.5">
              {factor.deviation_pct !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${getDeviationColor(factor.deviation_pct)}`}>
                  {factor.deviation_pct.toFixed(1)}% deviation
                </span>
              )}
              {factor.importance !== undefined && (
                <div className="flex items-center gap-1.5 flex-1">
                  <span className="text-xs text-gray-500">Impact:</span>
                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden max-w-[80px]">
                    <div
                      className="h-full bg-indigo-500 rounded-full"
                      style={{ width: `${Math.min(100, factor.importance * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">{(factor.importance * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
