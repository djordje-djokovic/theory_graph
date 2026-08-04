# Batch `03_full_v151_w02` — full-sample crossed v1.5.1

- Cases: **48** (GotSelected=1: 11)
- Files: 144 (48 × 3)
- Sessions: 6
- Codebook: v1.5.1
- Model (locked): `composer-2.5` (NOT fast/lite)
- Status: **extraction in progress**

## Model lock

1. Launch each session with model = `composer-2.5` (never omit → fast; never lite).
2. Every JSON: `meta.model_id = "composer-2.5"`, `meta.codebook_version = "1.5.1"`.
3. Before scoring: `python scripts/audit_model_provenance.py C:/Projects/uni/sources/entrepreneurial_theories/data/theory_dags/corpus_v1_5/batches/03_full_v151_w02`
