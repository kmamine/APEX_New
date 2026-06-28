# Development

## Setup

Python is managed with [`uv`](https://docs.astral.sh/uv/); the frontend needs
Node 18+ (Node ships in the project's conda env if you use one).

```bash
make install        # uv sync core + dev (no GPU stacks)
make install-gpu    # + local-gpu, api, queue extras (for real inference)
cd web && npm install
```

Common tasks (see the [`Makefile`](../Makefile)):

| Command | Action |
|---------|--------|
| `make test` | GPU-free suite (`pytest -m "not gpu and not network"`) |
| `make lint` / `make format` | ruff check / autofix + format |
| `make type` | mypy |
| `make api` | run the FastAPI server (reads `.env`) |
| `make web` | run the Vite dev server (`:3000`, proxies `/api`) |
| `make gen-types` | regenerate `web/src/api/schema.gen.ts` from the live OpenAPI schema |
| `make vllm` | serve the gemma MLLM via vLLM |
| `make demo` | end-to-end run on the `fake` backend |

> The Vite dev proxy targets `http://localhost:8000`; override with
> `VITE_API_TARGET` if the API runs elsewhere.

## Project layout

```
src/apex/
  goalspec/      typed GoalSpec — enums, options, presets, validation,
                 detail dictionaries, MLLM seed prompts
  config/        env-driven Settings, QualityThresholds, LoopPolicy
  backends/      ChatBackend + EditBackend protocols, registry, fake;
                 openai_chat; local/{editor_qwen,editor_flux}; api/editor_replicate
  mllm/          structured schemas, Orchestrator, Judge
  editor/        ImageEditor wrapper, IdentityRestorer (inswapper)
  metrics/       Metric base, identity/face/sharpness/aesthetic/iqa, report, registry
  loop/          IterationRecord/RunResult, pure decision policy, AgenticLoop engine
  persistence/   ProfileStore, RunStore (run.json), RunArtifacts (images)
  service/       ApexHarness (FastAPI-agnostic), API DTOs
  api/           FastAPI app, routes, InProcessRunner (SSE)
  cli.py         apex run / serve / doctor
web/src/         React app (api client + useRunStream, GoalForm, RunView, ui/)
tests/           unit/ (GPU-free) + integration/ (gpu/network markers)
```

The dependency direction is strictly inward: inner layers (`goalspec`, `config`)
never import outer ones (`api`, `service`), and everything talks to the backend
*protocols*, never to torch/vLLM directly. That's what lets the `fake` backend
exercise the entire stack with no GPU.

## Testing

```bash
uv run pytest -m "not gpu and not network"   # default — fast, no models
uv run pytest -m network                      # live MLLM checks against :50033
uv run pytest -m gpu                           # heavy editor/metric checks (needs hardware)
```

- **Unit tests** cover the GoalSpec/validation/presets (including legacy v2.0
  JSON round-trips), the pure metrics, the decision policy, the loop engine, and
  the full API lifecycle — all against the `fake` backend, so CI runs them with
  no GPU.
- **Integration tests** (`tests/integration/`) are marked `network`/`gpu` and
  skip gracefully when the endpoint/hardware is absent.

## CI

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs two GPU-free jobs
on every push/PR:

- **python** — `ruff check`, `ruff format --check`, `mypy`, GPU-free `pytest`.
- **web** — `npm ci`, `npm run type-check`, `npm run build`.

## Extending the harness

**Add a metric** — subclass [`Metric`](../src/apex/metrics/base.py), implement
`_measure(original, candidate) -> (value, detail)`, set `is_gate` /
`is_hard_gate`, register it in [`metrics/registry.py`](../src/apex/metrics/registry.py).

**Add an editor backend** — implement `edit_image(EditRequest) -> EditResult`
([`backends/base.py`](../src/apex/backends/base.py)) with lazy heavy imports, and
wire it into [`backends/registry.py`](../src/apex/backends/registry.py).

**Add a chat backend** — implement `chat_structured(system, user, images, schema)`
returning a validated Pydantic instance.

**Change orchestrator/judge behavior** — edit the prompts and schemas in
[`goalspec/seed_prompt.py`](../src/apex/goalspec/seed_prompt.py) and
[`mllm/schemas.py`](../src/apex/mllm/schemas.py).

## Frontend ↔ backend types

The Pydantic DTOs are the source of truth. After changing them, regenerate the
TS types (`make gen-types`) — CI fails if `schema.gen.ts` is stale. The
hand-written `web/src/api/types.ts` is the curated surface the components use.

## Conventions

- Keep code GPU-free to import (defer torch/diffusers/insightface to first use).
- Run `make lint type test` before committing.
- Commits are authored by the repo owner only (no co-authors).
