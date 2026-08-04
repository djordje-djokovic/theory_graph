# Batch `06_full_remaining`

- Cases: **266** (GotSelected=1: 51)
- Seed: `20260731`
- Model (locked): `composer-2.5` (NOT composer-2.5-fast / lite)
- Codebook: v1.3.2 Pass A structure, k=3
- Status: **extractions complete · scored 2026-07-31**
- Scope: all remaining usable transcripts not in 02/03/04 (includes former 01_expand50 cases)

## Checklist

1. [x] Fill `runs/run1..run3/` using `prompts/` (798/798)
2. [x] Validate each run directory with `scripts/validate_theory_dag.py`
   - run1/2/3: 0 structural failures; span verification **266/266 (100%)** each
   - span fix applied: `pilot-733` run2 P7 (`per-user` not `per-person`/`per-store`)
3. [x] Score with `scripts/theory_dag_stability.py` → `report/`

## Stability (k=3)

| Metric | Value | Rule |
|---|---:|---|
| α_k(breadth) | **0.814** | in-flight pause if &lt; 0.70 → **above pause**; confirmation target ≥ 0.80 → **PASS** |
| Mean ARI vs consensus | 0.963 | ≥ 0.70 → pass |
| Unstable cases | 12/266 | see `report/stability_by_case.csv` |

**Reading:** Full remaining corpus clears the 0.80 confirmation target on breadth aggregate reliability. Partition consensus is strong (ARI 0.963). Domain-count single-run α is lower (0.441) — expected under domain compression; use consensus domain count for analysis.

## Artifacts

- `runs/run{1,2,3}/*.json` + `_measures.csv`
- `report/STABILITY.md`
- `report/stability_summary.json`
- `report/stability_by_case.csv`
