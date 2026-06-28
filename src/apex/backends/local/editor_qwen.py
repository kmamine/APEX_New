"""Local image editor backend: Qwen-Image-Edit-2511 via diffusers.

Supports two load paths (both lazy-imported, so this module is importable on a
CPU-only box):

- Full precision: ``QwenImageEditPlusPipeline.from_pretrained(model_id)`` (~60 GB).
- GGUF-quantized transformer: load the transformer from a single ``.gguf`` file
  (e.g. a ~13 GB Q4_K_M from ``unsloth/Qwen-Image-Edit-2511-GGUF``) and assemble
  the pipeline with the base repo's text encoder + VAE. Needs the ``gguf`` package
  and a recent diffusers (``QwenImageEditPlusPipeline`` / GGUF support may require
  diffusers from git). Verified on the H100 box in M6.
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
        gguf_file: str | None = None,
    ) -> None:
        self.model_id = model_id
        self.device = device
        self.torch_dtype = torch_dtype
        self.gguf_file = gguf_file
        self._pipe: object | None = None

    def _pipeline(self) -> object:
        if self._pipe is None:
            import torch
            from diffusers import QwenImageEditPlusPipeline

            dtype = getattr(torch, self.torch_dtype)
            if self.gguf_file:
                from diffusers import GGUFQuantizationConfig, QwenImageTransformer2DModel

                transformer = QwenImageTransformer2DModel.from_single_file(
                    self.gguf_file,
                    quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
                    torch_dtype=dtype,
                )
                pipe = QwenImageEditPlusPipeline.from_pretrained(
                    self.model_id, transformer=transformer, torch_dtype=dtype
                )
            else:
                pipe = QwenImageEditPlusPipeline.from_pretrained(self.model_id, torch_dtype=dtype)
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
            meta={"backend": "qwen", "model": self.model_id, "gguf": bool(self.gguf_file)},
        )


__all__ = ["QwenImageEditBackend"]
