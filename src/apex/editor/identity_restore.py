"""Identity restoration: graft the original face's identity onto an edit.

Diffusion editors regenerate the face, so ArcFace similarity to the original
caps out fairly low. After an edit we optionally run InsightFace's ``inswapper``
to transfer the ORIGINAL face's identity onto the generated portrait, which
raises identity similarity substantially. Heavy imports are lazy; needs the
``local-gpu`` extra and the inswapper model (fetched from a HF mirror).
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


class IdentityRestorer:
    def __init__(
        self,
        *,
        model_repo: str = "ezioruan/inswapper_128.onnx",
        model_file: str = "inswapper_128.onnx",
        det_size: int = 640,
        ctx_id: int = 0,
    ) -> None:
        self.model_repo = model_repo
        self.model_file = model_file
        self.det_size = det_size
        self.ctx_id = ctx_id
        self._app: object | None = None
        self._swapper: object | None = None

    def _ensure(self) -> tuple[object, object]:
        if self._swapper is None:
            from huggingface_hub import hf_hub_download
            from insightface.app import FaceAnalysis
            from insightface.model_zoo import get_model

            app = FaceAnalysis(name="buffalo_l")
            app.prepare(ctx_id=self.ctx_id, det_size=(self.det_size, self.det_size))
            path = hf_hub_download(repo_id=self.model_repo, filename=self.model_file)
            self._app, self._swapper = app, get_model(path)
        return self._app, self._swapper

    @staticmethod
    def _largest(faces: list) -> object:
        return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

    def restore(self, source: Image.Image, target: Image.Image) -> Image.Image:
        """Swap the identity of the largest face in ``source`` onto ``target``."""
        app, swapper = self._ensure()
        src_bgr = cv2.cvtColor(np.asarray(source.convert("RGB")), cv2.COLOR_RGB2BGR)
        tgt_bgr = cv2.cvtColor(np.asarray(target.convert("RGB")), cv2.COLOR_RGB2BGR)

        src_faces = app.get(src_bgr)  # type: ignore[attr-defined]
        tgt_faces = app.get(tgt_bgr)  # type: ignore[attr-defined]
        if not src_faces or not tgt_faces:
            return target  # nothing to graft onto / from

        swapped = swapper.get(  # type: ignore[attr-defined]
            tgt_bgr, self._largest(tgt_faces), self._largest(src_faces), paste_back=True
        )
        return Image.fromarray(cv2.cvtColor(swapped, cv2.COLOR_BGR2RGB))


__all__ = ["IdentityRestorer"]
