"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
