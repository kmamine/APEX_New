"""Hosted image editor backend: Qwen-Image-Edit via Replicate.

Best-effort adapter (lazy ``replicate`` import). The exact model slug and input
field names should be confirmed against the Replicate model page before relying
on this path; the local Qwen backend is the primary/tested route.
"""

from __future__ import annotations

import io

from PIL import Image

from ..base import EditRequest, EditResult


class ReplicateEditBackend:
    def __init__(self, *, model: str, api_token: str | None = None) -> None:
        # `model` may be the Replicate slug; default to the official one if a HF id is passed.
        self.model = (
            model if "/" in model and not model.startswith("Qwen/") else "qwen/qwen-image-edit"
        )
        self.api_token = api_token

    def edit_image(self, request: EditRequest) -> EditResult:
        import os

        import replicate

        if self.api_token:
            os.environ.setdefault("REPLICATE_API_TOKEN", self.api_token)

        input_buffer = io.BytesIO()
        request.input_image.convert("RGB").save(input_buffer, format="PNG")
        input_buffer.seek(0)

        output = replicate.run(
            self.model,
            input={
                "image": input_buffer,
                "prompt": request.instruction,
                "negative_prompt": request.negative_prompt or " ",
                "num_inference_steps": request.num_inference_steps,
                "true_cfg_scale": request.true_cfg_scale,
            },
        )
        image = _load_replicate_output(output)
        return EditResult(image=image, seed_used=request.seed, meta={"backend": "replicate"})


def _load_replicate_output(output: object) -> Image.Image:
    """Replicate returns a URL, a list of URLs, or a file-like object."""
    import httpx

    item = output[0] if isinstance(output, list) else output
    read = getattr(item, "read", None)
    if callable(read):
        return Image.open(io.BytesIO(read()))
    return Image.open(io.BytesIO(httpx.get(str(item)).content))


__all__ = ["ReplicateEditBackend"]
