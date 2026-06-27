"""Aesthetic / perceptual-quality scoring via pyiqa (lazy; informational).

Reported for insight but not a gate by default — these scores are noisy and
shouldn't block an otherwise-good portrait. Needs the ``local-gpu`` extra.
"""

from __future__ import annotations

from PIL import Image

from .base import Metric


class _PyiqaMetric(Metric):
    """Shared lazy-loading wrapper around a pyiqa metric."""

    is_gate = False

    def __init__(
        self,
        threshold: float,
        *,
        metric_name: str,
        device: str = "cpu",
        higher_is_better: bool = True,
    ) -> None:
        super().__init__(threshold, higher_is_better=higher_is_better)
        self._metric_name = metric_name
        self._device = device
        self._model: object | None = None

    def _scorer(self) -> object:
        if self._model is None:
            import pyiqa

            self._model = pyiqa.create_metric(self._metric_name, device=self._device)
        return self._model

    def _score(self, candidate: Image.Image) -> float:
        import torch
        from torchvision.transforms.functional import to_tensor

        tensor = to_tensor(candidate.convert("RGB")).unsqueeze(0).to(self._device)
        with torch.no_grad():
            return float(self._scorer()(tensor).item())  # type: ignore[operator]


class AestheticScore(_PyiqaMetric):
    name = "aesthetic"

    def __init__(self, threshold: float = 5.0, *, device: str = "cpu") -> None:
        super().__init__(threshold, metric_name="clipiqa", device=device)

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        score = self._score(candidate)
        return score, f"clipiqa {score:.3f}"


__all__ = ["AestheticScore"]
