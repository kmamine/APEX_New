"""GoalSpec, enums/options consistency, presets, and legacy JSON round-trip."""

from __future__ import annotations

import pytest

from apex.goalspec import (
    OPTIONS,
    PRESETS,
    AgeRange,
    Attire,
    Background,
    Ethnicity,
    Gender,
    GoalSpec,
    Lighting,
    Mood,
    Purpose,
    Resolution,
    Vibe,
    goal_from_preset,
    option_values,
)
from apex.goalspec.enums import Resolution as Res
from apex.goalspec.seed_prompt import build_goal_brief

FIELD_ENUMS = {
    "purpose": Purpose,
    "attire": Attire,
    "background": Background,
    "vibe": Vibe,
    "lighting": Lighting,
    "mood": Mood,
    "age_range": AgeRange,
    "gender": Gender,
    "ethnicity": Ethnicity,
    "resolution": Resolution,
}


@pytest.mark.parametrize("field", list(FIELD_ENUMS))
def test_options_match_enums(field: str) -> None:
    """Display options and enum values must stay perfectly in sync (order included)."""
    enum_values = [member.value for member in FIELD_ENUMS[field]]
    assert option_values(field) == enum_values


def test_every_enum_field_has_options() -> None:
    assert set(OPTIONS) == set(FIELD_ENUMS)


def test_resolution_dimensions() -> None:
    assert Res.STANDARD.dimensions == (1024, 1024)
    assert Res.WIDE.dimensions == (1536, 1024)
    assert Res.PORTRAIT.dimensions == (1024, 1536)
    assert Res.HIGH_RES.dimensions == (2048, 2048)


def test_goalspec_defaults(sample_goal: GoalSpec) -> None:
    assert sample_goal.basic_info.purpose == Purpose.LINKEDIN
    assert sample_goal.advanced_settings.lighting == Lighting.PROFESSIONAL_FLASH
    assert sample_goal.advanced_settings.resolution == Resolution.STANDARD
    assert sample_goal.metadata.version == "3.0"


def test_goalspec_rejects_invalid_option() -> None:
    with pytest.raises(ValueError):
        GoalSpec(
            basic_info={
                "purpose": "Astronaut",
                "attire": "Business Formal",
                "background": "Corporate Office",
                "vibe": "Confident",
            }
        )


def test_legacy_round_trip_is_lossless(legacy_profile_dict: dict) -> None:
    """A v2.0 profile loads and re-serializes byte-for-value identically."""
    goal = GoalSpec.from_profile_json(legacy_profile_dict)
    assert goal.metadata.version == "2.0"  # preserved, not overwritten
    assert goal.to_profile_json() == legacy_profile_dict


def test_presets_count_and_membership() -> None:
    assert len(PRESETS) == 5
    assert "LinkedIn Professional" in PRESETS  # legacy parity


def test_goal_from_preset() -> None:
    goal = goal_from_preset("Executive Portrait")
    assert goal.basic_info.purpose == Purpose.CORPORATE_WEBSITE
    assert goal.basic_info.vibe == Vibe.AUTHORITATIVE
    assert goal.additional_info.preset_used == "Executive Portrait"
    assert goal.additional_info.custom_notes


def test_build_goal_brief_includes_expansions(sample_goal: GoalSpec) -> None:
    brief = build_goal_brief(sample_goal)
    assert "Purpose: LinkedIn" in brief
    assert "professional headshot optimized for social media" in brief
    assert "1024x1024 (Standard)" in brief
