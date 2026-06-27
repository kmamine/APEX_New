"""Backend protocols — the seam that makes APEX pluggable.

Two capabilities, kept as separate protocols because a local deployment splits
them across processes (vLLM server for chat, in-process diffusers for editing)
while a hosted deployment may use two different vendors. The loop, harness, and
tests depend only on these protocols — never on torch/vLLM/Replicate directly.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, runtime_checkable

from PIL import Image
from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


@dataclass(slots=True)
class EditRequest:
    """A single image-edit request handed to an :class:`EditBackend`."""

    input_image: Image.Image
    instruction: str
    reference_images: list[Image.Image] = field(default_factory=list)
    negative_prompt: str = ""
    num_inference_steps: int = 45
    true_cfg_scale: float = 4.0
    seed: int | None = None
    width: int | None = None
    height: int | None = None


@dataclass(slots=True)
class EditResult:
    image: Image.Image
    seed_used: int | None = None
    meta: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class ChatBackend(Protocol):
    """A multimodal chat model that returns validated structured output."""

    def chat_structured(
        self,
        system: str,
        user: str,
        images: Sequence[Image.Image],
        schema: type[TModel],
    ) -> TModel:
        """Return an instance of ``schema`` produced by the model."""
        ...


@runtime_checkable
class EditBackend(Protocol):
    """An image editor that transforms an image per a text instruction."""

    def edit_image(self, request: EditRequest) -> EditResult: ...


@dataclass(slots=True)
class ModelBackend:
    """A chat + editor pair the loop engine consumes as one object."""

    chat: ChatBackend
    editor: EditBackend


__all__ = [
    "ChatBackend",
    "EditBackend",
    "EditRequest",
    "EditResult",
    "ModelBackend",
    "TModel",
]
