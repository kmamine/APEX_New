"""No-reference image quality (BRISQUE) via pyiqa (lazy; informational)."""

from __future__ import annotations

from PIL import Image

from .aesthetic import _PyiqaMetric


class NoReferenceIQA(_PyiqaMetric):
    name = "iqa"

    def __init__(self, threshold: float = 0.0, *, device: str = "cpu") -> None:
        # BRISQUE: lower is better.
        super().__init__(threshold, metric_name="brisque", device=device, higher_is_better=False)

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        score = self._score(candidate)
        return score, f"brisque {score:.3f}"


__all__ = ["NoReferenceIQA"]
