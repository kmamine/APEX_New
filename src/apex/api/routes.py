"""HTTP routes for the APEX API (mounted under ``/api/v1``)."""

from __future__ import annotations

import io
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from sse_starlette.sse import EventSourceResponse

from ..goalspec import (
    GoalSpec,
    ValidationResult,
    goal_from_form,
    goal_from_preset,
    validate_goal_form,
)
from ..persistence import RunArtifacts
from ..service.dto import (
    API_PREFIX,
    HealthResponse,
    PresetDTO,
    RunDetailDTO,
    StartRunResponse,
    build_options_response,
    build_run_detail,
)
from ..service.harness import ApexHarness
from .runner import TERMINAL, InProcessRunner

router = APIRouter(prefix=API_PREFIX)


def get_harness(request: Request) -> ApexHarness:
    return request.app.state.harness


def get_runner(request: Request) -> InProcessRunner:
    return request.app.state.runner


def _read_image(data: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="invalid image upload") from exc


# --- metadata ----------------------------------------------------------
@router.get("/health", response_model=HealthResponse)
def health(harness: ApexHarness = Depends(get_harness)) -> HealthResponse:
    s = harness.settings
    return HealthResponse(
        status="ok",
        backend_mode=s.backend_mode,
        mllm_model=s.mllm_model,
        editor_model=s.editor_model,
    )


@router.get("/options")
def options() -> dict:
    return build_options_response().model_dump()


@router.get("/presets", response_model=list[PresetDTO])
def presets(harness: ApexHarness = Depends(get_harness)) -> list[PresetDTO]:
    return [PresetDTO(**preset.model_dump()) for preset in harness.presets()]


@router.post("/goal/validate", response_model=ValidationResult)
def validate(payload: dict, harness: ApexHarness = Depends(get_harness)) -> ValidationResult:
    return harness.validate(payload)


# --- runs --------------------------------------------------------------
@router.post("/runs", response_model=StartRunResponse, status_code=202)
async def start_run(
    image: UploadFile = File(...),
    goal: str | None = Form(None),
    preset: str | None = Form(None),
    reference_image: UploadFile | None = File(None),
    harness: ApexHarness = Depends(get_harness),
    runner: InProcessRunner = Depends(get_runner),
) -> StartRunResponse:
    if preset:
        try:
            goal_spec: GoalSpec = goal_from_preset(preset)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"unknown preset: {preset}") from exc
    elif goal:
        data = json.loads(goal)
        result = validate_goal_form(data)
        if not result.is_valid:
            raise HTTPException(status_code=422, detail=result.message)
        goal_spec = goal_from_form(data)
    else:
        raise HTTPException(status_code=422, detail="provide either 'goal' or 'preset'")

    input_image = _read_image(await image.read())
    references = [_read_image(await reference_image.read())] if reference_image else []

    run_id = await runner.start(goal_spec, input_image, references)
    return StartRunResponse(
        run_id=run_id,
        status=harness.get_run(run_id).status,  # type: ignore[union-attr]
        status_url=f"{API_PREFIX}/runs/{run_id}",
        events_url=f"{API_PREFIX}/runs/{run_id}/events",
    )


@router.get("/runs/{run_id}", response_model=RunDetailDTO)
def get_run(run_id: str, harness: ApexHarness = Depends(get_harness)) -> RunDetailDTO:
    state = harness.get_run(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="run not found")
    return build_run_detail(state)


@router.get("/runs/{run_id}/events")
async def run_events(
    run_id: str,
    harness: ApexHarness = Depends(get_harness),
    runner: InProcessRunner = Depends(get_runner),
) -> EventSourceResponse:
    if harness.get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    queue = runner.add_subscriber(run_id)

    async def generator() -> AsyncIterator[dict]:
        try:
            state = harness.get_run(run_id)
            assert state is not None
            yield {
                "event": "snapshot",
                "data": json.dumps(build_run_detail(state).model_dump(mode="json")),
            }
            if state.status in TERMINAL:
                return
            while True:
                event = await queue.get()
                if event["type"] == "close":
                    break
                yield {"event": event["type"], "data": json.dumps(event)}
        finally:
            runner.remove_subscriber(run_id, queue)

    return EventSourceResponse(generator())


def _image_response(harness: ApexHarness, run_id: str, filename: str) -> FileResponse:
    path = RunArtifacts(harness.settings.runs_dir, run_id).path(filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="image not found")
    return FileResponse(path, media_type="image/png")


@router.get("/runs/{run_id}/iterations/{index}/image")
def iteration_image(
    run_id: str, index: int, harness: ApexHarness = Depends(get_harness)
) -> FileResponse:
    return _image_response(harness, run_id, f"iter_{index:02d}.png")


@router.get("/runs/{run_id}/final")
def final_image(run_id: str, harness: ApexHarness = Depends(get_harness)) -> FileResponse:
    return _image_response(harness, run_id, "final.png")


@router.delete("/runs/{run_id}", response_model=RunDetailDTO)
async def cancel_run(
    run_id: str,
    harness: ApexHarness = Depends(get_harness),
    runner: InProcessRunner = Depends(get_runner),
) -> RunDetailDTO:
    state = harness.get_run(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="run not found")
    await runner.cancel(run_id)
    return build_run_detail(state)


# --- profiles ----------------------------------------------------------
@router.get("/profiles", response_model=list[str])
def list_profiles(harness: ApexHarness = Depends(get_harness)) -> list[str]:
    return harness.list_profiles()


@router.get("/profiles/{filename}", response_model=GoalSpec)
def load_profile(filename: str, harness: ApexHarness = Depends(get_harness)) -> GoalSpec:
    goal = harness.load_profile(filename)
    if goal is None:
        raise HTTPException(status_code=404, detail="profile not found")
    return goal


@router.post("/profiles")
def save_profile(goal: GoalSpec, harness: ApexHarness = Depends(get_harness)) -> dict:
    return {"filename": harness.save_profile(goal)}


@router.delete("/profiles/{filename}")
def delete_profile(filename: str, harness: ApexHarness = Depends(get_harness)) -> dict:
    return {"deleted": harness.delete_profile(filename)}


__all__ = ["router"]
