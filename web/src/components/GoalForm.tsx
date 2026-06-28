import { useState } from 'react';
import type { GoalForm as GoalFormData, OptionsResponse, Preset } from '../api/types';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { Select } from './ui/Select';
import { Textarea } from './ui/Textarea';
import { ImageDropzone } from './ImageDropzone';

const DEFAULTS: GoalFormData = {
  purpose: '',
  attire: '',
  background: '',
  vibe: '',
  lighting: 'Professional Flash',
  mood: 'Professional',
  age_range: 'Not Specified',
  gender: 'Not Specified',
  ethnicity: 'Not Specified',
  resolution: '1024x1024 (Standard)',
  custom_notes: '',
};

const REQUIRED: (keyof GoalFormData)[] = ['purpose', 'attire', 'background', 'vibe'];

interface GoalFormProps {
  options: OptionsResponse;
  presets: Preset[];
  busy: boolean;
  error: string | null;
  onStart: (form: GoalFormData, image: File) => void;
}

export function GoalForm({ options, presets, busy, error, onStart }: GoalFormProps) {
  const [form, setForm] = useState<GoalFormData>(DEFAULTS);
  const [image, setImage] = useState<File | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  const set = (key: keyof GoalFormData, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const applyPreset = (name: string) => {
    const preset = presets.find((p) => p.name === name);
    if (!preset) return;
    setForm((prev) => ({
      ...prev,
      purpose: preset.purpose,
      attire: preset.attire,
      background: preset.background,
      vibe: preset.vibe,
      custom_notes: preset.custom_notes,
      preset_name: preset.name,
    }));
  };

  const submit = () => {
    setLocalError(null);
    if (!image) return setLocalError('Please upload a photo to transform.');
    const missing = REQUIRED.filter((key) => !form[key]);
    if (missing.length) return setLocalError(`Please choose: ${missing.join(', ')}.`);
    onStart(form, image);
  };

  const opt = (field: string) => options.fields[field] ?? [];

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="space-y-6">
        <Card title="1 · Your photo" description="The portrait is edited from this image.">
          <ImageDropzone file={image} onChange={setImage} />
        </Card>

        <Card title="2 · The goal" description="What should the portrait convey?">
          <div className="grid-responsive">
            <Select
              label="Purpose"
              options={opt('purpose')}
              placeholder="Select a purpose"
              value={form.purpose}
              onChange={(e) => set('purpose', e.target.value)}
            />
            <Select
              label="Attire"
              options={opt('attire')}
              placeholder="Select attire"
              value={form.attire}
              onChange={(e) => set('attire', e.target.value)}
            />
            <Select
              label="Background"
              options={opt('background')}
              placeholder="Select a background"
              value={form.background}
              onChange={(e) => set('background', e.target.value)}
            />
            <Select
              label="Vibe"
              options={opt('vibe')}
              placeholder="Select a vibe"
              value={form.vibe}
              onChange={(e) => set('vibe', e.target.value)}
            />
          </div>
        </Card>

        <Card title="3 · Advanced" description="Optional fine-tuning.">
          <div className="grid-responsive">
            <Select label="Lighting" options={opt('lighting')} value={form.lighting}
              onChange={(e) => set('lighting', e.target.value)} />
            <Select label="Mood" options={opt('mood')} value={form.mood}
              onChange={(e) => set('mood', e.target.value)} />
            <Select label="Age range" options={opt('age_range')} value={form.age_range}
              onChange={(e) => set('age_range', e.target.value)} />
            <Select label="Gender" options={opt('gender')} value={form.gender}
              onChange={(e) => set('gender', e.target.value)} />
            <Select label="Ethnicity" options={opt('ethnicity')} value={form.ethnicity}
              onChange={(e) => set('ethnicity', e.target.value)} />
            <Select label="Resolution" options={opt('resolution')} value={form.resolution}
              onChange={(e) => set('resolution', e.target.value)} />
          </div>
          <Textarea
            label="Custom notes"
            placeholder="Anything specific you'd like…"
            value={form.custom_notes}
            onChange={(e) => set('custom_notes', e.target.value)}
          />
        </Card>
      </div>

      <div className="space-y-6">
        <Card title="Presets" description="Start from a common look.">
          <div className="flex flex-col gap-2">
            {presets.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => applyPreset(preset.name)}
                className="rounded-lg border border-gray-200 p-3 text-left text-sm hover:border-primary-400 hover:bg-primary-50"
              >
                <div className="font-medium text-gray-800">{preset.name}</div>
                <div className="text-xs text-gray-500">{preset.description}</div>
              </button>
            ))}
          </div>
        </Card>

        <Card>
          {(localError || error) && (
            <p className="mb-3 text-sm text-red-600">{localError || error}</p>
          )}
          <Button size="lg" className="w-full" disabled={busy} onClick={submit}>
            {busy ? 'Starting…' : '✨ Generate portrait'}
          </Button>
        </Card>
      </div>
    </div>
  );
}
