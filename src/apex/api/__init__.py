"""FastAPI service: app factory, routes, and the in-process run runner."""

from .app import app, create_app

__all__ = ["app", "create_app"]
