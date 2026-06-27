"""Fake backend behavior + backend registry selection."""

from __future__ import annotations

from PIL import Image

from apex.backends import EditRequest, build_backend
from apex.backends.fake import FakeChatBackend, FakeEditBackend
from apex.config import Settings
from apex.mllm.schemas import JudgeResult, OrchestrationResult


def test_fake_chat_returns_valid_orchestration() -> None:
    chat = FakeChatBackend()
    result = chat.chat_structured("sys", "user", [], OrchestrationResult)
    assert isinstance(result, OrchestrationResult)
    assert result.next_edit.instruction


def test_fake_chat_judge_score_ramps() -> None:
    chat = FakeChatBackend()
    first = chat.chat_structured("s", "u", [], JudgeResult)
    second = chat.chat_structured("s", "u", [], JudgeResult)
    assert second.overall > first.overall


def test_fake_editor_resizes_to_requested_size(solid_image: Image.Image) -> None:
    result = FakeEditBackend().edit_image(
        EditRequest(input_image=solid_image, instruction="x", width=64, height=48)
    )
    assert result.image.size == (64, 48)
    assert result.meta["backend"] == "fake"


def test_build_backend_fake() -> None:
    backend = build_backend(Settings(backend_mode="fake"))
    assert isinstance(backend.chat, FakeChatBackend)
    assert isinstance(backend.editor, FakeEditBackend)
