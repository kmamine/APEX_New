"""ProfileStore save/load/list/delete round-trips."""

from __future__ import annotations

from pathlib import Path

from apex.goalspec import GoalSpec
from apex.persistence import ProfileStore


def test_save_and_load_round_trip(tmp_path: Path, sample_goal: GoalSpec) -> None:
    store = ProfileStore(tmp_path)
    path = store.save(sample_goal, "my_profile.json")
    assert path.exists()
    loaded = store.load("my_profile.json")
    assert loaded is not None
    assert loaded.to_profile_json() == sample_goal.to_profile_json()


def test_save_generates_timestamped_filename(tmp_path: Path, sample_goal: GoalSpec) -> None:
    store = ProfileStore(tmp_path)
    path = store.save(sample_goal)
    assert path.name.startswith("portrait_profile_")
    assert path.suffix == ".json"


def test_list_and_delete(tmp_path: Path, sample_goal: GoalSpec) -> None:
    store = ProfileStore(tmp_path)
    store.save(sample_goal, "a.json")
    store.save(sample_goal, "b.json")
    assert store.list() == ["a.json", "b.json"]
    assert store.delete("a.json") is True
    assert store.list() == ["b.json"]
    assert store.delete("a.json") is False  # already gone


def test_load_missing_returns_none(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path)
    assert store.load("nope.json") is None


def test_loads_legacy_profile(tmp_path: Path, legacy_profile_path: Path) -> None:
    store = ProfileStore(tmp_path)
    (tmp_path / "legacy.json").write_text(
        legacy_profile_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    loaded = store.load("legacy.json")
    assert loaded is not None
    assert loaded.metadata.version == "2.0"
