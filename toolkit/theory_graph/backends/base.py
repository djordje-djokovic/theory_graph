"""Shared EncodeResult dataclass (used by backends)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EncodeResult:
    text: str
    raw: str
    model_id: str
    provider: str
    usage: dict | None = None
