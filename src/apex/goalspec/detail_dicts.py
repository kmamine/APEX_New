"""Descriptive expansions for each goal option.

Preserved **verbatim** from `APEX_old/apex/core/prompt_generator.py`. In the
legacy system these strings were concatenated into a single Flux text prompt.
Here they are reused as structured *context* handed to the MLLM orchestrator
(see :mod:`apex.goalspec.seed_prompt`), and the negative prompt becomes the
image editor's default.
"""

from __future__ import annotations

PURPOSE_DETAILS: dict[str, str] = {
    "LinkedIn": "professional headshot optimized for social media",
    "Resume": "formal professional portrait for career applications",
    "Corporate Website": "executive-level corporate portrait",
    "Personal Branding": "distinctive personal brand portrait",
    "Business Card": "compact professional headshot",
    "Other": "professional portrait",
}

ATTIRE_DETAILS: dict[str, str] = {
    "Business Formal": "sharp business suit, professional tie, polished appearance",
    "Business Casual": "smart blazer, dress shirt, refined casual look",
    "Smart Casual": "stylish casual wear, modern professional appearance",
    "Creative Professional": "fashionable, artistic professional attire",
    "Academic": "scholarly attire, professional academic dress",
    "Other": "appropriate professional clothing",
}

BACKGROUND_DETAILS: dict[str, str] = {
    "Corporate Office": "modern office environment, soft bokeh, professional lighting",
    "Plain Color": "clean gradient background, studio lighting",
    "Outdoor": "natural outdoor setting, soft natural lighting",
    "Studio-like": "professional studio setup, controlled lighting",
    "Library/Academic": "scholarly environment, books, academic setting",
    "Creative Space": "artistic workspace, creative elements, modern aesthetic",
    "Other": "appropriate professional background",
}

VIBE_DETAILS: dict[str, str] = {
    "Confident": "confident expression, direct gaze, strong posture",
    "Friendly": "warm smile, approachable demeanor, friendly eyes",
    "Approachable": "gentle smile, open expression, welcoming appearance",
    "Authoritative": "commanding presence, serious expression, leadership aura",
    "Creative": "artistic expression, creative energy, innovative look",
    "Sophisticated": "refined elegance, intellectual appearance, polished style",
    "Warm": "genuine warmth, kind expression, compassionate presence",
}

LIGHTING_DETAILS: dict[str, str] = {
    "Natural Light": "soft natural lighting, window light",
    "Studio Lighting": "professional studio lighting setup",
    "Soft Lighting": "gentle, diffused lighting",
    "Dramatic Lighting": "dramatic shadows and highlights",
    "Golden Hour": "warm golden hour lighting",
    "Professional Flash": "professional flash photography lighting",
}

MOOD_DETAILS: dict[str, str] = {
    "Professional": "professional demeanor",
    "Casual": "relaxed, casual atmosphere",
    "Serious": "serious, focused expression",
    "Energetic": "dynamic, energetic presence",
    "Calm": "calm, peaceful demeanor",
    "Inspiring": "inspiring, motivational presence",
}

# Quality modifiers and the negative prompt, preserved from prompt_generator.py.
QUALITY_TAGS: list[str] = ["masterpiece", "best quality", "highly detailed", "photorealistic"]

NEGATIVE_PROMPT: str = (
    "blurry, low quality, pixelated, distorted, ugly, deformed, "
    "bad anatomy, bad proportions, extra limbs, mutation, "
    "low resolution, jpeg artifacts, watermark, signature, "
    "cartoon, anime, painting, illustration, 3d render"
)


__all__ = [
    "ATTIRE_DETAILS",
    "BACKGROUND_DETAILS",
    "LIGHTING_DETAILS",
    "MOOD_DETAILS",
    "NEGATIVE_PROMPT",
    "PURPOSE_DETAILS",
    "QUALITY_TAGS",
    "VIBE_DETAILS",
]
