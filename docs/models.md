# Models & Backends

APEX depends on two model capabilities, kept behind small protocols
([`apex.backends.base`](../src/apex/backends/base.py)) so nothing in the loop,
harness, or tests imports torch/vLLM/Replicate directly:

- **`ChatBackend`** — a multimodal chat model that returns validated structured
  output (the orchestrator and judge).
- **`EditBackend`** — an image editor that transforms an image per a text
  instruction.

A `ModelBackend` bundles one of each. [`registry.build_backend(settings)`](../src/apex/backends/registry.py)
assembles them from config; the chat and editor backends are chosen
independently, so you can mix (e.g. a local editor with a hosted MLLM).

```
backend_mode = local | api | fake
  chat_backend  (override)  →  OpenAI-compatible chat client  | fake
  editor_backend (override) →  Qwen | FLUX | Replicate         | fake
```

## Chat / MLLM (orchestrator + judge)

One [`OpenAICompatibleChatBackend`](../src/apex/backends/openai_chat.py) serves
both `local` and `api` modes — they differ only by base URL. It:

- sends images as base64 `image_url` content parts,
- requests structured output via `response_format` `json_schema`,
- validates the reply against the Pydantic schema and **re-asks once** on a
  parse failure.

The verified model is **`google/gemma-4-E4B-it`** served by vLLM. Serve it with
[`scripts/run_vllm.sh`](../scripts/run_vllm.sh) (or `make vllm`):

```bash
CUDA_VISIBLE_DEVICES=1 vllm serve google/gemma-4-E4B-it \
  --host 0.0.0.0 --port 50033 --api-key dummy-key --trust-remote-code
```

Any OpenAI-compatible multimodal endpoint works — point `APEX_VLLM_BASE_URL` at
it. Verify with `uv run apex doctor`.

## Editor

`APEX_EDITOR_ENGINE` selects the local engine; `backend_mode=api` uses Replicate.

### Qwen-Image-Edit-2511 (default, `engine=qwen`)
Full weights via diffusers `QwenImageEditPlusPipeline`
([`editor_qwen.py`](../src/apex/backends/local/editor_qwen.py)). Apache-2.0,
~60 GB, ~20 GB VRAM. **Best identity preservation** of the editors tested.
Requires `torchvision` (the Qwen2.5-VL image processor needs it).

- **GGUF transformer** (smaller): set `APEX_EDITOR_GGUF_FILE` to a `.gguf`
  (e.g. a ~13 GB Q4_K_M from `unsloth/Qwen-Image-Edit-2511-GGUF`). The base repo
  still supplies the text encoder + VAE. 2511 GGUF loading is bleeding-edge and
  may require diffusers from git.

### FLUX.1-Kontext-dev (fallback, `engine=flux`)
Via `FluxKontextPipeline` ([`editor_flux.py`](../src/apex/backends/local/editor_flux.py)).
~24 GB, strong instruction editing, **non-commercial license**, gated on HF
(needs an accepted license + token). Drifts identity above guidance ~2.5 — pair
with identity restoration. Set:
```bash
APEX_EDITOR_ENGINE=flux
APEX_EDITOR_MODEL=black-forest-labs/FLUX.1-Kontext-dev
```

### Replicate (hosted, `backend_mode=api`)
[`editor_replicate.py`](../src/apex/backends/api/editor_replicate.py) — best-effort
adapter; confirm the model slug + input field names against the Replicate model
page. No local GPU; set `APEX_REPLICATE_API_TOKEN`.

### Fake (`backend_mode=fake`)
[`fake.py`](../src/apex/backends/fake.py) — deterministic, no GPU/network. The
chat ramps its judge score so runs converge; the editor applies a mild,
identity-preserving transform. Powers tests, CI, and the offline demo.

## Identity restoration

Diffusion editing regenerates the face, capping ArcFace similarity to the
original around ~0.5. With `APEX_IDENTITY_RESTORE=true`, after each edit
[`IdentityRestorer`](../src/apex/editor/identity_restore.py) runs InsightFace
`inswapper` to graft the **original** face's identity onto the portrait, applied
in the loop *before* scoring. This lifts identity similarity to **~0.9**.

The official inswapper download is dead, so weights are fetched from a HF mirror
(`APEX_INSWAPPER_REPO`, default `ezioruan/inswapper_128.onnx`). InsightFace +
`onnxruntime-gpu` require torch to be imported first (it provides the CUDA
runtime libraries) — the harness always loads the editor before metrics, so this
holds in practice. Trade-off: inswapper operates at 128 px, so on close zoom the
face can be marginally softer than the body; a face upscaler (GFPGAN/CodeFormer)
would be a natural future polish.

## GPU topology

The verified layout on a 2× H100 box:

| Device | Process |
|--------|---------|
| `cuda:1` | vLLM serving the gemma MLLM (separate process) |
| `cuda:0` | the editor pipeline + InsightFace (in the API process) |

`APEX_EDITOR_DEVICE` controls the editor's device; the harness never starts
vLLM — it only connects to `APEX_VLLM_BASE_URL`.

## Dependency extras

| Extra | Brings in |
|-------|-----------|
| *(core)* | pydantic, pillow, numpy, opencv, openai, fastapi, uvicorn, typer — runs the API + `fake` backend with no GPU |
| `local-gpu` | torch, torchvision, diffusers, transformers, accelerate, safetensors, insightface, onnxruntime-gpu, gguf, sentencepiece, protobuf |
| `api` | replicate |
| `quality` | pyiqa (aesthetic + no-reference IQA metrics; split out because it pins an ancient numba) |
| `dev` | pytest, ruff, mypy, pytest-httpx, pre-commit |
