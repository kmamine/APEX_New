"""Small image-conversion helpers shared by the OpenCV-based metrics."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def to_gray(img: Image.Image) -> np.ndarray:
    """PIL image -> single-channel grayscale uint8 ndarray."""
    return cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2GRAY)


def to_bgr(img: Image.Image) -> np.ndarray:
    """PIL image -> BGR uint8 ndarray (OpenCV / insightface convention)."""
    return cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)


__all__ = ["to_bgr", "to_gray"]
