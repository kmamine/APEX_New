"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from apex.goalspec import BasicInfo, GoalSpec

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def legacy_profile_path() -> Path:
    return FIXTURES / "legacy_profile_v2.json"


@pytest.fixture
def legacy_profile_dict(legacy_profile_path: Path) -> dict:
    return json.loads(legacy_profile_path.read_text(encoding="utf-8"))


@pytest.fixture
def sample_goal() -> GoalSpec:
    return GoalSpec(
        basic_info=BasicInfo(
            purpose="LinkedIn",
            attire="Business Formal",
            background="Corporate Office",
            vibe="Confident",
        )
    )


@pytest.fixture
def solid_image() -> Image.Image:
    """A flat gray image — zero Laplacian variance (blurry/low sharpness)."""
    return Image.new("RGB", (128, 128), (120, 120, 120))


@pytest.fixture
def noise_image() -> Image.Image:
    """Deterministic high-frequency noise — high sharpness, stable across runs."""
    rng = np.random.default_rng(1234)
    arr = rng.integers(0, 256, size=(128, 128, 3), dtype=np.uint8)
    return Image.fromarray(arr, mode="RGB")
