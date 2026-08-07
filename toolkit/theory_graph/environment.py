"""Computational environment capture for encoding runs.

An LLM is a measurement instrument, so a run is only reproducible if the
instrument's settings are recorded. Model name and temperature are not
sufficient for a locally served model: quantization changes token selection,
and the serving version changes defaults, so two runs of "qwen3:32b" at
temperature 0 are not necessarily the same instrument.

Probing is best-effort. A run must never fail because the environment could
not be described, so every lookup here degrades to a recorded reason instead
of raising.
"""
from __future__ import annotations

import json
import os
import platform
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

OLLAMA_PROVIDERS = ("ollama", "ollama_chat")
_TIMEOUT_S = 5
_TRACKED_PACKAGES = ("litellm", "krippendorff", "scikit-learn", "pandas", "numpy")


def _ollama_base_url() -> str:
    raw = os.environ.get("OLLAMA_BASE_URL") or os.environ.get("OLLAMA_HOST")
    return (raw or "http://localhost:11434").rstrip("/")


def _post_json(url: str, payload: dict | None = None) -> dict | None:
    try:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def split_model_ref(model: str) -> tuple[str | None, str]:
    """('ollama_chat/qwen3:32b') -> ('ollama_chat', 'qwen3:32b')."""
    if "/" in model:
        provider, name = model.split("/", 1)
        return provider, name
    return None, model


def probe_ollama(model: str) -> dict:
    """Serving version and weight details for a locally served model."""
    provider, name = split_model_ref(model)
    if provider not in OLLAMA_PROVIDERS:
        return {"probed": False, "reason": f"provider {provider!r} is not Ollama"}

    base = _ollama_base_url()
    out: dict = {"probed": True, "base_url": base, "model_name": name}

    ver = _post_json(f"{base}/api/version")
    out["ollama_version"] = (ver or {}).get("version")

    shown = _post_json(f"{base}/api/show", {"model": name})
    if shown is None:
        out["probed"] = False
        out["reason"] = "Ollama did not answer /api/show"
        return out

    details = shown.get("details") or {}
    out["quantization_level"] = details.get("quantization_level")
    out["parameter_size"] = details.get("parameter_size")
    out["family"] = details.get("family")
    out["weight_format"] = details.get("format")

    info = shown.get("model_info") or {}
    for key, value in info.items():
        # Native training context length; the served window is num_ctx.
        if key.endswith(".context_length"):
            out["model_context_length"] = value
            break

    tags = _post_json(f"{base}/api/tags")
    for entry in (tags or {}).get("models") or []:
        if entry.get("name") == name or entry.get("model") == name:
            out["digest"] = entry.get("digest")
            out["size_bytes"] = entry.get("size")
            break
    return out


def _package_versions() -> dict:
    out = {}
    for name in _TRACKED_PACKAGES:
        try:
            out[name] = pkg_version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def capture(
    *,
    model: str,
    temperature: float | None,
    max_tokens: int | None = None,
    num_ctx: int | None = None,
    backend: str = "api",
) -> dict:
    """Full environment record for one encoding session."""
    provider, _ = split_model_ref(model)
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "inference": {
            "model_id": model,
            "provider": provider,
            "backend": backend,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "num_ctx": num_ctx,
        },
        "serving": probe_ollama(model),
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
        },
        "packages": _package_versions(),
    }


def _fingerprint(env: dict) -> str:
    """Identity of the instrument, ignoring capture time."""
    serving = env.get("serving") or {}
    return json.dumps(
        {
            "inference": env.get("inference"),
            "serving": {k: v for k, v in serving.items() if k != "base_url"},
            "packages": env.get("packages"),
            "runtime": env.get("runtime"),
        },
        sort_keys=True,
    )


def record(run_dir: Path, env: dict) -> Path:
    """Append this session's environment unless it repeats the last one.

    Kept as a log rather than a single file because runs are resumed across
    sessions, so a run's encodings may not all come from one environment.
    """
    path = run_dir / "environment.jsonl"
    if path.exists():
        previous = [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        if previous and _fingerprint(previous[-1]) == _fingerprint(env):
            return path
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(env, ensure_ascii=False) + "\n")
    return path


def provenance_stamp(env: dict) -> dict:
    """Compact instrument identity to embed in each encoding's `meta`.

    Only the fields that change what the model outputs; the full record lives
    in `environment.jsonl`.
    """
    serving = env.get("serving") or {}
    inference = env.get("inference") or {}
    stamp = {
        "num_ctx": inference.get("num_ctx"),
        "max_tokens": inference.get("max_tokens"),
    }
    for key in ("ollama_version", "quantization_level", "parameter_size", "digest"):
        if serving.get(key) is not None:
            stamp[key] = serving[key]
    return {k: v for k, v in stamp.items() if v is not None}
