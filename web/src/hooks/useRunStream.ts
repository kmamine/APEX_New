import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { RunDetail } from '../api/types';
import { TERMINAL_STATUSES } from '../api/types';

interface RunStream {
  detail: RunDetail | null;
  finished: boolean;
  error: string | null;
}

/**
 * Subscribes to a run's SSE stream. Each event triggers a full GET of the run
 * (so image URLs are always present); the snapshot event hydrates immediately
 * and late-joins / reconnects work without replay.
 */
export function useRunStream(runId: string | null): RunStream {
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [finished, setFinished] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    setDetail(null);
    setFinished(false);
    setError(null);

    const source = new EventSource(api.eventsUrl(runId));
    let closed = false;

    const refresh = async () => {
      try {
        const next = await api.getRun(runId);
        setDetail(next);
        if (TERMINAL_STATUSES.includes(next.status)) {
          setFinished(true);
          close();
        }
      } catch (err) {
        setError(String(err));
      }
    };

    const close = () => {
      if (!closed) {
        closed = true;
        source.close();
      }
    };

    source.addEventListener('snapshot', (e) => {
      try {
        setDetail(JSON.parse((e as MessageEvent).data));
      } catch {
        void refresh();
      }
    });
    source.addEventListener('iteration', () => void refresh());
    source.addEventListener('done', () => void refresh());
    source.addEventListener('cancelled', () => void refresh());
    source.addEventListener('failed', () => void refresh());
    source.onerror = () => {
      // Transport hiccup: if the run already finished server-side, a refresh
      // settles state; otherwise the browser auto-reconnects.
      if (!finished) void refresh();
    };

    return close;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  return { detail, finished, error };
}
