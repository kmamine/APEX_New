"""Data structures describing a harness run and its iterations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from PIL import Image
from pydantic import BaseModel

from ..metrics.report import QualityReport
from ..mllm.schemas import JudgeResult


class Decision(StrEnum):
    ACCEPT = "accept"
    REFINE = "refine"
    STOP_MAX_ITERS = "stop_max_iters"
    STOP_IDENTITY_FAIL = "stop_identity_fail"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED_MAX_ITERS = "stopped_max_iters"
    STOPPED_IDENTITY = "stopped_identity"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IterationRecord(BaseModel):
    """Serializable record of one orchestrate -> edit -> evaluate -> decide step."""

    index: int
    instruction: str
    analysis: str = ""
    confidence: float = 0.0
    judge: JudgeResult
    metrics: QualityReport
    decision: Decision
    accepted: bool


@dataclass(slots=True)
class RunResult:
    """In-memory result of a run: serializable records plus the actual images."""

    status: RunStatus
    iterations: list[IterationRecord]
    iteration_images: list[Image.Image]
    final_image: Image.Image
    final_index: int
    input_image: Image.Image
    reference_images: list[Image.Image] = field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return self.status == RunStatus.COMPLETED

    @property
    def final_iteration(self) -> IterationRecord | None:
        if 0 <= self.final_index < len(self.iterations):
            return self.iterations[self.final_index]
        return None


__all__ = ["Decision", "IterationRecord", "RunResult", "RunStatus"]
