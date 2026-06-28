"""Pluggable model backends (chat + image editor): local / api / fake."""

from .base import ChatBackend, EditBackend, EditRequest, EditResult, ModelBackend
from .fake import FakeChatBackend, FakeEditBackend, fake_backend
from .registry import build_backend, build_chat, build_editor

__all__ = [
    "ChatBackend",
    "EditBackend",
    "EditRequest",
    "EditResult",
    "FakeChatBackend",
    "FakeEditBackend",
    "ModelBackend",
    "build_backend",
    "build_chat",
    "build_editor",
    "fake_backend",
]
