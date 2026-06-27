"""Structured-output schemas the MLLM is constrained to produce.

Two small schemas (one per role) are more reliable for a compact model than a
single combined one, so the orchestrator and judge use separate calls.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EditInstruction(BaseModel):
    instruction: str = Field(description="One concise, concrete image-edit instruction.")
    rationale: str = Field(default="", description="Why this edit moves toward the brief.")


class OrchestrationResult(BaseModel):
    """The orchestrator's plan for the next edit."""

    analysis: str = Field(description="What still differs from the target brief.")
    next_edit: EditInstruction
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    done: bool = Field(default=False, description="True if no further edit is needed.")


class CriterionScore(BaseModel):
    criterion: str
    score: float = Field(ge=0.0, le=10.0)
    comment: str = ""


class JudgeResult(BaseModel):
    """The judge's per-criterion assessment of an edited image."""

    scores: list[CriterionScore] = Field(default_factory=list)
    overall: float = Field(ge=0.0, le=10.0)
    acceptable: bool = Field(description="Does it meet the bar for the requested portrait?")
    feedback: str = Field(default="", description="Concrete guidance for the next edit.")


__all__ = [
    "CriterionScore",
    "EditInstruction",
    "JudgeResult",
    "OrchestrationResult",
]
