# Batch 02_breadth_v131 — confirmation battery

**Status:** COMPLETE — entry gate PASS (α_k = 0.889)  
**Results:** `RESULTS.md`  
**Preregistration:** `docs/methods/pilot_theory_dags/BREADTH_RELIABILITY_v131.md`  
**Codebook:** v1.3.1 (§4.1 clarification)  
**Model:** `composer-2.5` · k = 3 · codebook-only prompts

## Composition

| Slice | n | Role |
|---|---:|---|
| dev15 | 15 | Regression check (same ids as stability subsample) |
| fresh15 | 15 | Held-out confirmatory draw (seed 20260731, length tertiles) |
| **Total** | **30** | Primary gate estimate |

## Gate

α_k(breadth) ≥ 0.80 on the 30; span ≥ 0.98; DAG valid 100%.

## Paths

- `cases.csv`, `transcripts/`, `prompts/`
- `runs/run1|run2|run3/` — fill with Pass A JSON (`meta.codebook_version = "1.3.1"`, `meta.model_id = "composer-2.5"`)
