"""Built-in portrait presets.

Preserved **verbatim** from `APEX_old/web-app/src/constants/options.ts` (the
richer of the two legacy preset sets — it carries the user-facing descriptions
the React app shows). A preset seeds the four required fields plus custom notes;
advanced settings fall back to their defaults.
"""

from __future__ import annotations

from pydantic import BaseModel

from .enums import Attire, Background, Purpose, Vibe
from .models import AdditionalInfo, BasicInfo, GoalSpec


class PresetData(BaseModel):
    name: str
    purpose: str
    attire: str
    background: str
    vibe: str
    custom_notes: str
    description: str


PRESETS: dict[str, PresetData] = {
    "LinkedIn Professional": PresetData(
        name="LinkedIn Professional",
        purpose="LinkedIn",
        attire="Business Formal",
        background="Corporate Office",
        vibe="Confident",
        custom_notes=(
            "Professional headshot optimized for LinkedIn profile. "
            "Clean, crisp, and trustworthy appearance."
        ),
        description="Perfect for professional networking and career profiles",
    ),
    "Creative Portfolio": PresetData(
        name="Creative Portfolio",
        purpose="Personal Branding",
        attire="Creative Professional",
        background="Creative Space",
        vibe="Creative",
        custom_notes=(
            "Artistic and creative professional portrait showcasing personality and creativity."
        ),
        description="Ideal for artists, designers, and creative professionals",
    ),
    "Academic Profile": PresetData(
        name="Academic Profile",
        purpose="Resume",
        attire="Academic",
        background="Library/Academic",
        vibe="Sophisticated",
        custom_notes=(
            "Professional academic portrait suitable for research profiles "
            "and institutional websites."
        ),
        description="Great for researchers, professors, and academic professionals",
    ),
    "Startup Founder": PresetData(
        name="Startup Founder",
        purpose="Personal Branding",
        attire="Smart Casual",
        background="Plain Color",
        vibe="Confident",
        custom_notes=(
            "Modern entrepreneur portrait combining professionalism "
            "with approachable startup culture."
        ),
        description="Modern look for entrepreneurs and startup leaders",
    ),
    "Executive Portrait": PresetData(
        name="Executive Portrait",
        purpose="Corporate Website",
        attire="Business Formal",
        background="Corporate Office",
        vibe="Authoritative",
        custom_notes=(
            "High-level executive portrait projecting leadership, authority, "
            "and corporate excellence."
        ),
        description="High-level corporate portraits for C-suite executives",
    ),
}


def get_preset(name: str) -> PresetData | None:
    return PRESETS.get(name)


def goal_from_preset(name: str) -> GoalSpec:
    """Build a :class:`GoalSpec` from a preset (advanced settings stay default)."""
    preset = PRESETS[name]
    return GoalSpec(
        basic_info=BasicInfo(
            purpose=Purpose(preset.purpose),
            attire=Attire(preset.attire),
            background=Background(preset.background),
            vibe=Vibe(preset.vibe),
        ),
        additional_info=AdditionalInfo(custom_notes=preset.custom_notes, preset_used=name),
    )


__all__ = ["PRESETS", "PresetData", "get_preset", "goal_from_preset"]
