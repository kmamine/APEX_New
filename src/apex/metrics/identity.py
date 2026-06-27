"""Identity preservation — the hard gate.

:class:`IdentityPreservation` uses InsightFace/ArcFace embeddings (lazy import;
needs the ``local-gpu`` extra). :class:`StubIdentity` is a dependency-free
structural-similarity stand-in so the loop, harness, and demo work without a GPU
(used by the ``fake`` backend and CI).

Similarity is always measured against the ORIGINAL input photo — never the prior
iteration — so identity cannot drift past the gate one small step at a time.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from ._util import to_bgr
from .base import Metric


class IdentityPreservation(Metric):
    name = "identity"
    is_gate = True
    is_hard_gate = True

    def __init__(self, threshold: float = 0.35, *, det_size: int = 640) -> None:
        super().__init__(threshold)
        self._det_size = det_size
        self._app: object | None = None

    def _analyzer(self) -> object:
        if self._app is None:
            from insightface.app import FaceAnalysis

            app = FaceAnalysis(name="buffalo_l")
            app.prepare(ctx_id=0, det_size=(self._det_size, self._det_size))
            self._app = app
        return self._app

    def _embedding(self, img: Image.Image) -> np.ndarray | None:
        faces = self._analyzer().get(to_bgr(img))  # type: ignore[attr-defined]
        if not faces:
            return None
        largest = max(
            faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
        )
        return np.asarray(largest.normed_embedding, dtype=np.float64)

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        e_orig = self._embedding(original)
        e_cand = self._embedding(candidate)
        if e_orig is None or e_cand is None:
            return 0.0, "no face detected in input or candidate"
        cosine = float(np.dot(e_orig, e_cand))  # embeddings are L2-normalized
        return cosine, f"ArcFace cosine {cosine:.3f}"


class StubIdentity(Metric):
    """Deterministic, dependency-free identity proxy for GPU-free runs."""

    name = "identity"
    is_gate = True
    is_hard_gate = True

    def __init__(self, threshold: float = 0.35) -> None:
        super().__init__(threshold)

    @staticmethod
    def _feature(img: Image.Image) -> np.ndarray:
        gray = np.asarray(img.convert("L").resize((64, 64)), dtype=np.float64).ravel()
        centered = gray - gray.mean()
        norm = np.linalg.norm(centered)
        return centered / norm if norm else centered

    def _measure(self, original: Image.Image, candidate: Image.Image) -> tuple[float, str]:
        sim = float(np.dot(self._feature(original), self._feature(candidate)))
        sim = (sim + 1.0) / 2.0  # map [-1, 1] -> [0, 1]
        return sim, f"structural similarity (stub) {sim:.3f}"


__all__ = ["IdentityPreservation", "StubIdentity"]
