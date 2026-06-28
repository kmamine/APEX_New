"""Application settings, loaded from environment (prefix ``APEX_``) or ``.env``.

Supersedes the legacy ``apex/config/settings.py``: every old ``APEX_*`` variable
is preserved and new ones are added for backend selection, model endpoints, and
quality thresholds.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from .thresholds import LoopPolicy, QualityThresholds

BackendMode = Literal["local", "api", "fake"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APEX_",
        env_file=".env",
        extra="ignore",
        protected_namespaces=(),  # allow fields like `model_cache`
    )

    # --- UI / server (preserved) ---
    host: str = "127.0.0.1"
    port: int = 8000
    share: bool = False
    profiles_dir: str = "data/profiles"
    uploads_dir: str = "data/uploads"
    runs_dir: str = "data/runs"
    auto_save: bool = True

    # --- Backend selection ---
    backend_mode: BackendMode = "local"
    chat_backend: BackendMode | None = None
    editor_backend: BackendMode | None = None

    # --- MLLM (orchestrator + judge) ---
    vllm_base_url: str = "http://localhost:50033/v1"
    vllm_api_key: str = "dummy-key"
    mllm_model: str = "google/gemma-4-E4B-it"
    mllm_temperature: float = 0.4
    mllm_max_tokens: int = 1024

    # --- Image editor ---
    # Which local editing engine: "qwen" (Qwen-Image-Edit) or "flux"
    # (FLUX.1-Kontext-dev — the fallback if Qwen weights are impractical).
    editor_engine: Literal["qwen", "flux"] = "qwen"
    editor_model: str = "Qwen/Qwen-Image-Edit-2511"  # base repo (text encoder + VAE)
    # Optional GGUF-quantized Qwen transformer (much smaller download); the base
    # repo above still supplies the text encoder + VAE. e.g. a Q4_K_M file (~13 GB).
    editor_gguf_file: str | None = None
    # The MLLM (vLLM) runs on cuda:1, so the editor defaults to cuda:0.
    editor_device: str = "cuda:0"
    num_inference_steps: int = 50
    true_cfg_scale: float = 4.0  # Qwen
    editor_guidance_scale: float = 3.0  # FLUX.1-Kontext
    # Appended to every edit instruction to nudge the editor toward a clean,
    # photographic look (the semantic edit itself comes from the orchestrator).
    editor_style_suffix: str = (
        "professional headshot photography, sharp focus, natural skin texture, "
        "flattering soft studio lighting, high detail, photorealistic"
    )
    replicate_api_token: str | None = None

    # --- Quality thresholds & loop policy ---
    identity_threshold: float = 0.35
    judge_threshold: float = 7.0
    sharpness_min: float = 100.0
    aesthetic_min: float = 5.0
    iqa_min: float = 0.0
    max_iterations: int = 5
    max_identity_fails: int = 2
    enabled_metrics: str | None = None  # comma-separated; None => all enabled

    # --- Misc ---
    model_cache: str = "models"

    # Derived helpers ----------------------------------------------------
    def resolved_chat_backend(self) -> BackendMode:
        return self.chat_backend or self.backend_mode

    def resolved_editor_backend(self) -> BackendMode:
        return self.editor_backend or self.backend_mode

    def thresholds(self) -> QualityThresholds:
        return QualityThresholds(
            identity_threshold=self.identity_threshold,
            judge_threshold=self.judge_threshold,
            sharpness_min=self.sharpness_min,
            aesthetic_min=self.aesthetic_min,
            iqa_min=self.iqa_min,
        )

    def loop_policy(self) -> LoopPolicy:
        return LoopPolicy(
            max_iterations=self.max_iterations,
            max_identity_fails=self.max_identity_fails,
        )

    def enabled_metric_names(self) -> list[str] | None:
        if not self.enabled_metrics:
            return None
        return [name.strip() for name in self.enabled_metrics.split(",") if name.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()


__all__ = ["BackendMode", "Settings", "get_settings"]
