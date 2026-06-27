"""Deterministic, model-opinion-free metrics that gate the harness loop.

Identity preservation is the hard gate; face presence and sharpness are soft
gates; aesthetic and no-reference IQA are informational. Heavy models load
lazily so importing this package never requires a GPU.
"""

from .base import Metric, MetricResult
from .face import FacePresence
from .identity import IdentityPreservation, StubIdentity
from .registry import DEFAULT_METRICS, build_metrics, evaluate_image
from .report import QualityReport, build_report
from .sharpness import Sharpness

__all__ = [
    "DEFAULT_METRICS",
    "FacePresence",
    "IdentityPreservation",
    "Metric",
    "MetricResult",
    "QualityReport",
    "Sharpness",
    "StubIdentity",
    "build_metrics",
    "build_report",
    "evaluate_image",
]
