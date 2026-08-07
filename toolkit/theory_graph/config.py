"""Experiment config schema (YAML)."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


DEFAULT_JOIN_COLUMNS = [
    "GotSelected",
    "event",
    "eventID",
    "year",
    "industry",
    "BMI",
    "zBMI",
    "Gender",
    "Attractiveness",
    "zAttractiveness",
    "AgeAI",
    "zAgeAI",
    "RaceAI",
    "zRaceAI",
    "ent_formality_13",
    "presenter_count",
    "know_cent_biz",
    "cust_cent_biz",
    "word_count",
]


class ExperimentBlock(BaseModel):
    prompt_version: str
    run_id: str | None = None
    corpus: str = "startup_battlefield"
    sample: str = "smoke_n20"
    design: Literal["nested", "crossed"] = "nested"


class PassBlock(BaseModel):
    name: str
    prompt_version: str
    k_runs: int = Field(default=1, ge=1, le=10)
    requires: str | None = None


class LlmBlock(BaseModel):
    model: str = "openai/gpt-4.1"
    temperature: float = 0.0
    max_tokens: int = 6000
    timeout_s: int = 120
    num_ctx: int | None = None
    """Context window (tokens) forwarded to Ollama models only. Ollama's server
    default (commonly 2048-4096) silently truncates long codebook+transcript
    prompts, which can cause the model to ignore frozen upstream premises.
    Leave unset for cloud providers (ignored for non-Ollama models)."""


class EncodingBlock(BaseModel):
    backend: Literal["api", "manual"] = "api"
    k_runs: int = Field(default=3, ge=1, le=10)
    json_retry: int = Field(default=2, ge=0, le=5)
    run_passes: list[str] | None = None


class EmbeddingsBlock(BaseModel):
    enabled: bool = False
    model: str = "openai/text-embedding-3-small"
    source: Literal["transcript", "premises"] = "transcript"


class SimilaritiesBlock(BaseModel):
    enabled: bool = True
    method: Literal["tfidf"] = "tfidf"


class DatasetBlock(BaseModel):
    outcome: str = "GotSelected"
    join_columns: list[str] | None = None
    embeddings: EmbeddingsBlock = Field(default_factory=EmbeddingsBlock)
    similarities: SimilaritiesBlock = Field(default_factory=SimilaritiesBlock)


class AnalysisModelBlock(BaseModel):
    name: str
    formula: str
    when: str | None = None


class AnalysisBlock(BaseModel):
    preset: Literal["battlefield", "custom"] = "battlefield"
    outcome: str = "GotSelected"
    models: list[AnalysisModelBlock] | None = None


STANDARD_PASSES: dict[str, PassBlock] = {
    "premises": PassBlock(name="premises", prompt_version="v2_1_0_premises", k_runs=3),
    "dfv": PassBlock(name="dfv", prompt_version="v2_1_0_dfv", k_runs=1, requires="premises"),
    "domains": PassBlock(
        name="domains", prompt_version="v2_1_0_domains", k_runs=1, requires="premises"
    ),
}


class ExperimentConfig(BaseModel):
    experiment: ExperimentBlock
    llm: LlmBlock = Field(default_factory=LlmBlock)
    encoding: EncodingBlock = Field(default_factory=EncodingBlock)
    passes: list[PassBlock] | None = None
    dataset: DatasetBlock = Field(default_factory=DatasetBlock)
    analysis: AnalysisBlock = Field(default_factory=AnalysisBlock)

    def resolved_passes(self) -> list[PassBlock]:
        if self.passes:
            # Backfill `requires` for recognized pass names (premises/dfv/domains)
            # when a custom `passes:` block omits it. Without this, a config that
            # redeclares a standard pass without repeating `requires: premises`
            # silently loses the upstream-premises link: the pass still runs, but
            # never receives the frozen premise list, and the model free-styles
            # its own premises instead of the ones fixed by Pass A.
            fixed = []
            for p in self.passes:
                if p.requires is None and p.name in STANDARD_PASSES:
                    p = p.model_copy(update={"requires": STANDARD_PASSES[p.name].requires})
                fixed.append(p)
            return fixed
        return [
            PassBlock(
                name="structure",
                prompt_version=self.experiment.prompt_version,
                k_runs=self.encoding.k_runs,
            )
        ]

    def resolved_join_columns(self) -> list[str]:
        return self.dataset.join_columns or list(DEFAULT_JOIN_COLUMNS)

    @classmethod
    def load(cls, path: Path) -> "ExperimentConfig":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def dump(self, path: Path) -> None:
        path.write_text(
            yaml.safe_dump(self.model_dump(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def downstream_passes(all_passes: list[PassBlock], roots: set[str]) -> list[PassBlock]:
    return [p for p in all_passes if p.name not in roots and p.requires and p.requires in roots]


def standard_pass(name: str, *, default_k_runs: int = 3) -> PassBlock:
    if name not in STANDARD_PASSES:
        raise RuntimeError(f"unknown pass {name!r} (use premises, dfv, or domains)")
    p = STANDARD_PASSES[name].model_copy(deep=True)
    if name == "premises":
        p.k_runs = default_k_runs
    return p
