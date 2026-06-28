"""Image editing: a backend-agnostic wrapper + optional identity restoration."""

from .identity_restore import IdentityRestorer
from .image_editor import ImageEditor

__all__ = ["IdentityRestorer", "ImageEditor"]
