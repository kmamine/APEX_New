"""Live MLLM checks against the gemma vLLM endpoint.

Marked ``network`` (skipped by default; CI runs ``-m 'not gpu and not network'``).
Run with: ``uv run pytest -m network``. Skips gracefully if the endpoint is down.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from PIL import Image

from apex.backends.openai_chat import OpenAICompatibleChatBackend
from apex.goalspec import goal_from_preset
from apex.goalspec.seed_prompt import (
    JUDGE_SYSTEM_PROMPT,
    ORCHESTRATOR_SYSTEM_PROMPT,
    build_judge_user_prompt,
    build_orchestrator_user_prompt,
)
from apex.mllm.schemas import JudgeResult, OrchestrationResult

pytestmark = pytest.mark.network

BASE_URL = "http://localhost:50033/v1"
API_KEY = "dummy-key"
MODEL = "google/gemma-4-E4B-it"
FACE = Path(__file__).resolve().parents[2] / "21007787.jpg"


def _endpoint_up() -> bool:
    try:
        httpx.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=3.0,
        )
        return True
    except httpx.HTTPError:
        return False


def _image() -> Image.Image:
    if FACE.exists():
        return Image.open(FACE).convert("RGB")
    return Image.new("RGB", (256, 256), (128, 128, 128))


def _chat() -> OpenAICompatibleChatBackend:
    return OpenAICompatibleChatBackend(
        base_url=BASE_URL, api_key=API_KEY, model=MODEL, temperature=0.3, max_tokens=512
    )


@pytest.mark.skipif(not _endpoint_up(), reason="gemma vLLM endpoint not reachable")
def test_real_orchestrator_returns_instruction() -> None:
    goal = goal_from_preset("LinkedIn Professional")
    plan = _chat().chat_structured(
        ORCHESTRATOR_SYSTEM_PROMPT,
        build_orchestrator_user_prompt(goal, None),
        [_image()],
        OrchestrationResult,
    )
    assert plan.next_edit.instruction.strip()
    assert 0.0 <= plan.confidence <= 1.0


@pytest.mark.skipif(not _endpoint_up(), reason="gemma vLLM endpoint not reachable")
def test_real_judge_scores_image() -> None:
    goal = goal_from_preset("LinkedIn Professional")
    verdict = _chat().chat_structured(
        JUDGE_SYSTEM_PROMPT, build_judge_user_prompt(goal), [_image()], JudgeResult
    )
    assert 0.0 <= verdict.overall <= 10.0
    assert isinstance(verdict.acceptable, bool)
