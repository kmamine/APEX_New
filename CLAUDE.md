# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

`APEX_New` is a fresh rewrite of APEX and is currently near-empty — only [README.md](README.md) and a single "Initial commit". The complete previous implementation lives in the **untracked** [APEX_old/](APEX_old/) directory (its own git repo, origin `github.com/kmamine/APEX_old.git`) and is the reference for the rewrite.

- When asked to build a feature, read the corresponding code in `APEX_old/` first — it is the canonical starting point, not something to design from scratch.
- Do **not** commit `APEX_old/` into this repo unless explicitly asked; it is reference material.

## What APEX is

APEX (Agentic Portrait EXperience) is an **agentic harness that turns a user's input photo into a polished professional portrait, with a built-in quality-assurance loop**. It is **image-to-image, not text-to-image**: the user supplies a photo of themselves and the system *edits* it into a portrait while preserving their identity. The harness has two jobs — (1) **generate** the portrait, and (2) **assure quality** by measuring each result and iterating until it clears a bar.

### Target pipeline (APEX_New)

```
Input photo  (+ goal: purpose / attire / vibe / background)
   ↓
MLLM Orchestrator   ── analyzes the image + goal, plans the next edit instruction
   ↓
Qwen/Qwen-Image-Edit-2511   ── applies the edit (image → edited image)
   ↓
Evaluation harness
   ├─ MLLM-as-judge        (subjective: does attire / background / vibe match the goal?)
   └─ Deterministic metrics (objective, model-opinion-free — see below)
   ↓
MLLM Orchestrator   ── accept, or refine: loop back with a revised edit instruction
   ↓   (loop until quality threshold met or max iterations)
Final portrait
```

### Core design decisions (new — these supersede the APEX_old plan)

- **One MLLM (multimodal LLM) does both orchestration and judging.** It drives the loop — choosing the next edit and deciding when the result is good enough — and serves as the subjective judge. Served via vLLM behind an OpenAI-compatible API; candidate models are listed in [APEX_old/VLM-Guide.md](APEX_old/VLM-Guide.md).
- **`Qwen/Qwen-Image-Edit-2511` is the image editor.** This replaces APEX_old's planned Flux *generation* step. APEX edits an existing photo rather than generating a face from scratch — that is what makes identity preservation a meaningful, measurable goal.
- **Metrics are not only LLM-as-judge.** The quality bar combines the MLLM's subjective verdict with **deterministic metrics** that don't depend on a model's opinion. The central one is **identity preservation** (input-vs-output face-embedding similarity), since the output must stay a portrait of *this* user; other candidates: face detection / single-subject check, sharpness/blur, artifact detection, resolution, aesthetic score. These give a reproducible signal that gates the loop alongside the judge. (Exact metric set is an open design decision.)
- **The loop architecture is being refined** — the orchestrate → edit → evaluate → decide cycle above, with explicit accept/refine/stop conditions, is the shape to build toward.

**Current state:** none of this is implemented yet — `APEX_New` is an empty repo and `APEX_old` contains only the form → profile → template-prompt front end (no model calls, no editing, no loop). Treat the pipeline above as the target to build, not existing behavior.

## Reference scaffolding (`APEX_old`) — reuse vs. discard

`APEX_old` predates the image-to-image direction, so it is only a **partial** reference:

- **Reusable:** the goal/profile schema (`ProfileData`: purpose / attire / background / vibe + advanced settings), the built-in presets, the env-driven config pattern, and the dual Gradio/React front-ends for collecting the user's goal.
- **Superseded:** `core/prompt_generator.py` (template→text-prompt) and the Flux *generation* plan — the new core is image **editing** (Qwen-Image-Edit) driven by an MLLM orchestrator with a metrics-gated loop, all of which is net-new and not present in `APEX_old`.

Two parallel front-ends sit over one shared profile schema:

- **Python package `apex/`** (v2.0.0) with a Gradio UI; entry point [APEX_old/app.py](APEX_old/app.py) → serves at `http://127.0.0.1:7860`.
- **React web app `web-app/`** (Vite + TypeScript + Tailwind) → `http://localhost:3000`; runs purely client-side and exports the same JSON (no backend call).

**The contract between them is the `ProfileData` JSON schema** (`basic_info` / `advanced_settings` / `additional_info` / `metadata` / `generated_prompt`). It is defined **twice** — in [APEX_old/apex/models/profile.py](APEX_old/apex/models/profile.py) and [APEX_old/web-app/src/types/index.ts](APEX_old/web-app/src/types/index.ts) — and the validation rules and presets are duplicated too ([profile_manager.py](APEX_old/apex/core/profile_manager.py) ↔ [web-app/src/utils/profileManager.ts](APEX_old/web-app/src/utils/profileManager.ts)). Any change to fields, validation, or presets must be mirrored on both sides.

Python module roles:
- `config/settings.py` — dataclass config with env-var overrides (`APEX_PORT`, `APEX_HOST`, `APEX_SHARE`, `APEX_PROFILES_DIR`, `APEX_UPLOADS_DIR`, `APEX_AUTO_SAVE`); exposes a global `config` instance.
- `models/profile.py` — `ProfileData` dataclasses + a `Profile` static-method class for validation/creation.
- `core/profile_manager.py` — create/validate/save(JSON)/load/list/delete profiles, plus built-in presets (LinkedIn Professional, Creative Portfolio, Academic, Startup Founder, Executive).
- `core/prompt_generator.py` — maps form selections to a text prompt string (superseded by the image-editing core; kept only as reference).
- `ui/gradio_interface.py` — the Gradio interface (`create_interface`).
- Profiles persist as JSON under `data/profiles/`.

## Commands

`APEX_New` has no build system yet; these run inside `APEX_old/` (or wherever rewritten code lands).

Python backend:
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # or requirements-minimal.txt on dependency conflicts
python app.py                            # launch Gradio UI on :7860
python -m pytest tests/                  # full test suite (unittest-style, run via pytest)
python -m pytest tests/test_basic.py::TestPromptGenerator::test_generate_prompt   # single test
black apex/                              # format
```

React web app (from `web-app/`):
```bash
npm install
npm run dev          # dev server on :3000
npm run build        # tsc + vite build
npm run lint
npm run type-check   # tsc --noEmit
```
