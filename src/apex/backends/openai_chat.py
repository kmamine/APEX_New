"""OpenAI-compatible multimodal chat backend with structured output.

Used for BOTH the local vLLM server (gemma) and hosted OpenAI-compatible
endpoints — they differ only by base URL / key. Images are sent as base64 data
URLs; structured output is requested via ``response_format`` json_schema and
validated against the Pydantic model, with one bounded re-ask on a parse error.
"""

from __future__ import annotations

import base64
import io
from collections.abc import Sequence

from openai import OpenAI
from PIL import Image
from pydantic import ValidationError

from .base import TModel


def _data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


class OpenAICompatibleChatBackend:
    """Calls a chat-completions endpoint and returns a validated Pydantic model."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        max_retries: int = 1,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def _content(self, user: str, images: Sequence[Image.Image]) -> list[dict[str, object]]:
        parts: list[dict[str, object]] = [{"type": "text", "text": user}]
        for image in images:
            parts.append({"type": "image_url", "image_url": {"url": _data_url(image)}})
        return parts

    def chat_structured(
        self,
        system: str,
        user: str,
        images: Sequence[Image.Image],
        schema: type[TModel],
    ) -> TModel:
        messages: list[dict[str, object]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": self._content(user, images)},
        ]
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()},
        }

        last_error: Exception | None = None
        for _attempt in range(self.max_retries + 1):
            completion = self._client.chat.completions.create(  # type: ignore[call-overload]
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
            )
            content = completion.choices[0].message.content or ""
            try:
                return schema.model_validate_json(content)
            except ValidationError as exc:
                last_error = exc
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"That did not match the required schema ({exc}). "
                            "Reply again with valid JSON only."
                        ),
                    }
                )
        raise RuntimeError(f"MLLM failed to produce valid {schema.__name__}: {last_error}")


__all__ = ["OpenAICompatibleChatBackend"]
