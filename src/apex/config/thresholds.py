"""Quality thresholds and loop policy — the knobs that gate the harness."""

from __future__ import annotations

from pydantic import BaseModel


class QualityThresholds(BaseModel):
    """Cutoffs each metric / the judge must clear. All env-overridable."""

    identity_threshold: float = 0.35  # ArcFace cosine vs the original photo (HARD gate)
    judge_threshold: float = 7.0  # MLLM-as-judge overall, 0-10
    sharpness_min: float = 100.0  # OpenCV Laplacian variance
    aesthetic_min: float = 5.0  # CLIP aesthetic predictor, ~0-10
    iqa_min: float = 0.0  # no-reference IQA (normalized; 0 disables)


class LoopPolicy(BaseModel):
    """How long and how forgivingly the refinement loop runs."""

    max_iterations: int = 5
    max_identity_fails: int = 2  # consecutive identity-gate failures before giving up


__all__ = ["LoopPolicy", "QualityThresholds"]
