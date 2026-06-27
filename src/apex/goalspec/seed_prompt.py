"""Turn a :class:`GoalSpec` into MLLM context.

The legacy `prompt_generator.py` concatenated the detail dictionaries into one
Flux text prompt. Here the same descriptive strings become a structured *brief*
handed to the MLLM, plus the shared **acceptance rubric** that both the
orchestrator (to plan edits) and the judge (to score them) reason against.
"""

from __future__ import annotations

from .detail_dicts import (
    ATTIRE_DETAILS,
    BACKGROUND_DETAILS,
    LIGHTING_DETAILS,
    MOOD_DETAILS,
    PURPOSE_DETAILS,
    VIBE_DETAILS,
)
from .models import GoalSpec

#: Criteria the judge scores 0-10 and the orchestrator optimizes toward.
ACCEPTANCE_CRITERIA: list[dict[str, str]] = [
    {
        "key": "identity",
        "label": "Identity preservation",
        "description": "The subject is unmistakably the same person as the input photo.",
    },
    {
        "key": "attire",
        "label": "Attire match",
        "description": "Clothing matches the requested attire.",
    },
    {
        "key": "background",
        "label": "Background match",
        "description": "The background matches the requested setting.",
    },
    {
        "key": "vibe",
        "label": "Vibe & expression",
        "description": "Expression and posture convey the requested vibe.",
    },
    {
        "key": "lighting",
        "label": "Lighting & mood",
        "description": "Lighting and overall mood match the request.",
    },
    {
        "key": "professionalism",
        "label": "Professional quality",
        "description": "Reads as a polished, professional portrait suitable for its purpose.",
    },
]

ORCHESTRATOR_SYSTEM_PROMPT = (
    "You are APEX, an expert photo retoucher that turns an ordinary photo into a "
    "professional portrait by issuing one concise image-edit instruction at a time. "
    "You are given the target brief, the current image, and feedback from the previous "
    "attempt. Plan the single most impactful next edit. NON-NEGOTIABLE: never alter the "
    "person's facial identity, bone structure, or distinguishing features — only adjust "
    "attire, background, lighting, framing, grooming and color. Prefer gentle, targeted "
    "edits over drastic ones. Respond only via the provided JSON schema."
)

JUDGE_SYSTEM_PROMPT = (
    "You are APEX's portrait quality judge. Compare the edited image against the target "
    "brief and score each acceptance criterion from 0 (poor) to 10 (excellent). Be "
    "critical and concrete. Identity preservation is paramount: if the person no longer "
    "looks like the input, score identity low regardless of aesthetics. Respond only via "
    "the provided JSON schema."
)


def build_goal_brief(goal: GoalSpec) -> str:
    """Render the goal as an explicit, labeled target brief for the MLLM."""
    b, a = goal.basic_info, goal.advanced_settings
    lines = [
        f"- Purpose: {b.purpose} ({PURPOSE_DETAILS[b.purpose]})",
        f"- Attire: {b.attire} ({ATTIRE_DETAILS[b.attire]})",
        f"- Background: {b.background} ({BACKGROUND_DETAILS[b.background]})",
        f"- Vibe: {b.vibe} ({VIBE_DETAILS[b.vibe]})",
        f"- Lighting: {a.lighting} ({LIGHTING_DETAILS[a.lighting]})",
        f"- Mood: {a.mood} ({MOOD_DETAILS[a.mood]})",
    ]
    if a.age_range != "Not Specified":
        lines.append(f"- Age range: {a.age_range}")
    if a.gender != "Not Specified":
        lines.append(f"- Gender presentation: {a.gender}")
    if a.ethnicity != "Not Specified":
        lines.append(f"- Ethnicity: {a.ethnicity}")
    lines.append(f"- Output resolution: {a.resolution}")
    if goal.additional_info.custom_notes:
        lines.append(f"- Additional notes: {goal.additional_info.custom_notes.strip()}")
    return "TARGET PORTRAIT BRIEF:\n" + "\n".join(lines)


def build_orchestrator_user_prompt(goal: GoalSpec, prior_feedback: str | None = None) -> str:
    brief = build_goal_brief(goal)
    if prior_feedback:
        feedback = f"\n\nFEEDBACK FROM PREVIOUS ATTEMPT:\n{prior_feedback}"
    else:
        feedback = "\n\nThis is the first edit; the attached image is the original photo."
    return (
        f"{brief}{feedback}\n\n"
        "Decide the single next edit instruction that best moves the current image toward "
        "the brief while preserving identity."
    )


def build_judge_user_prompt(goal: GoalSpec) -> str:
    brief = build_goal_brief(goal)
    criteria = "\n".join(f"- {c['label']}: {c['description']}" for c in ACCEPTANCE_CRITERIA)
    return (
        f"{brief}\n\nScore the attached edited image on each criterion (0-10):\n{criteria}\n\n"
        "Then give an overall score and decide whether it is acceptable."
    )


__all__ = [
    "ACCEPTANCE_CRITERIA",
    "JUDGE_SYSTEM_PROMPT",
    "ORCHESTRATOR_SYSTEM_PROMPT",
    "build_goal_brief",
    "build_judge_user_prompt",
    "build_orchestrator_user_prompt",
]
