"""Hosted API backends: Qwen-Image-Edit via Replicate (chat reuses openai_chat)."""

from .editor_replicate import ReplicateEditBackend

__all__ = ["ReplicateEditBackend"]
