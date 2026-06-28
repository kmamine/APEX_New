#!/usr/bin/env bash
# Serve the APEX MLLM (orchestrator + judge) via vLLM, OpenAI-compatible.
# Adjust MODEL / PORT / GPU to taste; this mirrors the project's defaults.
set -euo pipefail

MODEL="${APEX_MLLM_MODEL:-google/gemma-4-E4B-it}"
PORT="${VLLM_PORT:-50033}"
API_KEY="${APEX_VLLM_API_KEY:-dummy-key}"
GPU="${VLLM_GPU:-0}"

echo "Serving ${MODEL} on :${PORT} (GPU ${GPU})"
CUDA_VISIBLE_DEVICES="${GPU}" vllm serve "${MODEL}" \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --api-key "${API_KEY}" \
    --gpu-memory-utilization 0.9 \
    --trust-remote-code
