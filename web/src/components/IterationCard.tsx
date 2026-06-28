import type { Iteration } from '../api/types';
import { Badge } from './ui/Badge';
import { cn } from '../lib/cn';

function decisionTone(decision: string): 'green' | 'blue' | 'amber' | 'red' | 'gray' {
  if (decision === 'accept') return 'green';
  if (decision === 'refine') return 'blue';
  if (decision === 'stop_identity_fail') return 'red';
  if (decision.startsWith('stop')) return 'amber';
  return 'gray';
}

export function IterationCard({ iteration }: { iteration: Iteration }) {
  return (
    <div className={cn('card p-4', iteration.accepted && 'ring-2 ring-green-400')}>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700">Iteration {iteration.index}</span>
        <Badge tone={decisionTone(iteration.decision)}>{iteration.decision}</Badge>
      </div>
      <img
        src={iteration.image_url}
        alt={`iteration ${iteration.index}`}
        className="mb-3 aspect-square w-full rounded-lg object-cover"
      />
      <div className="mb-2 flex items-center gap-2 text-xs">
        <Badge tone="blue">judge {iteration.overall.toFixed(1)}</Badge>
        {iteration.identity != null && (
          <Badge tone={iteration.identity >= 0.35 ? 'green' : 'red'}>
            identity {iteration.identity.toFixed(2)}
          </Badge>
        )}
      </div>
      <p className="mb-2 line-clamp-2 text-xs text-gray-500" title={iteration.instruction}>
        {iteration.instruction}
      </p>
      <div className="flex flex-wrap gap-1">
        {iteration.metrics.map((metric) => (
          <span
            key={metric.name}
            title={metric.detail}
            className={cn(
              'rounded px-1.5 py-0.5 text-[11px]',
              metric.passed ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700',
            )}
          >
            {metric.name} {metric.value.toFixed(metric.value < 10 ? 2 : 0)}
          </span>
        ))}
      </div>
    </div>
  );
}
