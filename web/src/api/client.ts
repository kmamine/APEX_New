import type {
  OptionsResponse,
  Preset,
  RunDetail,
  StartRunResponse,
  ValidationResult,
} from './types';

const API = '/api/v1';

async function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getOptions: () => fetch(`${API}/options`).then(asJson<OptionsResponse>),
  getPresets: () => fetch(`${API}/presets`).then(asJson<Preset[]>),

  validateGoal: (data: Record<string, unknown>) =>
    fetch(`${API}/goal/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(asJson<ValidationResult>),

  startRun: (body: FormData) =>
    fetch(`${API}/runs`, { method: 'POST', body }).then(asJson<StartRunResponse>),

  getRun: (runId: string) => fetch(`${API}/runs/${runId}`).then(asJson<RunDetail>),

  cancelRun: (runId: string) =>
    fetch(`${API}/runs/${runId}`, { method: 'DELETE' }).then(asJson<RunDetail>),

  eventsUrl: (runId: string) => `${API}/runs/${runId}/events`,
};
