# Batch 02_breadth_v131 — confirmation results

**Status:** GATE PASS (breadth entry gate)  
**Codebook:** v1.3.1 · **Model:** `composer-2.5` · k=3  
**Preregistration:** `docs/methods/pilot_theory_dags/BREADTH_RELIABILITY_v131.md`

## Entry gate (Phase 4.1)

| Test | Value | Threshold | Pass |
|---|---:|---:|---|
| α_k breadth (n=30) | **0.889** | ≥ 0.80 | **yes** |
| Span verification | 90/90 (100%) | ≥ 0.98 | **yes** |
| DAG validation | 90/90 | 1.00 | **yes** |

**Decision:** open full-sample extraction under frozen v1.3.1 + composer-2.5 + k=3. Human IRR runs in parallel (pause-if-fail).

## Slice diagnostics (not gates)

| Slice | n | α single | α_k | Mean breadth range | Share range ≥ 2 |
|---|---:|---:|---:|---:|---:|
| All 30 | 30 | 0.727 | **0.889** | 0.90 | 0.13 |
| Dev-15 | 15 | 0.540 | 0.779 | 0.93 | 0.20 |
| Fresh-15 | 15 | 0.761 | **0.905** | 0.87 | 0.07 |

Dev-15 alone is below 0.80; Fresh-15 and the pre-registered pooled 30 clear. Baseline Composer n=50 under v1.3 was α_k = 0.72.

## Other metrics (observe)

| Metric | Value |
|---|---:|
| Mean ARI vs consensus | 0.955 |
| α n_domains | 0.468 |
| Outside two modal D | 0.067 (still fails 0.10; Stage 3 position unchanged) |
| Flagged unstable | 2/30 |

## Comparison to pre-fix baseline

| Battery | Codebook | Model | α_k breadth |
|---|---|---|---:|
| n=50 historical | v1.3 | composer-2.5 | 0.72 |
| **Confirmation n=30** | **v1.3.1** | **composer-2.5** | **0.89** |
