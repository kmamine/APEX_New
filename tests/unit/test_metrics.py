"""Deterministic, GPU-free metric tests + report aggregation."""

from __future__ import annotations

from PIL import Image

from apex.backends.fake import _mild_enhance
from apex.config import QualityThresholds
from apex.metrics import (
    FacePresence,
    Sharpness,
    StubIdentity,
    build_metrics,
    evaluate_image,
)


def test_sharpness_discriminates(noise_image: Image.Image, solid_image: Image.Image) -> None:
    metric = Sharpness(threshold=100.0)
    noisy = metric.compute(noise_image, noise_image)
    flat = metric.compute(solid_image, solid_image)
    assert noisy.value > flat.value
    assert noisy.passed and not flat.passed


def test_stub_identity_high_for_mild_edit(noise_image: Image.Image) -> None:
    metric = StubIdentity(threshold=0.35)
    result = metric.compute(noise_image, _mild_enhance(noise_image))
    assert result.is_hard_gate
    assert result.value >= 0.9
    assert result.passed


def test_face_presence_zero_faces_fails(solid_image: Image.Image) -> None:
    result = FacePresence().compute(solid_image, solid_image)
    assert result.value == 0.0
    assert not result.passed


def test_evaluate_image_builds_report(noise_image: Image.Image) -> None:
    metrics = build_metrics(
        QualityThresholds(), enabled=["identity", "sharpness"], identity_impl="stub"
    )
    report = evaluate_image(metrics, noise_image, _mild_enhance(noise_image))
    assert report.identity is not None
    assert report.identity_passed
    assert report.score("sharpness") is not None
