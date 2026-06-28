"""The :class:`GoalSpec` — APEX's strongly-typed portrait goal.

This is the legacy "profile" reframed: the same nested shape
(`basic_info` / `advanced_settings` / `additional_info` / `metadata` /
`generated_prompt`) that `APEX_old/apex/models/profile.py` produced, but as
validated Pydantic models. :meth:`GoalSpec.to_profile_json` /
:meth:`GoalSpec.from_profile_json` keep the on-disk JSON contract so old saved
profiles still load.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    AgeRange,
    Attire,
    Background,
    Ethnicity,
    Gender,
    Lighting,
    Mood,
    Purpose,
    Resolution,
    Vibe,
)


class BasicInfo(BaseModel):
    purpose: Purpose
    attire: Attire
    background: Background
    vibe: Vibe


class AdvancedSettings(BaseModel):
    lighting: Lighting = Lighting.PROFESSIONAL_FLASH
    mood: Mood = Mood.PROFESSIONAL
    age_range: AgeRange = AgeRange.NOT_SPECIFIED
    gender: Gender = Gender.NOT_SPECIFIED
    ethnicity: Ethnicity = Ethnicity.NOT_SPECIFIED
    resolution: Resolution = Resolution.STANDARD


class AdditionalInfo(BaseModel):
    reference_photo: str | None = None
    custom_notes: str | None = None
    preset_used: str | None = None


def _now_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Metadata(BaseModel):
    timestamp: str = Field(default_factory=_now_timestamp)
    version: str = "3.0"
    created_by: str = "APEX Portrait Generator"


class GoalSpec(BaseModel):
    """The complete portrait goal — the contract that drives the harness."""

    model_config = ConfigDict(extra="ignore")

    basic_info: BasicInfo
    advanced_settings: AdvancedSettings = Field(default_factory=AdvancedSettings)
    additional_info: AdditionalInfo = Field(default_factory=AdditionalInfo)
    metadata: Metadata = Field(default_factory=Metadata)
    generated_prompt: str | None = None

    def to_profile_json(self) -> dict[str, Any]:
        """Serialize to the legacy profile JSON shape (enum values as strings)."""
        return self.model_dump(mode="json")

    @classmethod
    def from_profile_json(cls, data: dict[str, Any]) -> GoalSpec:
        """Load from the legacy profile JSON shape (v2.0 profiles included)."""
        return cls.model_validate(data)


_ADVANCED_FIELDS = ("lighting", "mood", "age_range", "gender", "ethnicity", "resolution")


def goal_from_form(data: dict[str, Any]) -> GoalSpec:
    """Build a GoalSpec from a flat form payload (the shape the React app posts).

    Unset advanced fields fall back to their defaults. Validate the payload with
    :func:`apex.goalspec.validate_goal_form` first.
    """
    advanced = {key: data[key] for key in _ADVANCED_FIELDS if data.get(key)}
    return GoalSpec(
        basic_info=BasicInfo(
            purpose=data["purpose"],
            attire=data["attire"],
            background=data["background"],
            vibe=data["vibe"],
        ),
        advanced_settings=AdvancedSettings(**advanced),
        additional_info=AdditionalInfo(
            custom_notes=(data.get("custom_notes") or None),
            preset_used=(data.get("preset_name") or None),
        ),
    )


__all__ = [
    "AdditionalInfo",
    "AdvancedSettings",
    "BasicInfo",
    "GoalSpec",
    "Metadata",
    "goal_from_form",
]
