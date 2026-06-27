"""The portrait goal: enums, options, presets, validation, and MLLM seeding.

The legacy "profile" reframed as the structured goal that drives the harness.
Every legacy option value, preset, validation message, and descriptive string
is preserved here.
"""

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
from .models import (
    AdditionalInfo,
    AdvancedSettings,
    BasicInfo,
    GoalSpec,
    Metadata,
)
from .options import OPTIONS, FieldOption, option_values
from .presets import PRESETS, PresetData, get_preset, goal_from_preset
from .validation import ValidationResult, validate_basic_info, validate_goal_form

__all__ = [
    # enums
    "Purpose",
    "Attire",
    "Background",
    "Vibe",
    "Lighting",
    "Mood",
    "AgeRange",
    "Gender",
    "Ethnicity",
    "Resolution",
    # models
    "GoalSpec",
    "BasicInfo",
    "AdvancedSettings",
    "AdditionalInfo",
    "Metadata",
    # options / presets
    "OPTIONS",
    "FieldOption",
    "option_values",
    "PRESETS",
    "PresetData",
    "get_preset",
    "goal_from_preset",
    # validation
    "ValidationResult",
    "validate_basic_info",
    "validate_goal_form",
]
