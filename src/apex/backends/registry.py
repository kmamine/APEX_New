"""Select and assemble the configured chat + editor backends."""

from __future__ import annotations

from ..config import Settings
from .base import ChatBackend, EditBackend, ModelBackend
from .fake import FakeChatBackend, FakeEditBackend


def _build_chat(mode: str, settings: Settings) -> ChatBackend:
    if mode == "fake":
        return FakeChatBackend()
    if mode in ("local", "api"):
        # Both speak the OpenAI-compatible protocol; only the endpoint differs.
        from .openai_chat import OpenAICompatibleChatBackend

        return OpenAICompatibleChatBackend(
            base_url=settings.vllm_base_url,
            api_key=settings.vllm_api_key,
            model=settings.mllm_model,
            temperature=settings.mllm_temperature,
            max_tokens=settings.mllm_max_tokens,
        )
    raise ValueError(f"unknown chat backend mode: {mode!r}")


def _build_editor(mode: str, settings: Settings) -> EditBackend:
    if mode == "fake":
        return FakeEditBackend()
    if mode == "local":
        from .local.editor_qwen import QwenImageEditBackend

        return QwenImageEditBackend(model_id=settings.editor_model, device=settings.editor_device)
    if mode == "api":
        from .api.editor_replicate import ReplicateEditBackend

        return ReplicateEditBackend(
            model=settings.editor_model, api_token=settings.replicate_api_token
        )
    raise ValueError(f"unknown editor backend mode: {mode!r}")


def build_chat(settings: Settings) -> ChatBackend:
    """Build the chat backend (cheap to recreate; safe to call per run)."""
    return _build_chat(settings.resolved_chat_backend(), settings)


def build_editor(settings: Settings) -> EditBackend:
    """Build the editor backend (keep warm — the local pipeline reloads otherwise)."""
    return _build_editor(settings.resolved_editor_backend(), settings)


def build_backend(settings: Settings) -> ModelBackend:
    """Build the chat + editor backends from settings (per-capability overrides honored)."""
    return ModelBackend(chat=build_chat(settings), editor=build_editor(settings))


__all__ = ["build_backend", "build_chat", "build_editor"]
