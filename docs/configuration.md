# Configuration

All configuration is environment-driven. Settings load (in precedence order)
from process environment variables, then a local `.env` file, then code
defaults. Every variable is prefixed `APEX_` and maps to a field on
[`apex.config.Settings`](../src/apex/config/settings.py). Copy
[`.env.example`](../.env.example) to `.env` and edit.

```python
from apex.config import get_settings
settings = get_settings()   # process-wide, cached
```

## UI / server

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_HOST` | `127.0.0.1` | Bind host for the API server. |
| `APEX_PORT` | `8000` | Bind port for the API server. |
| `APEX_SHARE` | `false` | Reserved (legacy share flag). |
| `APEX_PROFILES_DIR` | `data/profiles` | Where saved goal profiles (JSON) live. |
| `APEX_UPLOADS_DIR` | `data/uploads` | Reserved for uploaded assets. |
| `APEX_RUNS_DIR` | `data/runs` | Per-run artifacts (`run_<id>/` with images + `run.json`). |
| `APEX_AUTO_SAVE` | `true` | Auto-save the goal as a profile when a run completes. |

## Backend selection

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_BACKEND_MODE` | `local` | `local` (vLLM + diffusers), `api` (hosted), or `fake` (no GPU/network). |
| `APEX_CHAT_BACKEND` | *(unset → `backend_mode`)* | Override just the chat (MLLM) backend. |
| `APEX_EDITOR_BACKEND` | *(unset → `backend_mode`)* | Override just the editor backend (e.g. local editor + hosted chat). |

## MLLM (orchestrator + judge)

The chat model is reached through an OpenAI-compatible endpoint (the same client
serves a local vLLM server and hosted APIs).

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_VLLM_BASE_URL` | `http://localhost:50033/v1` | OpenAI-compatible base URL. |
| `APEX_VLLM_API_KEY` | `dummy-key` | API key/token (vLLM accepts any non-empty value by default). |
| `APEX_MLLM_MODEL` | `google/gemma-4-E4B-it` | Model id served at the endpoint. |
| `APEX_MLLM_TEMPERATURE` | `0.4` | Sampling temperature for orchestrator/judge. |
| `APEX_MLLM_MAX_TOKENS` | `1024` | Max output tokens per structured call. |

## Image editor

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_EDITOR_ENGINE` | `qwen` | `qwen` (Qwen-Image-Edit) or `flux` (FLUX.1-Kontext-dev fallback). |
| `APEX_EDITOR_MODEL` | `Qwen/Qwen-Image-Edit-2511` | HF model id. For FLUX set `black-forest-labs/FLUX.1-Kontext-dev`. |
| `APEX_EDITOR_GGUF_FILE` | *(unset)* | Optional GGUF transformer for Qwen (smaller download); base repo still supplies text-encoder + VAE. |
| `APEX_EDITOR_DEVICE` | `cuda:0` | CUDA device for the editor pipeline (MLLM/vLLM is assumed on the other GPU). |
| `APEX_NUM_INFERENCE_STEPS` | `50` | Diffusion steps per edit. |
| `APEX_TRUE_CFG_SCALE` | `4.0` | Qwen `true_cfg_scale`. |
| `APEX_EDITOR_GUIDANCE_SCALE` | `2.5` | FLUX guidance scale (above ~2.5 the face drifts). |
| `APEX_EDITOR_STYLE_SUFFIX` | *(photographic anchor)* | Appended to every edit instruction for a clean, natural-skin look. The semantic edit still comes from the orchestrator. |
| `APEX_REPLICATE_API_TOKEN` | *(unset)* | Token for the hosted Replicate editor (`backend_mode=api`). |

## Quality thresholds & loop policy

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_IDENTITY_THRESHOLD` | `0.35` | ArcFace cosine (vs the **original** photo) below which an iteration fails the **hard** gate. With identity restoration on, runs land ~0.9, so you can raise this (e.g. `0.8`) to enforce a strict bar. |
| `APEX_JUDGE_THRESHOLD` | `7.0` | Minimum MLLM-judge overall score (0–10) to accept. |
| `APEX_SHARPNESS_MIN` | `100.0` | Minimum OpenCV Laplacian variance (soft gate). |
| `APEX_AESTHETIC_MIN` | `5.0` | Aesthetic floor (informational; needs the `quality` extra). |
| `APEX_IQA_MIN` | `0.0` | No-reference IQA floor (informational; needs the `quality` extra). |
| `APEX_MAX_ITERATIONS` | `5` | Maximum refine iterations before returning the best result. |
| `APEX_MAX_IDENTITY_FAILS` | `2` | Consecutive identity-gate failures before stopping the run. |
| `APEX_EDIT_FROM_ORIGINAL` | `true` | Edit the original photo each iteration (one clean transform, no drift) instead of compounding edits. |
| `APEX_ENABLED_METRICS` | *(unset → all)* | Comma-separated subset, e.g. `identity,face,sharpness`. |

## Identity restoration

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_IDENTITY_RESTORE` | `false` | After each edit, graft the original face's identity onto the portrait (InsightFace `inswapper`). Lifts identity similarity from ~0.5 to ~0.9. Needs the `local-gpu` extra. |
| `APEX_INSWAPPER_REPO` | `ezioruan/inswapper_128.onnx` | HF repo for the inswapper weights (the official URL is dead). |
| `APEX_INSWAPPER_FILE` | `inswapper_128.onnx` | File within that repo. |

## Misc

| Variable | Default | Description |
|----------|---------|-------------|
| `APEX_MODEL_CACHE` | `models` | Local cache hint for model assets. |

> Hugging Face downloads (Qwen/FLUX/insightface) honor the standard `HF_HOME` /
> `HF_HUB_CACHE` / `HF_TOKEN` environment variables.

## Recommended profiles

**GPU-free dev / CI / demo** — full pipeline, deterministic, no models:
```bash
APEX_BACKEND_MODE=fake
```

**Local GPU (the verified setup)** — gemma on `cuda:1`, editor on `cuda:0`,
identity restoration on, soft metrics that need no extra HF models:
```bash
APEX_BACKEND_MODE=local
APEX_EDITOR_ENGINE=qwen
APEX_EDITOR_DEVICE=cuda:0
APEX_VLLM_BASE_URL=http://localhost:50033/v1
APEX_IDENTITY_RESTORE=true
APEX_ENABLED_METRICS=identity,face,sharpness
APEX_IDENTITY_THRESHOLD=0.8     # enforce strong likeness (restoration lands ~0.9)
```

**FLUX fallback** (if Qwen weights are impractical):
```bash
APEX_EDITOR_ENGINE=flux
APEX_EDITOR_MODEL=black-forest-labs/FLUX.1-Kontext-dev
```

**Hosted API** (no local GPU):
```bash
APEX_BACKEND_MODE=api
APEX_VLLM_BASE_URL=https://your-openai-compatible-endpoint/v1
APEX_VLLM_API_KEY=...
APEX_REPLICATE_API_TOKEN=...
```
