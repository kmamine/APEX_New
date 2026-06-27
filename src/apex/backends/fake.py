"""A GPU-free, deterministic backend for tests, CI, and offline demos.

The fake chat ramps its judge scores across calls so a run converges in a few
iterations; the fake editor applies a mild, identity-preserving enhancement (or
a caller-supplied transform, to exercise the identity gate in tests).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import cast

from PIL import Image, ImageEnhance
from pydantic import BaseModel

from .base import EditRequest, EditResult, ModelBackend, TModel


class FakeChatBackend:
    """Returns canned, schema-valid structured output without any model."""

    def __init__(self, *, base_overall: float = 5.0, step: float = 2.0, accept_at: float = 8.0):
        self._base_overall = base_overall
        self._step = step
        self._accept_at = accept_at
        self._judge_calls = 0

    def chat_structured(
        self,
        system: str,
        user: str,
        images: Sequence[Image.Image],
        schema: type[TModel],
    ) -> TModel:
        from ..mllm.schemas import (
            CriterionScore,
            EditInstruction,
            JudgeResult,
            OrchestrationResult,
        )

        if schema is OrchestrationResult:
            result: BaseModel = OrchestrationResult(
                analysis="Adjust attire, background and lighting toward the brief.",
                next_edit=EditInstruction(
                    instruction="Apply the requested professional attire, background and lighting.",
                    rationale="Moves the image toward the target brief.",
                ),
                confidence=0.7,
            )
        elif schema is JudgeResult:
            self._judge_calls += 1
            overall = min(10.0, self._base_overall + self._step * (self._judge_calls - 1))
            result = JudgeResult(
                scores=[CriterionScore(criterion="overall", score=overall)],
                overall=overall,
                acceptable=overall >= self._accept_at,
                feedback="Increase lighting contrast and refine the background.",
            )
        else:  # best-effort default for any other schema
            result = schema()
        return cast(TModel, result)


def _mild_enhance(image: Image.Image) -> Image.Image:
    out = ImageEnhance.Contrast(image.convert("RGB")).enhance(1.05)
    return ImageEnhance.Brightness(out).enhance(1.02)


class FakeEditBackend:
    """Returns a deterministically transformed image (identity-preserving by default)."""

    def __init__(self, transform: Callable[[Image.Image], Image.Image] | None = None):
        self._transform = transform or _mild_enhance

    def edit_image(self, request: EditRequest) -> EditResult:
        image = self._transform(request.input_image)
        if request.width and request.height:
            image = image.resize((request.width, request.height))
        return EditResult(image=image, seed_used=request.seed or 0, meta={"backend": "fake"})


def fake_backend() -> ModelBackend:
    return ModelBackend(chat=FakeChatBackend(), editor=FakeEditBackend())


__all__ = ["FakeChatBackend", "FakeEditBackend", "fake_backend"]
