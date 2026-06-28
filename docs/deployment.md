# Deployment

## Full-stack demo (no GPU)

The `fake` backend runs the whole pipeline deterministically, so the entire
stack is demoable anywhere via Docker Compose
([`docker-compose.yml`](../docker-compose.yml)):

```bash
docker compose up --build
# web on http://localhost:3000, API on http://localhost:8000 (fake backend)
```

- **api** — [`Dockerfile`](../Dockerfile), a `uv`-based image running
  `uvicorn apex.api.app:app`, `APEX_BACKEND_MODE=fake`, artifacts on a volume.
- **web** — [`web/Dockerfile`](../web/Dockerfile), a Node build served by nginx
  ([`web/nginx.conf`](../web/nginx.conf)) which proxies `/api` to the api
  service with SSE-friendly buffering off.

## Local GPU (real inference)

Real inference needs a CUDA host with the `local-gpu` extra and an external vLLM
server for the MLLM. The editor runs in-process via diffusers.

1. **Serve the MLLM** on one GPU (`make vllm` / [`scripts/run_vllm.sh`](../scripts/run_vllm.sh)):
   ```bash
   CUDA_VISIBLE_DEVICES=1 vllm serve google/gemma-4-E4B-it \
     --host 0.0.0.0 --port 50033 --api-key dummy-key --trust-remote-code
   ```
2. **Configure** (`.env`):
   ```bash
   APEX_BACKEND_MODE=local
   APEX_EDITOR_DEVICE=cuda:0
   APEX_VLLM_BASE_URL=http://localhost:50033/v1
   APEX_IDENTITY_RESTORE=true
   APEX_ENABLED_METRICS=identity,face,sharpness
   ```
3. **Pre-warm & check**: `uv run apex doctor` (verifies the endpoint + GPU).
4. **Run the API**: `make api` (or `uv run apex serve`). The Qwen weights
   (~60 GB) download on first use; subsequent runs are warm.

### GPU topology
`cuda:1` → vLLM (gemma); `cuda:0` → editor pipeline + InsightFace. See
[models.md](models.md#gpu-topology).

## Run execution & scaling

Long, GPU-bound edits run in a worker thread via the
[`InProcessRunner`](../src/apex/api/runner.py) so the API stays responsive;
progress fans out over SSE. GPU concurrency is effectively 1 (the editor
pipeline is shared and kept warm). For multi-worker scale, a queue-backed runner
(arq + Redis — the `queue` extra) is the intended next step; the service layer
([`ApexHarness`](../src/apex/service/harness.py)) is already decoupled from
FastAPI to make that swap clean.

## Frontend serving & SSE

In production the React build is served same-origin (nginx) and proxies `/api`
to the API, with response buffering **off** so SSE streams promptly
(`proxy_buffering off`). The web client also polls run status as a fallback, so
a buffering proxy degrades gracefully rather than hanging.

## Production notes

- **State** is on disk under `data/` (`profiles/`, `runs/<id>/`). Mount a volume;
  there is currently no automatic retention/cleanup.
- **No auth / multi-user** is built in — front it with your own auth/ingress.
- **Secrets** (`APEX_VLLM_API_KEY`, `APEX_REPLICATE_API_TOKEN`, `HF_TOKEN`) come
  from the environment; don't bake them into images.
- **Licensing**: Qwen-Image-Edit is Apache-2.0; FLUX.1-Kontext-dev is
  non-commercial and gated; confirm model licenses for your use.
