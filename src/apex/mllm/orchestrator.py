"""The orchestrator: asks the MLLM to plan the next edit instruction."""

from __future__ import annotations

from PIL import Image

from ..backends.base import ChatBackend
from ..goalspec import GoalSpec
from ..goalspec.seed_prompt import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    build_orchestrator_user_prompt,
)
from .schemas import OrchestrationResult


class Orchestrator:
    def __init__(self, chat: ChatBackend) -> None:
        self.chat = chat

    def plan(
        self,
        goal: GoalSpec,
        current_image: Image.Image,
        prior_feedback: str | None = None,
    ) -> OrchestrationResult:
        return self.chat.chat_structured(
            ORCHESTRATOR_SYSTEM_PROMPT,
            build_orchestrator_user_prompt(goal, prior_feedback),
            [current_image],
            OrchestrationResult,
        )


__all__ = ["Orchestrator"]
