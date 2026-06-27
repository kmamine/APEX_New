"""Strongly-typed option enums for the portrait goal.

Values are preserved **verbatim** from the legacy implementation
(`APEX_old/web-app/src/constants/options.ts` and the Gradio interface) so that
existing saved profiles remain valid. Display labels/icons live in
:mod:`apex.goalspec.options`; a test asserts the two stay in sync.
"""

from __future__ import annotations

from enum import StrEnum


class Purpose(StrEnum):
    LINKEDIN = "LinkedIn"
    RESUME = "Resume"
    CORPORATE_WEBSITE = "Corporate Website"
    PERSONAL_BRANDING = "Personal Branding"
    BUSINESS_CARD = "Business Card"
    OTHER = "Other"


class Attire(StrEnum):
    BUSINESS_FORMAL = "Business Formal"
    BUSINESS_CASUAL = "Business Casual"
    SMART_CASUAL = "Smart Casual"
    CREATIVE_PROFESSIONAL = "Creative Professional"
    ACADEMIC = "Academic"
    OTHER = "Other"


class Background(StrEnum):
    CORPORATE_OFFICE = "Corporate Office"
    PLAIN_COLOR = "Plain Color"
    OUTDOOR = "Outdoor"
    STUDIO_LIKE = "Studio-like"
    LIBRARY_ACADEMIC = "Library/Academic"
    CREATIVE_SPACE = "Creative Space"
    OTHER = "Other"


class Vibe(StrEnum):
    CONFIDENT = "Confident"
    FRIENDLY = "Friendly"
    APPROACHABLE = "Approachable"
    AUTHORITATIVE = "Authoritative"
    CREATIVE = "Creative"
    SOPHISTICATED = "Sophisticated"
    WARM = "Warm"


class Lighting(StrEnum):
    NATURAL_LIGHT = "Natural Light"
    STUDIO_LIGHTING = "Studio Lighting"
    SOFT_LIGHTING = "Soft Lighting"
    DRAMATIC_LIGHTING = "Dramatic Lighting"
    GOLDEN_HOUR = "Golden Hour"
    PROFESSIONAL_FLASH = "Professional Flash"


class Mood(StrEnum):
    PROFESSIONAL = "Professional"
    CASUAL = "Casual"
    SERIOUS = "Serious"
    ENERGETIC = "Energetic"
    CALM = "Calm"
    INSPIRING = "Inspiring"


class AgeRange(StrEnum):
    AGE_20_30 = "20-30"
    AGE_30_40 = "30-40"
    AGE_40_50 = "40-50"
    AGE_50_60 = "50-60"
    AGE_60_PLUS = "60+"
    NOT_SPECIFIED = "Not Specified"


class Gender(StrEnum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-binary"
    NOT_SPECIFIED = "Not Specified"


class Ethnicity(StrEnum):
    ASIAN = "Asian"
    BLACK = "Black"
    CAUCASIAN = "Caucasian"
    HISPANIC = "Hispanic"
    MIDDLE_EASTERN = "Middle Eastern"
    MIXED = "Mixed"
    NOT_SPECIFIED = "Not Specified"


class Resolution(StrEnum):
    STANDARD = "1024x1024 (Standard)"
    WIDE = "1536x1024 (Wide)"
    PORTRAIT = "1024x1536 (Portrait)"
    HIGH_RES = "2048x2048 (High-Res)"

    @property
    def dimensions(self) -> tuple[int, int]:
        """Return (width, height) parsed from the option label."""
        wh = self.value.split(" ", 1)[0]
        w, h = wh.split("x")
        return int(w), int(h)


__all__ = [
    "AgeRange",
    "Attire",
    "Background",
    "Ethnicity",
    "Gender",
    "Lighting",
    "Mood",
    "Purpose",
    "Resolution",
    "Vibe",
]
