"""Form-level validation with the legacy user-facing messages preserved.

`GoalSpec` itself is enum-validated by Pydantic, but the UI submits raw strings
(possibly empty for unselected dropdowns). This module validates that raw input
*before* a `GoalSpec` is constructed, returning the same friendly messages the
old Gradio/React app showed (`APEX_old/apex/models/profile.py`,
`APEX_old/apex/utils/validators.py`).
"""

from __future__ import annotations

from pydantic import BaseModel

from .options import option_values

# Exact messages from the legacy implementation.
_REQUIRED_MESSAGES: dict[str, str] = {
    "purpose": "⚠️ Please select a purpose for your portrait",
    "attire": "⚠️ Please select your preferred attire",
    "background": "⚠️ Please select a background style",
    "vibe": "⚠️ Please select your desired vibe",
}
ALL_VALID_MESSAGE = "✅ All inputs valid"

MAX_CUSTOM_NOTES_LENGTH = 1000


class ValidationResult(BaseModel):
    is_valid: bool
    message: str
    missing_fields: list[str] = []


def validate_basic_info(purpose: str, attire: str, background: str, vibe: str) -> tuple[bool, str]:
    """Legacy-compatible check of the four required fields, in order."""
    for field, value in (
        ("purpose", purpose),
        ("attire", attire),
        ("background", background),
        ("vibe", vibe),
    ):
        if not value or not str(value).strip():
            return False, _REQUIRED_MESSAGES[field]
    return True, ALL_VALID_MESSAGE


def validate_goal_form(data: dict[str, object]) -> ValidationResult:
    """Validate a raw form payload: required fields, choice membership, notes length."""
    missing: list[str] = []
    for field in ("purpose", "attire", "background", "vibe"):
        value = data.get(field)
        if not value or not str(value).strip():
            missing.append(field)
    if missing:
        return ValidationResult(
            is_valid=False, message=_REQUIRED_MESSAGES[missing[0]], missing_fields=missing
        )

    # Choice fields must be valid options when provided.
    for field in (
        "purpose",
        "attire",
        "background",
        "vibe",
        "lighting",
        "mood",
        "age_range",
        "gender",
        "ethnicity",
        "resolution",
    ):
        value = data.get(field)
        if value not in (None, "") and str(value) not in option_values(field):
            return ValidationResult(
                is_valid=False,
                message=f"⚠️ '{value}' is not a valid {field.replace('_', ' ')} option",
            )

    notes = data.get("custom_notes")
    if isinstance(notes, str) and len(notes.strip()) > MAX_CUSTOM_NOTES_LENGTH:
        return ValidationResult(
            is_valid=False,
            message=f"⚠️ Custom notes must be {MAX_CUSTOM_NOTES_LENGTH} characters or fewer",
        )

    return ValidationResult(is_valid=True, message=ALL_VALID_MESSAGE)


__all__ = [
    "ALL_VALID_MESSAGE",
    "MAX_CUSTOM_NOTES_LENGTH",
    "ValidationResult",
    "validate_basic_info",
    "validate_goal_form",
]
