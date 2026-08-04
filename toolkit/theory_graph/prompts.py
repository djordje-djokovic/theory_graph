"""Prompt loading + message construction."""
from __future__ import annotations

from pathlib import Path


def load_prompt(prompts_dir: Path, version: str) -> str:
    # accept "v2_0_0" or "v2_0_0.md"
    name = version if version.endswith(".md") else f"{version}.md"
    path = prompts_dir / name
    if not path.exists():
        raise FileNotFoundError(f"prompt not found: {path}")
    return path.read_text(encoding="utf-8")


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
) -> str:
    session_block = ""
    if coder_session_id:
        session_block = f"\n- coder_session_id: {coder_session_id}"
    if session_case_index is not None:
        session_block += f"\n- session_case_index: {session_case_index}"

    return f"""{task_header(codebook_version, model_id)}

## Codebook

{codebook_text}

## Case

- case_id: {case_id}
- extraction_run: {extraction_run}{session_block}

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
) -> list[dict]:
    user = build_user_message(
        codebook_text=codebook_text,
        codebook_version=codebook_version,
        case_id=case_id,
        transcript=transcript,
        model_id=model_id,
        extraction_run=extraction_run,
    )
    system = (
        "You are a trained research coder. Return JSON only, conforming to the "
        "codebook schema. No prose outside the JSON object."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
