"""Prompt loading + message construction."""
from __future__ import annotations

from pathlib import Path


def prompt_filename(version: str) -> str:
    # accept "v2_0_0" or "v2_0_0.md"
    return version if version.endswith(".md") else f"{version}.md"


def load_prompt(prompts_dir: Path, version: str, snapshot_dir: Path | None = None) -> str:
    """Read a codebook file, preferring the copy frozen into the experiment.

    Codebook files are the audit record for a version, so a run must be read
    back against the text it was actually encoded with rather than whatever
    `prompts/` holds later. Runs created before snapshots existed have no
    snapshot directory and fall back to the shared `prompts/` tree.
    """
    name = prompt_filename(version)
    if snapshot_dir is not None:
        frozen = snapshot_dir / name
        if frozen.exists():
            return frozen.read_text(encoding="utf-8")
    path = prompts_dir / name
    if not path.exists():
        raise FileNotFoundError(f"prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def snapshot_prompts(prompts_dir: Path, versions: list[str], snapshot_dir: Path) -> None:
    """Freeze each codebook file into the experiment folder, once."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for version in dict.fromkeys(versions):
        name = prompt_filename(version)
        dest = snapshot_dir / name
        if dest.exists():
            continue
        src = prompts_dir / name
        if not src.exists():
            raise FileNotFoundError(f"prompt not found: {src}")
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def task_header(codebook_version: str, model_id: str) -> str:
    return f"""# Extraction task — codebook only (v{codebook_version})

Follow the codebook below. Output one JSON object matching the schema.
Do not invent premises not supported by the transcript.
Prefer exact contiguous transcript spans for evidence when possible.
Do not use any outside knowledge about this venture.

MODEL LOCK: You MUST set meta.model_id to "{model_id}" exactly.
"""


def build_user_message(
    *,
    codebook_text: str,
    codebook_version: str,
    case_id: str,
    transcript: str,
    model_id: str,
    extraction_run: int,
    coder_session_id: str | None = None,
    session_case_index: int | None = None,
    frozen_premises: str | None = None,
) -> str:
    session_block = ""
    if coder_session_id:
        session_block = f"\n- coder_session_id: {coder_session_id}"
    if session_case_index is not None:
        session_block += f"\n- session_case_index: {session_case_index}"

    frozen_block = ""
    if frozen_premises is not None:
        frozen_block = f"""
## Frozen premises (fixed; from Pass A — do not add, remove, merge, split, or rename)

{frozen_premises}
"""

    return f"""{task_header(codebook_version, model_id)}

## Codebook

{codebook_text}

## Case

- case_id: {case_id}
- extraction_run: {extraction_run}{session_block}
{frozen_block}
## Transcript

{transcript}

## Output meta (required)

meta.codebook_version = "{codebook_version}"
meta.pass = "structure"
meta.case_id = "{case_id}"
meta.extraction_run = {extraction_run}
meta.model_id = "{model_id}"
meta.model_provider = "litellm"
meta.temperature = null
meta.temperature_controlled = false
meta.extracted_at = <ISO-8601>
"""


def messages_for_case(
    *,
    codebook_text: str,
    codebook_version: str,
    case_id: str,
    transcript: str,
    model_id: str,
    extraction_run: int,
    frozen_premises: str | None = None,
) -> list[dict]:
    user = build_user_message(
        codebook_text=codebook_text,
        codebook_version=codebook_version,
        case_id=case_id,
        transcript=transcript,
        model_id=model_id,
        extraction_run=extraction_run,
        frozen_premises=frozen_premises,
    )
    system = (
        "You are a trained research coder. Return JSON only, conforming to the "
        "codebook schema. No prose outside the JSON object."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
