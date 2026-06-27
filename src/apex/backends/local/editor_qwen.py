"""Local image editor backend: Qwen-Image-Edit-2511 via diffusers.

Heavy imports (torch, diffusers) are deferred to first use so this module is
importable on a CPU-only box. Needs the ``local-gpu`` extra and a GPU; exercised
in M6 on the H100 box.
"""

from __future__ import annotations

from ..base import EditRequest, EditResult


class QwenImageEditBackend:
    """Wraps ``QwenImageEditPlusPipeline`` (kept warm across iterations)."""

    def __init__(
        self,
        *,
        model_id: str = "Qwen/Qwen-Image-Edit-2511",
        device: str = "cuda:1",
        torch_dtype: str = "bfloat16",
    ) -> None:
        self.model_id = model_id
        self.device = device
        self.torch_dtype = torch_dtype
        self._pipe: object | None = None

    def _pipeline(self) -> object:
        if self._pipe is None:
            import torch
            from diffusers import QwenImageEditPlusPipeline

            pipe = QwenImageEditPlusPipeline.from_pretrained(
                self.model_id, torch_dtype=getattr(torch, self.torch_dtype)
            )
            self._pipe = pipe.to(self.device)
        return self._pipe

    def edit_image(self, request: EditRequest) -> EditResult:
        import torch

        pipe = self._pipeline()
        images = [request.input_image, *request.reference_images]
        image_arg = images if len(images) > 1 else request.input_image

        generator = None
        if request.seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(request.seed)

        result = pipe(  # type: ignore[operator]
            image=image_arg,
            prompt=request.instruction,
            negative_prompt=request.negative_prompt or " ",
            num_inference_steps=request.num_inference_steps,
            true_cfg_scale=request.true_cfg_scale,
            generator=generator,
        )
        return EditResult(
            image=result.images[0],
            seed_used=request.seed,
            meta={"backend": "qwen", "model": self.model_id},
        )


__all__ = ["QwenImageEditBackend"]
