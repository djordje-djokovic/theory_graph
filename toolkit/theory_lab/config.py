"""Experiment config schema (YAML)."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ExperimentBlock(BaseModel):
    prompt_version: str
    corpus: str = "startup_battlefield"
    sample: str = "smoke_n20"
    design: Literal["nested", "crossed"] = "nested"


class LlmBlock(BaseModel):
    model: str = "openai/gpt-4.1"
    temperature: float = 0.0
    max_tokens: int = 6000
    timeout_s: int = 120


class EncodingBlock(BaseModel):
    backend: Literal["api", "manual"] = "api"
    k_runs: int = Field(default=3, ge=1, le=10)
    json_retry: int = Field(default=2, ge=0, le=5)


class ExperimentConfig(BaseModel):
    experiment: ExperimentBlock
    llm: LlmBlock = Field(default_factory=LlmBlock)
    encoding: EncodingBlock = Field(default_factory=EncodingBlock)

    @classmethod
    def load(cls, path: Path) -> "ExperimentConfig":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def dump(self, path: Path) -> None:
        path.write_text(
            yaml.safe_dump(self.model_dump(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
