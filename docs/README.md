# APEX Documentation

APEX (Agentic Portrait EXperience) turns a user's photo into a professional
portrait by **editing** it, inside a quality-assurance loop: one multimodal LLM
**orchestrates** the edits and **judges** the results, while **deterministic
metrics** — chiefly identity preservation — gate every iteration.

Start with the [project README](../README.md) for a quick tour, then dive in:

| Guide | What's inside |
|-------|----------------|
| [Architecture](architecture.md) | The loop, the layered package, data flow, run lifecycle, persistence schema |
| [Configuration](configuration.md) | Every `APEX_*` setting, defaults, and recommended profiles |
| [Models & backends](models.md) | gemma (vLLM) · Qwen-Image-Edit · FLUX · GGUF · Replicate · identity restoration · GPU topology |
| [Metrics & the loop](metrics.md) | The gates, thresholds, decision policy, edit-from-original, identity restore |
| [API reference](api.md) | Every endpoint, request/response shapes, the SSE event stream |
| [Development](development.md) | Setup, tests, lint/types, CI, project layout, extending the harness |
| [Deployment](deployment.md) | Docker Compose, GPU serving, runner/scaling, production notes |

## The one-paragraph mental model

A **`GoalSpec`** (purpose / attire / background / vibe + advanced settings) and an
input photo go to the **orchestrator** (an MLLM), which writes one edit
instruction. The **editor** (a diffusion model) applies it. The candidate is
scored by **deterministic metrics** (identity is a hard gate) and the **MLLM
judge**; a pure **decision policy** accepts (gates *and* judge agree), refines
(feed failures back), or stops (max-iters / repeated identity failure), always
returning the best iteration. Backends are pluggable (`local` / `api` / `fake`),
so the whole thing runs and is fully testable without a GPU.
