"""APEX — Agentic Portrait EXperience.

An agentic harness that turns a user's photo into a professional portrait by
*editing* it (image-to-image), wrapped in a quality-assurance loop: one
multimodal LLM both orchestrates the next edit and judges the result, while
deterministic metrics (identity preservation, face presence, sharpness,
aesthetic, no-reference IQA) gate each iteration.
"""

__version__ = "3.0.0"

__all__ = ["__version__"]
