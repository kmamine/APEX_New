"""Deterministic metric base class and per-metric result type."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image
from pydantic import BaseModel


class MetricResult(BaseModel):
    """One metric's verdict on a candidate image (serializable into run JSON)."""

    name: str
    value: float
    passed: bool
    threshold: float | None = None
    is_gate: bool = True  # contributes to the accept gate
    is_hard_gate: bool = False  # a failure here blocks the iteration outright (identity)
    detail: str = ""


class Metric(ABC):
    """A deterministic, model-opinion-free image metric.

    Subclasses implement :meth:`_measure`; the base handles pass/fail logic so
    every metric reports a uniform :class:`MetricResult`.
    """

    name: str = "metric"
    is_gate: bool = True
    is_hard_gate: bool = False

    def __init__(self, threshold: float, *, higher_is_better: bool = True) -> None:
        self.threshold = threshold
        self.higher_is_better = higher_is_better

    @abstractmethod
    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        """Return ``(value, detail)`` for the candidate (vs. the original)."""

    def _passed(self, value: float) -> bool:
        return value >= self.threshold if self.higher_is_better else value <= self.threshold

    def compute(self, original: Image.Image, candidate: Image.Image) -> MetricResult:
        value, detail = self._measure(original, candidate)
        return MetricResult(
            name=self.name,
            value=value,
            passed=self._passed(value),
            threshold=self.threshold,
            is_gate=self.is_gate,
            is_hard_gate=self.is_hard_gate,
            detail=detail,
        )


__all__ = ["Metric", "MetricResult"]
