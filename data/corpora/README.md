# Corpora

Each text source is one folder (competition pitches, written plans, interview
transcripts, …):

```
data/corpora/<corpus_id>/
  cases.csv                 # DV + controls (one row per case)
  transcripts/<case_id>.txt
  samples/
    smoke_n20.csv
    full_….csv
  README.md                 # optional notes for this corpus
```

## Current

| corpus_id | Description |
|---|---|
| `startup_battlefield` | TechCrunch Startup Battlefield pitches (Study 2) — reference corpus |

## Add a new corpus (e.g. Shark Tank)

1. Create `data/corpora/shark_tank/` with the same layout.
2. Put texts in `transcripts/` as `<case_id>.txt`.
3. Build `cases.csv` with at least: `id`, `case_id`, and your DV/control columns (`GotSelected` or another outcome — map names consistently for analyze).
4. Add sample CSVs under `samples/`.
5. In your experiment YAML set:

```yaml
experiment:
  corpus: shark_tank
  sample: smoke_n20
  …
```

The toolkit resolves paths via `experiment.corpus`; no code change required for a new folder that follows this layout.
