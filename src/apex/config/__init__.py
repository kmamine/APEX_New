"""Configuration: settings (env-driven) and quality thresholds / loop policy."""

from .settings import BackendMode, Settings, get_settings
from .thresholds import LoopPolicy, QualityThresholds

__all__ = ["BackendMode", "LoopPolicy", "QualityThresholds", "Settings", "get_settings"]
