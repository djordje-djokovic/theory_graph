# Reference results (share with coauthors)

Analysis-ready outputs for the confirmatory n=375 sample (clean GPU retranscriptions; pilot-108 excluded). Raw LLM encodings are **not** in git — use these CSVs and reports.

## Confirmatory runs (v2.1.1 premises)

| Folder | Model | Passes | Main files |
|--------|--------|--------|------------|
| `full_n375_k3_v211_gpt4o_mini/` | OpenAI gpt-4o-mini | premises k=3, dfv k=3, domains k=3 | `aggregated/dataset.csv`, `analysis/results.md`, `validation/reliability_report.md` |
| `full_n375_k3_v211_qwen3_32b/` | Ollama qwen3:32b | premises k=3 | same layout |

Reproduce regressions without re-encoding:

```powershell
theory-graph analyze --run reference/full_n375_k3_v211_gpt4o_mini
theory-graph analyze --run reference/full_n375_k3_v211_qwen3_32b
```

Or open `aggregated/dataset.csv` in R / Stata / Excel.

## Older baselines

`v1_3_2_nested/` and `v1_5_1_crossed/` are published structure baselines used by CI (`theory-graph reproduce` / `equivalence`). They are not the n375 confirmatory sample.
