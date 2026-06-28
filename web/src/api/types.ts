// Hand-maintained mirror of the FastAPI Pydantic DTOs (apex/service/dto.py).
// `npm run gen-types` regenerates the full schema into schema.gen.ts from the
// live server; this file is the curated surface the app codes against.

export type RunStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'stopped_max_iters'
  | 'stopped_identity'
  | 'failed'
  | 'cancelled';

export interface MetricResult {
  name: string;
  value: number;
  passed: boolean;
  threshold: number | null;
  is_gate: boolean;
  is_hard_gate: boolean;
  detail: string;
}

export interface CriterionScore {
  criterion: string;
  score: number;
  comment: string;
}

export interface JudgeResult {
  scores: CriterionScore[];
  overall: number;
  acceptable: boolean;
  feedback: string;
}

export interface Iteration {
  index: number;
  instruction: string;
  analysis: string;
  confidence: number;
  decision: string;
  accepted: boolean;
  overall: number;
  identity: number | null;
  image_url: string;
  judge: JudgeResult;
  metrics: MetricResult[];
}

export interface GoalSpec {
  basic_info: { purpose: string; attire: string; background: string; vibe: string };
  advanced_settings: {
    lighting: string;
    mood: string;
    age_range: string;
    gender: string;
    ethnicity: string;
    resolution: string;
  };
  additional_info: {
    reference_photo: string | null;
    custom_notes: string | null;
    preset_used: string | null;
  };
  metadata: { timestamp: string; version: string; created_by: string };
  generated_prompt: string | null;
}

export interface RunDetail {
  run_id: string;
  status: RunStatus;
  created_at: string;
  updated_at: string;
  current_iteration: number;
  max_iterations: number;
  final_index: number;
  input_image_url: string;
  final_image_url: string | null;
  error: string | null;
  iterations: Iteration[];
  goal: GoalSpec;
}

export interface Preset {
  name: string;
  purpose: string;
  attire: string;
  background: string;
  vibe: string;
  custom_notes: string;
  description: string;
}

export interface FieldOption {
  value: string;
  label: string;
  icon: string;
}

export interface OptionsResponse {
  fields: Record<string, FieldOption[]>;
}

export interface ValidationResult {
  is_valid: boolean;
  message: string;
  missing_fields: string[];
}

export interface StartRunResponse {
  run_id: string;
  status: RunStatus;
  status_url: string;
  events_url: string;
}

export interface GoalForm {
  purpose: string;
  attire: string;
  background: string;
  vibe: string;
  lighting: string;
  mood: string;
  age_range: string;
  gender: string;
  ethnicity: string;
  resolution: string;
  custom_notes: string;
  preset_name?: string;
}

export const TERMINAL_STATUSES: RunStatus[] = [
  'completed',
  'stopped_max_iters',
  'stopped_identity',
  'failed',
  'cancelled',
];
