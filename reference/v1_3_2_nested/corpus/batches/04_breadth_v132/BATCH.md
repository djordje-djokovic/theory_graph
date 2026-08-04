# Batch `04_breadth_v132`

- Cases: **30** (GotSelected=1: 9)
- Seed: `20260731`
- Model (locked): `composer-2.5`
- Codebook: v1.3.2 Pass A structure, k=3
- Status: **extractions complete · scored 2026-07-31**

## Checklist

1. [x] Fill `runs/run1..run3/` using `prompts/` (90/90)
2. [x] Validate each run directory with `scripts/validate_theory_dag.py`
   - run1/2/3: 0 structural failures; span verification **30/30 (100%)** each
3. [x] Score with `scripts/theory_dag_stability.py` → `report/`

## Stability (k=3)

| Metric | Value | Rule |
|---|---:|---|
| α_k(breadth) | **0.789** (re-score after duplicate-chunk overwrite settled) | in-flight pause if &lt; 0.70 → **above pause** |
| Mean ARI vs consensus | 0.856 | ≥ 0.70 → pass |
| Unstable cases | see `report/stability_by_case.csv` | |

**Reading:** After the duplicate-coding race settled, re-validation + re-scoring gives α_k = **0.789** on v1.3.2. On the **same 30 cases**, v1.3.1 gives **0.798** — the codebook difference is negligible. The earlier 0.696 was contaminated by mid-task duplicate overwrites. Both codebooks land just below the 0.80 confirmation target but above the 0.70 pause line.

## Artifacts

- `runs/run{1,2,3}/*.json` + `_measures.csv`
- `report/STABILITY.md`
- `report/stability_summary.json`
- `report/stability_by_case.csv`
