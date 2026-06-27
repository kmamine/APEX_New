"""Pure decision-policy tests."""

from __future__ import annotations

from apex.config import LoopPolicy, QualityThresholds
from apex.loop import Decision, composite_score, decide
from apex.metrics.base import MetricResult
from apex.metrics.report import QualityReport
from apex.mllm.schemas import JudgeResult

THRESHOLDS = QualityThresholds(judge_threshold=7.0)
POLICY = LoopPolicy(max_iterations=5, max_identity_fails=2)


def _report(*, identity_pass: bool, soft_pass: bool = True) -> QualityReport:
    return QualityReport(
        results=[
            MetricResult(
                name="identity",
                value=0.9 if identity_pass else 0.1,
                passed=identity_pass,
                is_gate=True,
                is_hard_gate=True,
            ),
            MetricResult(name="sharpness", value=200.0, passed=soft_pass, is_gate=True),
        ]
    )


def _judge(overall: float, acceptable: bool) -> JudgeResult:
    return JudgeResult(scores=[], overall=overall, acceptable=acceptable)


def test_identity_fail_refines_then_stops() -> None:
    kw = {
        "report": _report(identity_pass=False),
        "judge": _judge(8, True),
        "thresholds": THRESHOLDS,
        "policy": POLICY,
    }
    assert decide(iteration_index=0, identity_fail_streak=0, **kw) == Decision.REFINE
    assert decide(iteration_index=1, identity_fail_streak=1, **kw) == Decision.STOP_IDENTITY_FAIL


def test_accept_requires_agreement() -> None:
    kw = {
        "report": _report(identity_pass=True),
        "iteration_index": 0,
        "identity_fail_streak": 0,
        "thresholds": THRESHOLDS,
        "policy": POLICY,
    }
    assert decide(judge=_judge(9, True), **kw) == Decision.ACCEPT
    # judge above threshold but not "acceptable" -> not accepted
    assert decide(judge=_judge(9, False), **kw) == Decision.REFINE
    # soft gate failing -> not accepted even if judge is happy
    kw_soft = {**kw, "report": _report(identity_pass=True, soft_pass=False)}
    assert decide(judge=_judge(9, True), **kw_soft) == Decision.REFINE


def test_max_iters_stop() -> None:
    decision = decide(
        report=_report(identity_pass=True),
        judge=_judge(3, False),
        iteration_index=4,
        identity_fail_streak=0,
        thresholds=THRESHOLDS,
        policy=POLICY,
    )
    assert decision == Decision.STOP_MAX_ITERS


def test_composite_prefers_identity() -> None:
    passing = composite_score(_report(identity_pass=True), _judge(5, False))
    failing = composite_score(_report(identity_pass=False), _judge(9, True))
    assert passing > failing
