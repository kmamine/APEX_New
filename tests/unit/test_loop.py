"""End-to-end loop behavior against the fake backend (no GPU)."""

from __future__ import annotations

from PIL import Image

from apex.backends.fake import FakeChatBackend, FakeEditBackend
from apex.config import LoopPolicy, QualityThresholds
from apex.editor import ImageEditor
from apex.goalspec import GoalSpec
from apex.loop import AgenticLoop, RunStatus
from apex.metrics import build_metrics
from apex.metrics.base import Metric
from apex.mllm import Judge, Orchestrator


def _build_loop(*, metrics=None, max_iterations=5, max_identity_fails=2) -> AgenticLoop:
    chat = FakeChatBackend()  # shared so the judge score ramps across iterations
    thresholds = QualityThresholds(judge_threshold=7.0, sharpness_min=50.0)
    policy = LoopPolicy(max_iterations=max_iterations, max_identity_fails=max_identity_fails)
    if metrics is None:
        metrics = build_metrics(thresholds, enabled=["identity", "sharpness"], identity_impl="stub")
    return AgenticLoop(
        orchestrator=Orchestrator(chat),
        judge=Judge(chat),
        editor=ImageEditor(FakeEditBackend()),
        metrics=metrics,
        thresholds=thresholds,
        policy=policy,
    )


def test_loop_converges_and_accepts(noise_image: Image.Image, sample_goal: GoalSpec) -> None:
    result = _build_loop().run(sample_goal, noise_image)
    assert result.status == RunStatus.COMPLETED
    assert result.accepted
    assert result.iterations[result.final_index].accepted
    assert result.final_image.size == sample_goal.advanced_settings.resolution.dimensions


def test_loop_emits_contiguous_progress(noise_image: Image.Image, sample_goal: GoalSpec) -> None:
    seen: list[int] = []
    loop = _build_loop()
    loop.on_iteration = lambda record, _img: seen.append(record.index)
    loop.run(sample_goal, noise_image)
    assert seen == list(range(len(seen)))
    assert len(seen) >= 1


class _FailIdentity(Metric):
    name = "identity"
    is_gate = True
    is_hard_gate = True

    def __init__(self) -> None:
        super().__init__(0.35)

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        return 0.0, "forced identity failure"


def test_loop_stops_on_repeated_identity_failure(
    noise_image: Image.Image, sample_goal: GoalSpec
) -> None:
    loop = _build_loop(metrics=[_FailIdentity()], max_identity_fails=2)
    result = loop.run(sample_goal, noise_image)
    assert result.status == RunStatus.STOPPED_IDENTITY
    assert len(result.iterations) == 2


def test_loop_stops_at_max_iters_when_soft_gate_never_passes(
    solid_image: Image.Image, sample_goal: GoalSpec
) -> None:
    # A flat image never clears the sharpness gate, so the run exhausts its budget.
    result = _build_loop(max_iterations=3).run(sample_goal, solid_image)
    assert result.status == RunStatus.STOPPED_MAX_ITERS
    assert len(result.iterations) == 3
    assert 0 <= result.final_index < 3


def test_iteration_record_is_serializable(noise_image: Image.Image, sample_goal: GoalSpec) -> None:
    result = _build_loop().run(sample_goal, noise_image)
    dumped = result.iterations[0].model_dump(mode="json")
    assert {"index", "instruction", "judge", "metrics", "decision", "accepted"} <= dumped.keys()
