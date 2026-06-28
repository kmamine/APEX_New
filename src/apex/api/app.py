"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from ..config import Settings, get_settings
from ..service.harness import ApexHarness
from .routes import router
from .runner import InProcessRunner

# Vite dev server origins; same-origin in prod is served via the Vite /api proxy.
DEV_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title="APEX — Agentic Portrait EXperience",
        version=__version__,
        description="Turn a photo into a professional portrait with a quality-assured loop.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.harness = ApexHarness(settings)
    app.state.runner = InProcessRunner(app.state.harness)
    app.include_router(router)
    return app


app = create_app()


__all__ = ["app", "create_app"]
