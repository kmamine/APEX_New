# APEX — Agentic Portrait EXperience

> Turn a photo into a polished professional portrait — with a harness that *proves* the result is good.

APEX takes a user's photo and a structured **goal** (purpose, attire, background, vibe, …) and produces a professional portrait by **editing** the photo (image-to-image, never generating a stranger's face). A multimodal LLM **orchestrates** each edit and **judges** the result, while **deterministic metrics** — chiefly identity preservation — gate every iteration. The loop refines until the portrait clears a quality bar or the budget is spent, then returns the best iteration.

```
Input photo  (+ goal)
   ↓
MLLM Orchestrator ──→ Qwen-Image-Edit ──→ candidate
   ↓                                          ↓
   └────────── refine ◀── Decision ◀── Evaluation
                                        ├─ deterministic metrics (identity = hard gate)
                                        └─ MLLM-as-judge (per-criterion scores)
   ↓ (accept / max-iters)
Final portrait
```

## Why it's interesting

- **Image-to-image, identity-first.** Edits the real photo; an ArcFace identity gate (measured against the *original*) blocks drift, so the output is always recognizably *you*.
- **One MLLM, two jobs.** `google/gemma-4-E4B-it` (served via vLLM) both plans the next edit and scores the result, using structured JSON output.
- **Metrics, not vibes.** Quality is gated by deterministic signals (identity, face presence, sharpness, aesthetic, no-reference IQA) *and* the judge — they must agree to accept.
- **Pluggable backends.** Run fully local (vLLM + diffusers on GPU), against hosted APIs, or with a `fake` backend that needs no GPU — the whole stack is demoable and testable without hardware.
- **Full-stack.** A FastAPI service streams iteration progress (SSE) to a React app that shows the edit loop live.

## Status

Under active reformulation from the legacy `APEX_old/` reference (a form → static-prompt tool). See the build plan and `CLAUDE.md` for architecture. Milestones are tracked in the implementation plan.

## Quick start (no GPU)

```bash
make install          # uv sync core + dev
make test             # GPU-free suite
APEX_BACKEND_MODE=fake make api   # FastAPI on the fake backend
make web              # React dev server
```

## Local GPU run

```bash
make install-gpu
make vllm             # serve the gemma MLLM (localhost:50033)
APEX_BACKEND_MODE=local uv run apex run --image photo.jpg --preset "LinkedIn Professional"
```

## License

MIT — see [LICENSE](LICENSE).
