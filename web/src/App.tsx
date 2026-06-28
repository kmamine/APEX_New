import { useEffect, useState } from 'react';
import { api } from './api/client';
import type { GoalForm as GoalFormData, OptionsResponse, Preset } from './api/types';
import { GoalForm } from './components/GoalForm';
import { RunView } from './components/RunView';
import { Spinner } from './components/ui/Spinner';

export function App() {
  const [options, setOptions] = useState<OptionsResponse | null>(null);
  const [presets, setPresets] = useState<Preset[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [runId, setRunId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.getOptions(), api.getPresets()])
      .then(([opts, prs]) => {
        setOptions(opts);
        setPresets(prs);
      })
      .catch((err) => setLoadError(String(err)));
  }, []);

  const start = async (form: GoalFormData, image: File) => {
    setBusy(true);
    setStartError(null);
    try {
      const body = new FormData();
      body.append('image', image);
      body.append('goal', JSON.stringify(form));
      const { run_id } = await api.startRun(body);
      setRunId(run_id);
    } catch (err) {
      setStartError(String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">🖼️ APEX</h1>
        <p className="text-sm text-gray-500">
          Agentic Portrait EXperience — turn a photo into a professional portrait, with a
          quality-assured loop.
        </p>
      </header>

      {loadError && <p className="text-red-600">Could not reach the API: {loadError}</p>}

      {!options && !loadError && <Spinner label="Loading…" />}

      {options &&
        (runId ? (
          <RunView runId={runId} onReset={() => setRunId(null)} />
        ) : (
          <GoalForm
            options={options}
            presets={presets}
            busy={busy}
            error={startError}
            onStart={start}
          />
        ))}
    </div>
  );
}
