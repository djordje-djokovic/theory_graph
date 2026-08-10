# Results for coauthors (start here)

You do **not** need to run any code, install anything, or call any AI.

This folder has the finished analysis files for our confirmatory study: **375 startup pitches**, with cleaned full-pitch transcripts. One company (`pilot-108`) was excluded because the available video was for a different company of the same name.

If you later want to re-run regressions with the toolkit (still without calling an AI), see the optional section at the bottom, or the root [`README.md`](../README.md) section **Quick start: run the analysis**.

---

## What we measured

For each pitch, an AI listed the founder’s distinct claims (**premises**). The count of those claims is **breadth**. We then checked whether breadth predicts whether the startup was **selected** at Startup Battlefield (`GotSelected`).

On the GPT-4o-mini run we also have exploratory extras:

- **DFV tags** — is each claim about desirability, feasibility, or viability?
- **Domains** — how those claims group into strategic themes

Encoding (calling the AI) already happened. These folders are the **analysis handoff**: spreadsheets and regression tables. You do not need the raw AI JSON files to read or re-estimate the models.

---

## The two runs to look at

Open these folders after cloning or downloading the repo:

### 1. Primary run — GPT-4o-mini

Folder: `reference/full_n375_k3_v211_gpt4o_mini/`

- Most complete run (premises + DFV tags + domain groupings)
- Better measurement quality of the two models
- Open these files:

| File | What it is | Open with |
|------|------------|-----------|
| `aggregated/dataset.csv` | Spreadsheet: one row per pitch, all variables | Excel, Google Sheets, R, Stata |
| `analysis/results.md` | Regression tables (logit models) | Any text editor, VS Code, or Cursor |
| `validation/reliability_report.md` | How consistently the AI agreed with itself across 3 repeats | Same as above |

### 2. Comparison run — Qwen3-32b

Folder: `reference/full_n375_k3_v211_qwen3_32b/`

- Same 375 pitches and same premise-extraction instructions
- Premises only (no DFV / domains)
- Same three file types as above

---

## Plain-language takeaway (so far)

On these clean full-pitch transcripts:

1. **No clear inverted-U** for total premise count (breadth) predicting selection. Neither model finds a significant “sweet spot,” though the GPT-4o-mini direction looks right and is worth a closer check.
2. **GPT-4o-mini** is the more reliable coder (more consistent when asked three times).
3. On the GPT-4o-mini run, **feasibility-related claims** show a clearer positive association with selection (exploratory). Industry patterns also look worth following up; treat these as leads, not final confirmatory tests.

Exact coefficients are in each folder’s `analysis/results.md`.

---

## Important columns in `dataset.csv`

| Column | Meaning |
|--------|---------|
| `case_id` / `name` | Which pitch |
| `GotSelected` | 1 = selected, 0 = not |
| `breadth` | Number of premises (median of 3 AI runs) |
| `word_count` | Length of the transcript (control) |
| `breadth_D`, `breadth_F`, `breadth_V` | Counts of desirability / feasibility / viability tags *(GPT-4o-mini only)* |
| `n_domains` | Number of strategic theme groups *(GPT-4o-mini only)* |

Other columns are controls or diagnostics; you can ignore them at first.

---

## What you can ignore

| Path | Why |
|------|-----|
| `reference/v1_3_2_nested/`, `reference/v1_5_1_crossed/` | Older software baselines, **not** this confirmatory sample |
| `experiments/` | Local working runs / raw AI JSON (often not in git). Shareable results are here under `reference/` |
| Root `README.md` toolkit sections | How to re-run stats with the CLI, or (later) encode with a new model. Not required just to read results |

---

## Optional: re-run the stats (still no AI)

Only if the toolkit is installed. Otherwise open the CSV and `results.md` files above.

```powershell
theory-graph analyze --run reference/full_n375_k3_v211_gpt4o_mini
theory-graph analyze --run reference/full_n375_k3_v211_qwen3_32b
```

That refreshes `analysis/results.md` from `aggregated/dataset.csv`. It does **not** call an LLM and does **not** require re-encoding.

To try a different model or prompt on the transcripts, that is the separate **encoding** path in the root [`README.md`](../README.md).
