"""Run state model and its on-disk store (``run.json`` per run)."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import LoopPolicy, QualityThresholds
from ..goalspec import GoalSpec
from ..loop import IterationRecord, RunStatus


class RunState(BaseModel):
    """The full, serializable state of one harness run (persisted as run.json)."""

    run_id: str
    status: RunStatus = RunStatus.PENDING
    goal: GoalSpec
    created_at: str
    updated_at: str

    input_image: str  # filename within the run dir
    reference_images: list[str] = Field(default_factory=list)

    iterations: list[IterationRecord] = Field(default_factory=list)
    iteration_images: list[str] = Field(default_factory=list)  # parallel to iterations
    current_iteration: int = 0
    max_iterations: int = 0

    final_index: int = -1
    final_image: str | None = None
    error: str | None = None

    thresholds: QualityThresholds = Field(default_factory=QualityThresholds)
    policy: LoopPolicy = Field(default_factory=LoopPolicy)


class RunStore:
    """File-backed store of runs (``<runs_dir>/run_<id>/run.json``)."""

    def __init__(self, runs_dir: str | Path = "data/runs") -> None:
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id: str) -> Path:
        return self.runs_dir / f"run_{run_id}" / "run.json"

    def save(self, state: RunState) -> Path:
        path = self._path(state.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state.model_dump(mode="json"), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def load(self, run_id: str) -> RunState | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        try:
            return RunState.model_validate_json(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None

    def list(self) -> list[str]:
        return sorted(
            p.name.removeprefix("run_")
            for p in self.runs_dir.glob("run_*")
            if (p / "run.json").exists()
        )


__all__ = ["RunState", "RunStore"]
