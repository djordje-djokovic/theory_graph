"""Multi-corpus data layout helpers.

Layout:
  data/corpora/<corpus_id>/
    cases.csv
    transcripts/<case_id>.txt
    samples/<sample_name>.csv
    README.md   (optional)

Add a new competition later by creating another folder under corpora/
(e.g. shark_tank) with the same three pieces, then set experiment.corpus.
"""
from __future__ import annotations

from pathlib import Path


def corpora_root(lab_root: Path) -> Path:
    return lab_root / "data" / "corpora"


def corpus_dir(lab_root: Path, corpus_id: str) -> Path:
    d = corpora_root(lab_root) / corpus_id
    if not d.is_dir():
        raise FileNotFoundError(
            f"unknown corpus {corpus_id!r}; expected folder {d}. "
            f"Available: {list_corpora(lab_root)}"
        )
    return d


def list_corpora(lab_root: Path) -> list[str]:
    root = corpora_root(lab_root)
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def cases_csv(lab_root: Path, corpus_id: str) -> Path:
    p = corpus_dir(lab_root, corpus_id) / "cases.csv"
    if not p.exists():
        raise FileNotFoundError(f"missing {p}")
    return p


def transcripts_dir(lab_root: Path, corpus_id: str) -> Path:
    p = corpus_dir(lab_root, corpus_id) / "transcripts"
    if not p.exists():
        raise FileNotFoundError(f"missing {p}")
    return p


def samples_dir(lab_root: Path, corpus_id: str) -> Path:
    p = corpus_dir(lab_root, corpus_id) / "samples"
    if not p.exists():
        raise FileNotFoundError(f"missing {p}")
    return p
