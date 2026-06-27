"""The judge: asks the MLLM to score an edited image against the brief."""

from __future__ import annotations

from PIL import Image

from ..backends.base import ChatBackend
from ..goalspec import GoalSpec
from ..goalspec.seed_prompt import JUDGE_SYSTEM_PROMPT, build_judge_user_prompt
from .schemas import JudgeResult


class Judge:
    def __init__(self, chat: ChatBackend) -> None:
        self.chat = chat

    def evaluate(self, goal: GoalSpec, candidate_image: Image.Image) -> JudgeResult:
        return self.chat.chat_structured(
            JUDGE_SYSTEM_PROMPT,
            build_judge_user_prompt(goal),
            [candidate_image],
            JudgeResult,
        )


__all__ = ["Judge"]
