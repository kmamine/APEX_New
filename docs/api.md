# API Reference

The FastAPI service is mounted under `/api/v1`. It is built by
[`apex.api.app:create_app`](../src/apex/api/app.py); the request/response models
live in [`apex.service.dto`](../src/apex/service/dto.py) and are the single
source of truth for the generated TypeScript types (`web/src/api/schema.gen.ts`).

Interactive docs are available at `/docs` (Swagger) and `/redoc` when the server
is running. Run it with `make api` (or `uv run uvicorn apex.api.app:app`).

CORS is open to the Vite dev origins (`:3000`, `:5173`); in production the
frontend is served same-origin behind a reverse proxy.

## Metadata

### `GET /api/v1/health`
```json
{ "status": "ok", "backend_mode": "local",
  "mllm_model": "google/gemma-4-E4B-it", "editor_model": "Qwen/Qwen-Image-Edit-2511" }
```

### `GET /api/v1/options`
Dropdown options for every goal field (value + label + emoji icon), so the UI
needn't hard-code them.
```json
{ "fields": { "purpose": [{"value":"LinkedIn","label":"💼 LinkedIn","icon":"💼"}, ...],
              "attire": [...], "background": [...], "vibe": [...],
              "lighting": [...], "mood": [...], "age_range": [...],
              "gender": [...], "ethnicity": [...], "resolution": [...] } }
```

### `GET /api/v1/presets`
The five built-in presets.
```json
[ { "name": "LinkedIn Professional", "purpose": "LinkedIn", "attire": "Business Formal",
    "background": "Corporate Office", "vibe": "Confident",
    "custom_notes": "…", "description": "…" }, ... ]
```

### `POST /api/v1/goal/validate`
Validate a flat goal payload before starting a run. Body is the form object
(`purpose`, `attire`, …, `custom_notes`).
```json
{ "is_valid": false, "message": "⚠️ Please select a purpose for your portrait",
  "missing_fields": ["purpose"] }
```

## Runs

### `POST /api/v1/runs` → `202`
Start a run. **multipart/form-data**:

| Field | Type | Notes |
|-------|------|-------|
| `image` | file (required) | The input photo. |
| `goal` | string (JSON) | Flat goal object — provide this *or* `preset`. |
| `preset` | string | A preset name — provide this *or* `goal`. |
| `reference_image` | file (optional) | Style/composition reference. |

```json
{ "run_id": "c9acfc2fea38", "status": "pending",
  "status_url": "/api/v1/runs/c9acfc2fea38",
  "events_url": "/api/v1/runs/c9acfc2fea38/events" }
```
Errors: `400` invalid image, `404` unknown preset, `422` invalid goal / neither provided.

```bash
curl -X POST http://localhost:8000/api/v1/runs \
  -F "preset=LinkedIn Professional" -F "image=@photo.jpg"
```

### `GET /api/v1/runs/{run_id}` → `RunDetail`
Full, hydrate-anytime snapshot of a run.
```jsonc
{
  "run_id": "…", "status": "completed",          // pending|running|completed|
                                                  // stopped_max_iters|stopped_identity|failed|cancelled
  "created_at": "…", "updated_at": "…",
  "current_iteration": 2, "max_iterations": 3,
  "final_index": 1,
  "input_image_url": "/api/v1/runs/…/input",
  "final_image_url": "/api/v1/runs/…/final",      // null until a final exists
  "error": null,
  "goal": { /* GoalSpec: basic_info / advanced_settings / additional_info / metadata */ },
  "iterations": [
    {
      "index": 0, "instruction": "…", "analysis": "…", "confidence": 0.7,
      "decision": "refine", "accepted": false,
      "overall": 8.5, "identity": 0.95,
      "image_url": "/api/v1/runs/…/iterations/0/image",
      "judge": { "scores": [{"criterion":"…","score":9,"comment":"…"}],
                 "overall": 8.5, "acceptable": false, "feedback": "…" },
      "metrics": [ {"name":"identity","value":0.95,"passed":true,"threshold":0.35,
                    "is_gate":true,"is_hard_gate":true,"detail":"…"}, ... ]
    }
  ]
}
```

### `GET /api/v1/runs/{run_id}/events` → SSE
Server-Sent Events for live progress. Subscribe, then hydrate via
`GET /runs/{id}` (the snapshot carries the full detail). Event types:

| Event | Data |
|-------|------|
| `snapshot` | The full `RunDetail` JSON at connect time (handles late-join / reconnect). |
| `iteration` | `{ "type":"iteration", "index", "decision", "accepted", "overall", "identity" }` |
| `done` | `{ "type":"done", "status", "final_index" }` |
| `cancelled` | `{ "type":"cancelled" }` |
| `failed` | `{ "type":"failed", "message" }` |

The stream closes when the run reaches a terminal state. (The web client also
polls `GET /runs/{id}` every few seconds as a fallback.)

### Images (static `image/png`)
- `GET /api/v1/runs/{run_id}/input` — the original upload.
- `GET /api/v1/runs/{run_id}/iterations/{index}/image` — a given iteration.
- `GET /api/v1/runs/{run_id}/final` — the chosen best/final portrait.

### `DELETE /api/v1/runs/{run_id}` → `RunDetail`
Best-effort cancel of an in-flight run.

## Profiles

Goal profiles persist as JSON (the legacy v2.0 shape, still loadable).

| Method & path | Body / returns |
|---------------|----------------|
| `GET /api/v1/profiles` | `["portrait_profile_20250720_013142.json", ...]` |
| `GET /api/v1/profiles/{filename}` | a `GoalSpec` |
| `POST /api/v1/profiles` | body: `GoalSpec` → `{ "filename": "…" }` |
| `DELETE /api/v1/profiles/{filename}` | `{ "deleted": true }` |

## Generating TypeScript types

The web client's types are generated from this contract:
```bash
cd web && npm run gen-types    # openapi-typescript http://localhost:8000/openapi.json -> src/api/schema.gen.ts
```
Run the server first. CI checks the generated file is not stale.
