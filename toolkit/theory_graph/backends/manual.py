"""Manual backend: expects junior to drop JSON into encodings/run{k}/{case_id}.json."""
from __future__ import annotations

from pathlib import Path

from .base import EncodeResult


class ManualBackend:
    """Does not call an LLM. Use status/encode --resume after files are placed."""

    def __init__(self, encodings_dir: Path | None = None):
        self.encodings_dir = encodings_dir

    def complete(
        self,
        messages: list[dict],
        *,
        model: str = "manual",
        temperature: float = 0.0,
        max_tokens: int = 0,
        timeout_s: int = 0,
    ) -> EncodeResult:
        raise RuntimeError(
            "backend=manual does not call an LLM. Place completed JSON files "
            "under encodings/run{k}/{case_id}.json then run: theory-graph measure"
        )
