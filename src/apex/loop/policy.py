"""Pure decision logic for the refinement loop — no I/O, fully unit-tested.

Acceptance requires agreement: the deterministic gates pass AND the judge is
above threshold AND the judge marks the result acceptable. Identity is a hard
gate — a failure forces a refine (with revert) and, after enough consecutive
failures, stops the run.
"""

from __future__ import annotations

from ..config import LoopPolicy, QualityThresholds
from ..metrics.report import QualityReport
from ..mllm.schemas import JudgeResult
from .records import Decision


def decide(
    *,
    report: QualityReport,
    judge: JudgeResult,
    iteration_index: int,
    identity_fail_streak: int,
    thresholds: QualityThresholds,
    policy: LoopPolicy,
) -> Decision:
    """Return the loop's decision after an iteration's evaluation."""
    if not report.identity_passed:  # hard gate
        if identity_fail_streak + 1 >= policy.max_identity_fails:
            return Decision.STOP_IDENTITY_FAIL
        return Decision.REFINE

    judge_ok = judge.overall >= thresholds.judge_threshold and judge.acceptable
    if report.soft_gates_passed and judge_ok:
        return Decision.ACCEPT

    if iteration_index + 1 >= policy.max_iterations:
        return Decision.STOP_MAX_ITERS
    return Decision.REFINE


def composite_score(report: QualityReport, judge: JudgeResult) -> float:
    """Rank iterations so the 'best' returned on a non-accept stop is sensible.

    Identity-passing iterations always outrank failing ones; ties broken by the
    judge's overall score plus the count of passed soft gates.
    """
    identity_bonus = 1000.0 if report.identity_passed else 0.0
    soft_passed = sum(1 for r in report.results if r.is_gate and not r.is_hard_gate and r.passed)
    return identity_bonus + judge.overall + soft_passed


__all__ = ["composite_score", "decide"]
