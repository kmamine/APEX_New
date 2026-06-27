"""Face-presence gate: exactly one detectable face (OpenCV Haar cascade)."""

from __future__ import annotations

import cv2
from PIL import Image

from ._util import to_gray
from .base import Metric


class FacePresence(Metric):
    name = "face"
    is_gate = True

    def __init__(self, threshold: float = 1.0) -> None:
        super().__init__(threshold)
        self._cascade: cv2.CascadeClassifier | None = None

    def _detector(self) -> cv2.CascadeClassifier:
        if self._cascade is None:
            path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore[attr-defined]
            self._cascade = cv2.CascadeClassifier(path)
        return self._cascade

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        faces = self._detector().detectMultiScale(
            to_gray(candidate), scaleFactor=1.1, minNeighbors=5
        )
        count = len(faces)
        return float(count), f"{count} face(s) detected"

    def _passed(self, value: float) -> bool:
        return value == 1.0


__all__ = ["FacePresence"]
