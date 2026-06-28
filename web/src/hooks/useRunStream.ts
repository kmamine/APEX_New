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
 * Tracks a run via SSE, with a polling fallback so the final state always lands
 * even if the SSE stream is buffered/dropped by a dev proxy. Every event (and
 * each poll tick) does a full GET so image URLs are always present.
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

    let stopped = false;
    const source = new EventSource(api.eventsUrl(runId));
    let poll: ReturnType<typeof setInterval>;

    const stop = () => {
      if (!stopped) {
        stopped = true;
        source.close();
        clearInterval(poll);
      }
    };

    const refresh = async () => {
      try {
        const next = await api.getRun(runId);
        setDetail(next);
        if (TERMINAL_STATUSES.includes(next.status)) {
          setFinished(true);
          stop();
        }
      } catch (err) {
        setError(String(err));
      }
    };

    source.addEventListener('snapshot', (e) => {
      try {
        setDetail(JSON.parse((e as MessageEvent).data));
      } catch {
        void refresh();
      }
    });
    for (const evt of ['iteration', 'done', 'cancelled', 'failed']) {
      source.addEventListener(evt, () => void refresh());
    }
    source.onerror = () => void refresh();

    // Belt-and-suspenders: poll until the run reaches a terminal state.
    poll = setInterval(() => void refresh(), 2500);

    return stop;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  return { detail, finished, error };
}
