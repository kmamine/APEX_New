"""Aggregate metric results into a gating quality report."""

from __future__ import annotations

from pydantic import BaseModel

from .base import MetricResult


class QualityReport(BaseModel):
    """Aggregated deterministic metrics for one candidate image."""

    results: list[MetricResult]

    @property
    def identity(self) -> MetricResult | None:
        return next((r for r in self.results if r.is_hard_gate), None)

    @property
    def identity_passed(self) -> bool:
        """The hard gate. Absent identity metric => treated as passing."""
        identity = self.identity
        return identity.passed if identity is not None else True

    @property
    def soft_gates_passed(self) -> bool:
        """All non-hard gate metrics pass."""
        return all(r.passed for r in self.results if r.is_gate and not r.is_hard_gate)

    @property
    def failures(self) -> list[str]:
        """Human-readable descriptions of every gate that failed."""
        out: list[str] = []
        for r in self.results:
            if r.is_gate and not r.passed:
                tag = "identity" if r.is_hard_gate else r.name
                out.append(f"{tag}: {r.value:.3f} (threshold {r.threshold}) — {r.detail}".strip())
        return out

    def score(self, key: str) -> float | None:
        return next((r.value for r in self.results if r.name == key), None)


def build_report(results: list[MetricResult]) -> QualityReport:
    return QualityReport(results=results)


__all__ = ["QualityReport", "build_report"]
