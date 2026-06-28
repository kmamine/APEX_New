"""API contract + end-to-end run on the fake backend (no GPU)."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from apex.api.app import create_app
from apex.config import Settings


@pytest.fixture
def client(tmp_path) -> TestClient:
    settings = Settings(
        backend_mode="fake",
        profiles_dir=str(tmp_path / "profiles"),
        runs_dir=str(tmp_path / "runs"),
        uploads_dir=str(tmp_path / "uploads"),
        judge_threshold=7.0,
        sharpness_min=50.0,
    )
    return TestClient(create_app(settings))


def _noise_png() -> bytes:
    import numpy as np

    rng = np.random.default_rng(7)
    arr = rng.integers(0, 256, size=(128, 128, 3), dtype="uint8")
    buffer = io.BytesIO()
    Image.fromarray(arr, "RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["backend_mode"] == "fake"


def test_options_and_presets(client: TestClient) -> None:
    options = client.get("/api/v1/options").json()
    assert set(options["fields"]) >= {"purpose", "attire", "resolution"}
    presets = client.get("/api/v1/presets").json()
    assert any(p["name"] == "LinkedIn Professional" for p in presets)


def test_goal_validation_endpoint(client: TestClient) -> None:
    resp = client.post("/api/v1/goal/validate", json={"purpose": "", "attire": "Business Formal"})
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is False


def test_run_lifecycle_with_preset(client: TestClient) -> None:
    start = client.post(
        "/api/v1/runs",
        data={"preset": "LinkedIn Professional"},
        files={"image": ("photo.png", _noise_png(), "image/png")},
    )
    assert start.status_code == 202
    run_id = start.json()["run_id"]

    # The SSE stream drives the run to completion (TestClient consumes it fully).
    with client.stream("GET", f"/api/v1/runs/{run_id}/events") as stream:
        events = [line for line in stream.iter_lines() if line.startswith("event:")]
    assert any("snapshot" in e for e in events)

    detail = client.get(f"/api/v1/runs/{run_id}").json()
    assert detail["status"] == "completed"
    assert detail["iterations"]
    assert detail["final_image_url"]

    # Final image is downloadable.
    img = client.get(detail["final_image_url"])
    assert img.status_code == 200
    assert img.headers["content-type"] == "image/png"


def test_unknown_run_404(client: TestClient) -> None:
    assert client.get("/api/v1/runs/nope").status_code == 404
