# Results for coauthors (start here)

You do **not** need to run any code or call any AI.

This folder has the finished analysis files for our confirmatory study: **375 startup pitches**, with cleaned transcripts. One company (`pilot-108`) was excluded because the available video was for a different company of the same name.

---

## What we measured

For each pitch, an AI counted how many distinct claims (**premises**) the founder made. That count is called **breadth**. We then checked whether breadth predicts whether the startup was **selected** (got through) at Startup Battlefield.

We also have exploratory extras on one of the runs:

- **DFV tags** — is each claim about desirability, feasibility, or viability?
- **Domains** — how those claims group into strategic themes

---

## The two runs to look at

Open these folders on your computer (after cloning or downloading the repo):

### 1. Primary run — GPT-4o-mini  
Folder: `reference/full_n375_k3_v211_gpt4o_mini/`

- Most complete run (claims + DFV tags + domain groupings)
- Best measurement quality of the two models
- **Open these files:**

| File | What it is | Open with |
|------|------------|-----------|
| `aggregated/dataset.csv` | Spreadsheet: one row per pitch, all variables | Excel, Google Sheets, R, Stata |
| `analysis/results.md` | Regression tables (logit models) | Any text editor, or VS Code / Cursor |
| `validation/reliability_report.md` | How consistently the AI agreed with itself across 3 repeats | Same as above |

### 2. Comparison run — Qwen3-32b  
Folder: `reference/full_n375_k3_v211_qwen3_32b/`

- Same 375 pitches and same claim-extraction instructions
- Claims only (no DFV / domains)
- Same three file types as above

---

## Plain-language takeaway (so far)

On these clean full-pitch transcripts:

1. **No clear inverted-U** for total premise count (breadth) predicting selection — neither model finds a significant “sweet spot.”
2. **GPT-4o-mini** is the more reliable coder (more consistent when asked three times).
3. On the GPT-4o-mini run, **feasibility-related claims** show a positive association with selection in exploratory models (treat as exploratory, not confirmatory).

Details and exact coefficients are in each folder’s `analysis/results.md`.

---

## Important columns in `dataset.csv`

You only need a few columns for the main story:

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

## Folders you can ignore

- `reference/v1_3_2_nested/` and `reference/v1_5_1_crossed/` — older published baselines for software tests, **not** this confirmatory sample
- `experiments/` — empty or local-only working files; the shareable results are under `reference/`
- Root `README.md` — how to *run* the AI pipeline if you are coding; not required to read the results

---

## If you want to re-run the stats yourself

Optional. Only needed if you have the toolkit installed. Otherwise just use the CSV and the `results.md` files above.

```powershell
theory-graph analyze --run reference/full_n375_k3_v211_gpt4o_mini
theory-graph analyze --run reference/full_n375_k3_v211_qwen3_32b
```
