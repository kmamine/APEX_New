"""ApexHarness — the FastAPI-agnostic entry point that runs the harness.

Owns the backend, metrics, and stores. ``create_run`` registers a run and
persists its input; ``execute_run`` runs the (blocking) loop, streaming progress
through an optional callback and persisting artifacts + ``run.json`` as it goes.
The editor backend and metrics are built once (kept warm); the chat client is
rebuilt per run (cheap, and resets the fake judge counter between runs).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from collections.abc import Sequence as Seq
from datetime import datetime

from PIL import Image

from ..backends import build_chat, build_editor
from ..config import Settings, get_settings
from ..editor import ImageEditor
from ..goalspec import OPTIONS, PRESETS, GoalSpec, ValidationResult, validate_goal_form
from ..goalspec.options import FieldOption
from ..goalspec.presets import PresetData
from ..loop import AgenticLoop, IterationRecord, RunStatus
from ..metrics import build_metrics
from ..mllm import Judge, Orchestrator
from ..persistence import ProfileStore, RunArtifacts, RunState, RunStore

ProgressFn = Callable[[IterationRecord, str], None]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class ApexHarness:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.thresholds = self.settings.thresholds()
        self.policy = self.settings.loop_policy()
        self.profile_store = ProfileStore(self.settings.profiles_dir)
        self.run_store = RunStore(self.settings.runs_dir)
        self._editor_backend = build_editor(self.settings)
        self._metrics = self._build_metrics()
        self._runs: dict[str, RunState] = {}

    def _build_metrics(self) -> list:
        if self.settings.backend_mode == "fake":
            # Stub identity + sharpness only: the OpenCV face gate needs a real face.
            return build_metrics(
                self.thresholds, enabled=["identity", "sharpness"], identity_impl="stub"
            )
        return build_metrics(
            self.thresholds,
            enabled=self.settings.enabled_metric_names(),
            identity_impl="real",
        )

    # --- goal metadata -------------------------------------------------
    def options(self) -> dict[str, list[FieldOption]]:
        return OPTIONS

    def presets(self) -> list[PresetData]:
        return list(PRESETS.values())

    def validate(self, data: dict[str, object]) -> ValidationResult:
        return validate_goal_form(data)

    # --- profiles ------------------------------------------------------
    def list_profiles(self) -> list[str]:
        return self.profile_store.list()

    def load_profile(self, filename: str) -> GoalSpec | None:
        return self.profile_store.load(filename)

    def save_profile(self, goal: GoalSpec, filename: str | None = None) -> str:
        return self.profile_store.save(goal, filename).name

    def delete_profile(self, filename: str) -> bool:
        return self.profile_store.delete(filename)

    # --- runs ----------------------------------------------------------
    def create_run(
        self,
        goal: GoalSpec,
        input_image: Image.Image,
        reference_images: Seq[Image.Image] | None = None,
    ) -> RunState:
        run_id = uuid.uuid4().hex[:12]
        artifacts = RunArtifacts(self.settings.runs_dir, run_id)
        input_name = artifacts.save_input(input_image)
        ref_names = [
            artifacts._save(f"ref_{i:02d}.png", img) for i, img in enumerate(reference_images or [])
        ]
        now = _now()
        state = RunState(
            run_id=run_id,
            status=RunStatus.PENDING,
            goal=goal,
            created_at=now,
            updated_at=now,
            input_image=input_name,
            reference_images=ref_names,
            max_iterations=self.policy.max_iterations,
            thresholds=self.thresholds,
            policy=self.policy,
        )
        self._runs[run_id] = state
        self.run_store.save(state)
        return state

    def get_run(self, run_id: str) -> RunState | None:
        return self._runs.get(run_id) or self.run_store.load(run_id)

    def execute_run(self, run_id: str, progress: ProgressFn | None = None) -> RunState:
        state = self.get_run(run_id)
        if state is None:
            raise KeyError(run_id)
        self._runs[run_id] = state
        artifacts = RunArtifacts(self.settings.runs_dir, run_id)
        input_image = Image.open(artifacts.path(state.input_image)).convert("RGB")
        references = [
            Image.open(artifacts.path(name)).convert("RGB") for name in state.reference_images
        ]

        state.status = RunStatus.RUNNING
        state.updated_at = _now()
        self.run_store.save(state)

        def on_iteration(record: IterationRecord, image: Image.Image) -> None:
            name = artifacts.save_iteration(record.index, image)
            state.iterations.append(record)
            state.iteration_images.append(name)
            state.current_iteration = record.index + 1
            state.updated_at = _now()
            self.run_store.save(state)
            if progress is not None:
                progress(record, name)

        chat = build_chat(self.settings)
        loop = AgenticLoop(
            orchestrator=Orchestrator(chat),
            judge=Judge(chat),
            editor=ImageEditor(
                self._editor_backend,
                num_inference_steps=self.settings.num_inference_steps,
                true_cfg_scale=self.settings.true_cfg_scale,
            ),
            metrics=self._metrics,
            thresholds=self.thresholds,
            policy=self.policy,
            on_iteration=on_iteration,
        )

        try:
            result = loop.run(state.goal, input_image, reference_images=references)
        except Exception as exc:
            state.status = RunStatus.FAILED
            state.error = str(exc)
            state.updated_at = _now()
            self.run_store.save(state)
            return state

        state.status = result.status
        state.final_index = result.final_index
        state.final_image = artifacts.save_final(result.final_image)
        state.updated_at = _now()
        if self.settings.auto_save:
            self.profile_store.save(state.goal)
        self.run_store.save(state)
        return state


__all__ = ["ApexHarness", "ProgressFn"]
