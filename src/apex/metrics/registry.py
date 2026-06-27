"""Build the active metric set and run it over a candidate image."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal

from PIL import Image

from ..config import QualityThresholds
from .aesthetic import AestheticScore
from .base import Metric
from .face import FacePresence
from .identity import IdentityPreservation, StubIdentity
from .iqa import NoReferenceIQA
from .report import QualityReport, build_report
from .sharpness import Sharpness

#: Default order metrics run in (cheap/hard gates first).
DEFAULT_METRICS = ["identity", "face", "sharpness", "aesthetic", "iqa"]

IdentityImpl = Literal["real", "stub"]


def build_metrics(
    thresholds: QualityThresholds,
    enabled: Sequence[str] | None = None,
    *,
    identity_impl: IdentityImpl = "real",
    device: str = "cpu",
) -> list[Metric]:
    """Construct the enabled metrics (lazy heavy models are not loaded here)."""
    catalog: dict[str, Callable[[], Metric]] = {
        "identity": lambda: (
            StubIdentity(thresholds.identity_threshold)
            if identity_impl == "stub"
            else IdentityPreservation(thresholds.identity_threshold)
        ),
        "face": lambda: FacePresence(),
        "sharpness": lambda: Sharpness(thresholds.sharpness_min),
        "aesthetic": lambda: AestheticScore(thresholds.aesthetic_min, device=device),
        "iqa": lambda: NoReferenceIQA(thresholds.iqa_min, device=device),
    }
    names = list(enabled) if enabled is not None else DEFAULT_METRICS
    return [catalog[name]() for name in names if name in catalog]


def evaluate_image(
    metrics: Sequence[Metric], original: Image.Image, candidate: Image.Image
) -> QualityReport:
    """Run every metric and aggregate into a :class:`QualityReport`."""
    return build_report([m.compute(original, candidate) for m in metrics])


__all__ = ["DEFAULT_METRICS", "IdentityImpl", "build_metrics", "evaluate_image"]
