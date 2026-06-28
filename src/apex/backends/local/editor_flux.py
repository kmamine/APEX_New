"""Local image editor backend: FLUX.1-Kontext-dev via diffusers.

The fallback editor when the Qwen-Image-Edit weights are impractical. FLUX.1
Kontext is a ~24 GB (bf16) instruction editor with strong identity retention,
loaded via ``FluxKontextPipeline``. Heavy imports are lazy. Non-commercial
license — see the model card. Verified on the H100 box in M6.
"""

from __future__ import annotations

from ..base import EditRequest, EditResult


class FluxKontextBackend:
    """Wraps ``FluxKontextPipeline`` (kept warm across iterations)."""

    def __init__(
        self,
        *,
        model_id: str = "black-forest-labs/FLUX.1-Kontext-dev",
        device: str = "cuda:0",
        torch_dtype: str = "bfloat16",
        guidance_scale: float = 2.5,
    ) -> None:
        self.model_id = model_id
        self.device = device
        self.torch_dtype = torch_dtype
        self.guidance_scale = guidance_scale
        self._pipe: object | None = None

    def _pipeline(self) -> object:
        if self._pipe is None:
            import torch
            from diffusers import FluxKontextPipeline

            pipe = FluxKontextPipeline.from_pretrained(
                self.model_id, torch_dtype=getattr(torch, self.torch_dtype)
            )
            self._pipe = pipe.to(self.device)
        return self._pipe

    def edit_image(self, request: EditRequest) -> EditResult:
        import torch

        pipe = self._pipeline()
        generator = None
        if request.seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(request.seed)

        result = pipe(  # type: ignore[operator]
            image=request.input_image,
            prompt=request.instruction,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=self.guidance_scale,
            generator=generator,
        )
        return EditResult(
            image=result.images[0],
            seed_used=request.seed,
            meta={"backend": "flux-kontext", "model": self.model_id},
        )


__all__ = ["FluxKontextBackend"]
