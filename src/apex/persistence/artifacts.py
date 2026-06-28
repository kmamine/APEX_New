"""Per-run artifact directory: input, per-iteration, and final images."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

INPUT_NAME = "input.png"
FINAL_NAME = "final.png"


class RunArtifacts:
    """Owns ``<runs_dir>/run_<id>/`` and the image files written into it."""

    def __init__(self, runs_dir: str | Path, run_id: str) -> None:
        self.run_id = run_id
        self.dir = Path(runs_dir) / f"run_{run_id}"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _save(self, name: str, image: Image.Image) -> str:
        image.convert("RGB").save(self.dir / name)
        return name

    def save_input(self, image: Image.Image) -> str:
        return self._save(INPUT_NAME, image)

    def save_iteration(self, index: int, image: Image.Image) -> str:
        return self._save(f"iter_{index:02d}.png", image)

    def save_final(self, image: Image.Image) -> str:
        return self._save(FINAL_NAME, image)

    def path(self, name: str) -> Path:
        return self.dir / name


__all__ = ["FINAL_NAME", "INPUT_NAME", "RunArtifacts"]
