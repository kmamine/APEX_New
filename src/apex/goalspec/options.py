"""Display metadata (label + emoji icon) for each goal field option.

Preserved **verbatim** from `APEX_old/web-app/src/constants/options.ts`. The
FastAPI layer serves these so the React app renders the same dropdowns without
hand-duplicating the lists. :func:`option_values` ties the metadata back to the
enums; ``tests/unit/test_goalspec.py`` asserts they never drift apart.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldOption:
    value: str
    label: str
    icon: str


OPTIONS: dict[str, list[FieldOption]] = {
    "purpose": [
        FieldOption("LinkedIn", "💼 LinkedIn", "💼"),
        FieldOption("Resume", "📄 Resume", "📄"),
        FieldOption("Corporate Website", "🏢 Corporate Website", "🏢"),
        FieldOption("Personal Branding", "✨ Personal Branding", "✨"),
        FieldOption("Business Card", "🎯 Business Card", "🎯"),
        FieldOption("Other", "📋 Other", "📋"),
    ],
    "attire": [
        FieldOption("Business Formal", "👔 Business Formal", "👔"),
        FieldOption("Business Casual", "👕 Business Casual", "👕"),
        FieldOption("Smart Casual", "👻 Smart Casual", "👻"),
        FieldOption("Creative Professional", "🎨 Creative Professional", "🎨"),
        FieldOption("Academic", "🎓 Academic", "🎓"),
        FieldOption("Other", "📋 Other", "📋"),
    ],
    "background": [
        FieldOption("Corporate Office", "🏢 Corporate Office", "🏢"),
        FieldOption("Plain Color", "🎨 Plain Color", "🎨"),
        FieldOption("Outdoor", "🌳 Outdoor", "🌳"),
        FieldOption("Studio-like", "📸 Studio-like", "📸"),
        FieldOption("Library/Academic", "📚 Library/Academic", "📚"),
        FieldOption("Creative Space", "🎪 Creative Space", "🎪"),
        FieldOption("Other", "📋 Other", "📋"),
    ],
    "vibe": [
        FieldOption("Confident", "💪 Confident", "💪"),
        FieldOption("Friendly", "😊 Friendly", "😊"),
        FieldOption("Approachable", "🤝 Approachable", "🤝"),
        FieldOption("Authoritative", "👑 Authoritative", "👑"),
        FieldOption("Creative", "🎨 Creative", "🎨"),
        FieldOption("Sophisticated", "🎩 Sophisticated", "🎩"),
        FieldOption("Warm", "☀️ Warm", "☀️"),
    ],
    "lighting": [
        FieldOption("Natural Light", "☀️ Natural Light", "☀️"),
        FieldOption("Studio Lighting", "💡 Studio Lighting", "💡"),
        FieldOption("Soft Lighting", "🕯️ Soft Lighting", "🕯️"),
        FieldOption("Dramatic Lighting", "🎭 Dramatic Lighting", "🎭"),
        FieldOption("Golden Hour", "🌅 Golden Hour", "🌅"),
        FieldOption("Professional Flash", "📸 Professional Flash", "📸"),
    ],
    "mood": [
        FieldOption("Professional", "💼 Professional", "💼"),
        FieldOption("Casual", "😌 Casual", "😌"),
        FieldOption("Serious", "🧐 Serious", "🧐"),
        FieldOption("Energetic", "⚡ Energetic", "⚡"),
        FieldOption("Calm", "😌 Calm", "😌"),
        FieldOption("Inspiring", "✨ Inspiring", "✨"),
    ],
    "age_range": [
        FieldOption("20-30", "👶 20-30", "👶"),
        FieldOption("30-40", "👨 30-40", "👨"),
        FieldOption("40-50", "👔 40-50", "👔"),
        FieldOption("50-60", "👴 50-60", "👴"),
        FieldOption("60+", "👵 60+", "👵"),
        FieldOption("Not Specified", "❓ Not Specified", "❓"),
    ],
    "gender": [
        FieldOption("Male", "👨 Male", "👨"),
        FieldOption("Female", "👩 Female", "👩"),
        FieldOption("Non-binary", "🧑 Non-binary", "🧑"),
        FieldOption("Not Specified", "❓ Not Specified", "❓"),
    ],
    "ethnicity": [
        FieldOption("Asian", "🌏 Asian", "🌏"),
        FieldOption("Black", "🌍 Black", "🌍"),
        FieldOption("Caucasian", "🌎 Caucasian", "🌎"),
        FieldOption("Hispanic", "🌮 Hispanic", "🌮"),
        FieldOption("Middle Eastern", "🕌 Middle Eastern", "🕌"),
        FieldOption("Mixed", "🌈 Mixed", "🌈"),
        FieldOption("Not Specified", "❓ Not Specified", "❓"),
    ],
    "resolution": [
        FieldOption("1024x1024 (Standard)", "📐 1024x1024 (Standard)", "📐"),
        FieldOption("1536x1024 (Wide)", "📏 1536x1024 (Wide)", "📏"),
        FieldOption("1024x1536 (Portrait)", "📱 1024x1536 (Portrait)", "📱"),
        FieldOption("2048x2048 (High-Res)", "🖥️ 2048x2048 (High-Res)", "🖥️"),
    ],
}


def option_values(field: str) -> list[str]:
    """Return the raw values for a field, in display order."""
    return [opt.value for opt in OPTIONS[field]]


__all__ = ["OPTIONS", "FieldOption", "option_values"]
