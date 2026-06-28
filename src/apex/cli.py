"""APEX command-line interface."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from PIL import Image

from .config import get_settings
from .goalspec import GoalSpec, goal_from_preset
from .loop import IterationRecord

app = typer.Typer(help="APEX — Agentic Portrait EXperience", no_args_is_help=True)


@app.command()
def run(
    image: Path = typer.Option(..., "--image", "-i", exists=True, help="Input photo."),
    preset: str | None = typer.Option(None, "--preset", "-p", help="Preset name."),
    profile: Path | None = typer.Option(None, "--profile", help="A saved profile JSON."),
    backend: str | None = typer.Option(None, "--backend", help="local | api | fake."),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write the final portrait here."),
) -> None:
    """Run the harness on a photo and report each iteration."""
    from .service.harness import ApexHarness

    settings = get_settings()
    if backend:
        settings = settings.model_copy(update={"backend_mode": backend})

    if profile:
        goal = GoalSpec.from_profile_json(json.loads(profile.read_text()))
    elif preset:
        goal = goal_from_preset(preset)
    else:
        raise typer.BadParameter("provide --preset or --profile")

    harness = ApexHarness(settings)
    state = harness.create_run(goal, Image.open(image).convert("RGB"))
    typer.echo(f"▶ run {state.run_id} (backend={settings.backend_mode})")

    def progress(record: IterationRecord, _name: str) -> None:
        identity = record.metrics.identity.value if record.metrics.identity else float("nan")
        typer.echo(
            f"  iter {record.index}: {record.decision} "
            f"judge={record.judge.overall:.1f} identity={identity:.3f}"
        )

    final = harness.execute_run(state.run_id, progress)
    typer.echo(f"✔ {final.status} (best iteration #{final.final_index})")
    if final.final_image:
        final_path = Path(settings.runs_dir) / f"run_{final.run_id}" / final.final_image
        typer.echo(f"  final: {final_path}")
        if out:
            shutil.copy(final_path, out)
            typer.echo(f"  copied to: {out}")


@app.command()
def serve(
    host: str | None = typer.Option(None, help="Override APEX_HOST."),
    port: int | None = typer.Option(None, help="Override APEX_PORT."),
    reload: bool = typer.Option(False, help="Auto-reload (dev)."),
) -> None:
    """Launch the FastAPI server."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "apex.api.app:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


@app.command()
def doctor() -> None:
    """Check configuration, the MLLM endpoint, and GPU availability."""
    settings = get_settings()
    typer.echo("APEX configuration:")
    typer.echo(f"  backend_mode : {settings.backend_mode}")
    typer.echo(f"  mllm         : {settings.mllm_model} @ {settings.vllm_base_url}")
    typer.echo(f"  editor       : {settings.editor_model} on {settings.editor_device}")

    try:
        import httpx

        resp = httpx.get(f"{settings.vllm_base_url}/models", timeout=5.0)
        typer.echo(f"  MLLM endpoint: reachable (HTTP {resp.status_code})")
    except Exception as exc:
        typer.echo(f"  MLLM endpoint: UNREACHABLE ({exc})")

    try:
        import torch

        if torch.cuda.is_available():
            typer.echo(f"  CUDA         : {torch.cuda.device_count()} device(s)")
        else:
            typer.echo("  CUDA         : not available")
    except ImportError:
        typer.echo("  CUDA         : torch not installed (install the 'local-gpu' extra)")


__all__ = ["app"]
