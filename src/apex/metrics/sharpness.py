"""Sharpness via the variance of the Laplacian (OpenCV, no model needed)."""

from __future__ import annotations

import cv2
from PIL import Image

from ._util import to_gray
from .base import Metric


class Sharpness(Metric):
    name = "sharpness"
    is_gate = True

    def __init__(self, threshold: float = 100.0) -> None:
        super().__init__(threshold)

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        variance = float(cv2.Laplacian(to_gray(candidate), cv2.CV_64F).var())
        return variance, f"Laplacian variance {variance:.1f}"


__all__ = ["Sharpness"]
