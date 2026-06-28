"""Request/response models for the FastAPI layer (the OpenAPI contract).

These are the single source of truth the React app's TypeScript types are
generated from, so keep them explicit and stable.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..goalspec import GoalSpec
from ..loop import RunStatus
from ..metrics.base import MetricResult
from ..mllm.schemas import JudgeResult
from ..persistence import RunState

API_PREFIX = "/api/v1"


class OptionDTO(BaseModel):
    value: str
    label: str
    icon: str


class OptionsResponse(BaseModel):
    fields: dict[str, list[OptionDTO]]


class PresetDTO(BaseModel):
    name: str
    purpose: str
    attire: str
    background: str
    vibe: str
    custom_notes: str
    description: str


class HealthResponse(BaseModel):
    status: str
    backend_mode: str
    mllm_model: str
    editor_model: str


class StartRunResponse(BaseModel):
    run_id: str
    status: RunStatus
    status_url: str
    events_url: str


class IterationDTO(BaseModel):
    index: int
    instruction: str
    analysis: str
    confidence: float
    decision: str
    accepted: bool
    overall: float
    identity: float | None
    image_url: str
    judge: JudgeResult
    metrics: list[MetricResult]


class RunDetailDTO(BaseModel):
    run_id: str
    status: RunStatus
    created_at: str
    updated_at: str
    current_iteration: int
    max_iterations: int
    final_index: int
    final_image_url: str | None
    error: str | None
    iterations: list[IterationDTO]
    goal: GoalSpec


def _iteration_image_url(run_id: str, index: int) -> str:
    return f"{API_PREFIX}/runs/{run_id}/iterations/{index}/image"


def build_run_detail(state: RunState) -> RunDetailDTO:
    iterations = [
        IterationDTO(
            index=record.index,
            instruction=record.instruction,
            analysis=record.analysis,
            confidence=record.confidence,
            decision=str(record.decision),
            accepted=record.accepted,
            overall=record.judge.overall,
            identity=(record.metrics.identity.value if record.metrics.identity else None),
            image_url=_iteration_image_url(state.run_id, record.index),
            judge=record.judge,
            metrics=record.metrics.results,
        )
        for record in state.iterations
    ]
    final_url = f"{API_PREFIX}/runs/{state.run_id}/final" if state.final_image else None
    return RunDetailDTO(
        run_id=state.run_id,
        status=state.status,
        created_at=state.created_at,
        updated_at=state.updated_at,
        current_iteration=state.current_iteration,
        max_iterations=state.max_iterations,
        final_index=state.final_index,
        final_image_url=final_url,
        error=state.error,
        iterations=iterations,
        goal=state.goal,
    )


def build_options_response() -> OptionsResponse:
    from ..goalspec import OPTIONS

    return OptionsResponse(
        fields={
            field: [OptionDTO(value=o.value, label=o.label, icon=o.icon) for o in opts]
            for field, opts in OPTIONS.items()
        }
    )


__all__ = [
    "API_PREFIX",
    "HealthResponse",
    "IterationDTO",
    "OptionDTO",
    "OptionsResponse",
    "PresetDTO",
    "RunDetailDTO",
    "StartRunResponse",
    "build_options_response",
    "build_run_detail",
]
