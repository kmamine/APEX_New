import type { RunStatus } from '../api/types';
import { useRunStream } from '../hooks/useRunStream';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { Spinner } from './ui/Spinner';
import { IterationCard } from './IterationCard';

function statusTone(status: RunStatus): 'green' | 'blue' | 'amber' | 'red' | 'gray' {
  if (status === 'completed') return 'green';
  if (status === 'running' || status === 'pending') return 'blue';
  if (status === 'failed') return 'red';
  if (status === 'cancelled') return 'gray';
  return 'amber';
}

export function RunView({ runId, onReset }: { runId: string; onReset: () => void }) {
  const { detail, finished, error } = useRunStream(runId);

  if (error && !detail) {
    return (
      <Card>
        <p className="text-red-600">Failed to load run: {error}</p>
        <Button className="mt-3" onClick={onReset}>
          Start over
        </Button>
      </Card>
    );
  }
  if (!detail) return <Spinner label="Starting run…" />;

  const running = !finished && (detail.status === 'running' || detail.status === 'pending');

  // Prefer the final image; otherwise fall back to the best/last iteration so a
  // stopped run still shows a result.
  const iterations = detail.iterations;
  const bestIteration =
    detail.final_index >= 0 && detail.final_index < iterations.length
      ? iterations[detail.final_index]
      : iterations[iterations.length - 1];
  const resultUrl = detail.final_image_url ?? bestIteration?.image_url ?? null;

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Badge tone={statusTone(detail.status)}>{detail.status}</Badge>
            <span className="text-sm text-gray-600">
              iteration {detail.current_iteration} / {detail.max_iterations}
            </span>
            {running && <Spinner label="working…" />}
          </div>
          <Button variant="outline" onClick={onReset}>
            New portrait
          </Button>
        </div>
        {detail.error && <p className="mt-2 text-sm text-red-600">{detail.error}</p>}
      </Card>

      <Card title="Before → After">
        <div className="grid gap-4 sm:grid-cols-2">
          <figure>
            <img src={detail.input_image_url} alt="input" className="w-full rounded-lg" />
            <figcaption className="mt-1 text-center text-xs text-gray-500">Original</figcaption>
          </figure>
          <figure>
            {resultUrl ? (
              <a href={resultUrl} download>
                <img src={resultUrl} alt="result portrait" className="w-full rounded-lg" />
              </a>
            ) : (
              <div className="flex aspect-square items-center justify-center rounded-lg bg-gray-100 text-sm text-gray-400">
                {running ? 'Generating…' : 'No result'}
              </div>
            )}
            <figcaption className="mt-1 text-center text-xs text-gray-500">
              {detail.final_image_url
                ? 'Final — click to download'
                : resultUrl
                  ? 'Best iteration so far'
                  : 'Final'}
            </figcaption>
          </figure>
        </div>
      </Card>

      <div>
        <h3 className="section-title mb-3">Iterations</h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {detail.iterations.map((iteration) => (
            <IterationCard key={iteration.index} iteration={iteration} />
          ))}
          {!detail.iterations.length && (
            <p className="text-sm text-gray-500">Waiting for the first iteration…</p>
          )}
        </div>
      </div>
    </div>
  );
}
