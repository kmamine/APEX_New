"""Profile persistence — save/load/list/delete goals as JSON.

Ports `APEX_old/apex/core/profile_manager.py` (same filename scheme and JSON
shape) onto :class:`GoalSpec`, so profiles written by the legacy app still load.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..goalspec import GoalSpec


class ProfileStore:
    """File-backed store of portrait goals (one JSON file per profile)."""

    def __init__(self, profiles_dir: str | Path = "data/profiles") -> None:
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def save(self, goal: GoalSpec, filename: str | None = None) -> Path:
        """Write a goal to JSON. Defaults to a timestamped filename."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portrait_profile_{timestamp}.json"
        if not filename.endswith(".json"):
            filename += ".json"

        path = self.profiles_dir / filename
        path.write_text(
            json.dumps(goal.to_profile_json(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def load(self, filename: str) -> GoalSpec | None:
        """Load a goal by filename, or None if missing / invalid."""
        path = self.profiles_dir / filename
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return GoalSpec.from_profile_json(data)
        except (json.JSONDecodeError, OSError, ValueError):
            return None

    def list(self) -> list[str]:
        """List saved profile filenames (sorted)."""
        if not self.profiles_dir.exists():
            return []
        return sorted(p.name for p in self.profiles_dir.glob("*.json"))

    def delete(self, filename: str) -> bool:
        """Delete a profile; return True if it existed and was removed."""
        path = self.profiles_dir / filename
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False


__all__ = ["ProfileStore"]
