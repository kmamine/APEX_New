"""Validation parity with the legacy app + new form-level checks."""

from __future__ import annotations

from apex.goalspec import validate_basic_info, validate_goal_form
from apex.goalspec.validation import ALL_VALID_MESSAGE, MAX_CUSTOM_NOTES_LENGTH

VALID = {
    "purpose": "LinkedIn",
    "attire": "Business Formal",
    "background": "Corporate Office",
    "vibe": "Confident",
}


# --- legacy parity (ported from APEX_old/tests/test_basic.py) ---
def test_validate_basic_info_valid() -> None:
    is_valid, message = validate_basic_info(
        "LinkedIn", "Business Formal", "Corporate Office", "Confident"
    )
    assert is_valid
    assert message == ALL_VALID_MESSAGE


def test_validate_basic_info_invalid() -> None:
    is_valid, message = validate_basic_info("", "Business Formal", "Corporate Office", "Confident")
    assert not is_valid
    assert "purpose" in message


# --- new form-level validation ---
def test_validate_goal_form_valid() -> None:
    result = validate_goal_form(VALID)
    assert result.is_valid
    assert result.missing_fields == []


def test_validate_goal_form_reports_missing() -> None:
    result = validate_goal_form({**VALID, "vibe": ""})
    assert not result.is_valid
    assert result.missing_fields == ["vibe"]
    assert "vibe" in result.message


def test_validate_goal_form_rejects_bad_choice() -> None:
    result = validate_goal_form({**VALID, "lighting": "Disco Ball"})
    assert not result.is_valid
    assert "lighting" in result.message


def test_validate_goal_form_rejects_long_notes() -> None:
    result = validate_goal_form({**VALID, "custom_notes": "x" * (MAX_CUSTOM_NOTES_LENGTH + 1)})
    assert not result.is_valid
