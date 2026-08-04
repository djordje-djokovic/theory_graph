# Batch `03_prod50`

- Cases: **50** (GotSelected=1: 15)
- Seed: `20260731`
- Model (locked): `composer-2.5`
- Codebook: v1.3.1 Pass A structure, k=3
- Status: **extractions complete · scored 2026-07-31**

## Checklist

1. [x] Fill `runs/run1..run3/` using `prompts/` (150/150)
2. [x] Validate each run directory with `scripts/validate_theory_dag.py`
   - run1/2/3: 0 structural failures; span verification **50/50 (100%)** each
3. [x] Score with `scripts/theory_dag_stability.py` → `report/`

## Stability (k=3)

| Metric | Value | Rule |
|---|---:|---|
| α_k(breadth) | **0.731** | in-flight pause if &lt; 0.70 → **above pause**; confirmation target ≥ 0.80 → **miss** |
| Mean ARI vs consensus | 0.849 | ≥ 0.70 → pass |
| Unstable cases | 15/50 | see `report/stability_by_case.csv` |

**Decision under locked scale-up rules:** do **not** hard-pause (α_k ≥ 0.70). α_k is below the confirmation gate (0.80); collaborator call whether to continue the next batch, diagnose the 15 unstable cases, or hold for human IRR.

## Artifacts

- `runs/run{1,2,3}/*.json` + `_measures.csv`
- `report/STABILITY.md`
- `report/stability_summary.json`
- `report/stability_by_case.csv`
