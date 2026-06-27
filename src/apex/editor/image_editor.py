"""Thin wrapper turning an edit instruction into an :class:`EditBackend` call."""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image

from ..backends.base import EditBackend, EditRequest
from ..goalspec.detail_dicts import NEGATIVE_PROMPT


class ImageEditor:
    """Applies a single text instruction to an image via the configured backend."""

    def __init__(
        self,
        backend: EditBackend,
        *,
        negative_prompt: str = NEGATIVE_PROMPT,
        num_inference_steps: int = 45,
        true_cfg_scale: float = 4.0,
    ) -> None:
        self.backend = backend
        self.negative_prompt = negative_prompt
        self.num_inference_steps = num_inference_steps
        self.true_cfg_scale = true_cfg_scale

    def apply(
        self,
        image: Image.Image,
        instruction: str,
        reference_images: Sequence[Image.Image] | None = None,
        *,
        seed: int | None = None,
        size: tuple[int, int] | None = None,
    ) -> Image.Image:
        request = EditRequest(
            input_image=image,
            instruction=instruction,
            reference_images=list(reference_images or []),
            negative_prompt=self.negative_prompt,
            num_inference_steps=self.num_inference_steps,
            true_cfg_scale=self.true_cfg_scale,
            seed=seed,
            width=size[0] if size else None,
            height=size[1] if size else None,
        )
        return self.backend.edit_image(request).image


__all__ = ["ImageEditor"]
