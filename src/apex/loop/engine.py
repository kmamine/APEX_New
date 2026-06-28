"""The agentic refinement loop: orchestrate -> edit -> evaluate -> decide."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from PIL import Image

from ..config import LoopPolicy, QualityThresholds
from ..editor import IdentityRestorer, ImageEditor
from ..goalspec import GoalSpec
from ..metrics import Metric, evaluate_image
from ..metrics.report import QualityReport
from ..mllm import Judge, Orchestrator
from ..mllm.schemas import JudgeResult
from .policy import composite_score, decide
from .records import Decision, IterationRecord, RunResult, RunStatus

ProgressCallback = Callable[[IterationRecord, Image.Image], None]


@dataclass(slots=True)
class AgenticLoop:
    """Wires the orchestrator, editor, judge, and metrics into the loop."""

    orchestrator: Orchestrator
    judge: Judge
    editor: ImageEditor
    metrics: list[Metric]
    thresholds: QualityThresholds
    policy: LoopPolicy
    on_iteration: ProgressCallback | None = None
    identity_restorer: IdentityRestorer | None = None

    def run(
        self,
        goal: GoalSpec,
        input_image: Image.Image,
        *,
        reference_images: Sequence[Image.Image] | None = None,
    ) -> RunResult:
        references = list(reference_images or [])
        size = goal.advanced_settings.resolution.dimensions

        current = input_image
        last_accepted = input_image
        identity_fail_streak = 0
        prior_feedback: str | None = None

        iterations: list[IterationRecord] = []
        images: list[Image.Image] = []
        best_index = -1
        best_score = float("-inf")
        status = RunStatus.RUNNING
        final_index = -1

        for i in range(self.policy.max_iterations):
            # Edit the original each pass (no compounding) unless configured otherwise.
            source = input_image if self.policy.edit_from_original else current
            plan = self.orchestrator.plan(goal, source, prior_feedback)
            candidate = self.editor.apply(
                source, plan.next_edit.instruction, references, size=size
            )
            if self.identity_restorer is not None:
                # Graft the original identity back on to recover face similarity.
                candidate = self.identity_restorer.restore(input_image, candidate)
            report = evaluate_image(self.metrics, input_image, candidate)
            judgement = self.judge.evaluate(goal, candidate)
            decision = decide(
                report=report,
                judge=judgement,
                iteration_index=i,
                identity_fail_streak=identity_fail_streak,
                thresholds=self.thresholds,
                policy=self.policy,
            )

            record = IterationRecord(
                index=i,
                instruction=plan.next_edit.instruction,
                analysis=plan.analysis,
                confidence=plan.confidence,
                judge=judgement,
                metrics=report,
                decision=decision,
                accepted=decision == Decision.ACCEPT,
            )
            iterations.append(record)
            images.append(candidate)

            score = composite_score(report, judgement)
            if score > best_score:
                best_score, best_index = score, i

            if self.on_iteration is not None:
                self.on_iteration(record, candidate)

            if decision == Decision.ACCEPT:
                status, final_index = RunStatus.COMPLETED, i
                break
            if decision == Decision.STOP_IDENTITY_FAIL:
                status = RunStatus.STOPPED_IDENTITY
                break
            if decision == Decision.STOP_MAX_ITERS:
                status = RunStatus.STOPPED_MAX_ITERS
                break

            # REFINE. In compounding mode, keep progress only if identity held
            # (else revert); in edit-from-original mode the source never changes.
            if report.identity_passed:
                identity_fail_streak = 0
                if not self.policy.edit_from_original:
                    current = last_accepted = candidate
            else:
                identity_fail_streak += 1
                if not self.policy.edit_from_original:
                    current = last_accepted
            prior_feedback = _feedback(report, judgement)

        if not iterations:  # max_iterations <= 0
            return RunResult(
                status=RunStatus.FAILED,
                iterations=[],
                iteration_images=[],
                final_image=input_image,
                final_index=-1,
                input_image=input_image,
                reference_images=references,
            )

        if status != RunStatus.COMPLETED:
            final_index = best_index

        return RunResult(
            status=status,
            iterations=iterations,
            iteration_images=images,
            final_image=images[final_index],
            final_index=final_index,
            input_image=input_image,
            reference_images=references,
        )


def _feedback(report: QualityReport, judge: JudgeResult) -> str:
    parts: list[str] = []
    if report.failures:
        parts.append("Metric issues: " + "; ".join(report.failures))
    if judge.feedback:
        parts.append("Judge feedback: " + judge.feedback)
    return " ".join(parts) or "Refine further toward the brief."


__all__ = ["AgenticLoop", "ProgressCallback"]
