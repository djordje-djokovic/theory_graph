# Reliability report

Experiment: `full_n375_k3_v211_qwen3_32b`
Cases: 375 | Premises runs (k): 3 | Domains runs (k): 1

This file is produced automatically when you run **`theory-graph measure`**.
It summarizes **within-model** agreement: how consistently the same AI model
codes the same pitch when run multiple times on the same prompt.

---

## Quick glossary

| Term | Plain English |
|---|---|
| **Breadth** | How many premises (claims) the model extracts from a pitch (Pass A). |
| **Modularity** | How the model groups those premises into strategic domains (Pass C). |
| **Krippendorff's α** | Agreement on a *number* across runs (e.g. premise count or domain count). 1.0 = perfect; ≥0.80 good; 0.67–0.80 tentative; <0.67 weak. Computed from all k runs, and it reports how reliable a *single* run would be as a measure. |
| **Spearman-Brown** | Converts that into the reliability of an *aggregate* of k runs — which is what the analysis actually uses, since `breadth` is the median of the runs. |
| **Content alignment** | Do the *wordings* of premises match across runs? (Needed because each run labels claims P1, P2… independently.) |
| **ARI (Adjusted Rand Index)** | Do runs put the *same premises in the same domain groups*? 1.0 = identical grouping; 0 = chance. |
| **Validation %** | Share of JSON files that pass schema checks (not agreement — one run per file). |

---

## Summary

| What | Metric | Value | Interpretation |
|---|---|---|---|
| Breadth: agree on **count**? | Krippendorff α (ratio), one run as the measure | 0.568 | below tentative (<0.67) |
| Breadth: how far apart are the counts? | Mean absolute difference | 1.273 | Premises, on average, between any two runs of the same pitch. |
| Breadth: reliability of the **analysed** variable | Aggregate α, median of 3 | 0.798 | tentative (0.67–0.80) |
| Breadth: agree on **wording**? | Content match share (≥0.35) | 0.447 | Higher is better; ~1.0 means runs extract the same claims. |
| Modularity: agree on **domain count**? | Krippendorff α (n_domains) | n/a | not computed (need k≥2 runs with data) |
| Modularity: agree on **grouping**? | Mean pairwise ARI | n/a | ≥0.80 strong; 0.50–0.80 moderate; <0.50 weak. |

### Validation (schema compliance, not agreement)

- **premises**: 20% valid (1125 files, avg 2.7 errors/file)

---

## Pass A — Premises (breadth)

**Question:** When we ask the model three times to list the main claims in a pitch,
does it find the same number of claims and roughly the same content?

- Krippendorff α on premise count, **ratio** level: **0.568** (375/375 cases with all 3 runs)
- Mean absolute difference in premise count between runs: **1.273**
- Mean content-match share: **0.447**
- Per-case detail: `validation/reliability_premises_per_case.csv`

### Reliability of the measure actually analysed

`aggregated/dataset.csv` records `breadth` as the **median of the 3 runs**, not a single run, so the figures above are the reliability of one run and understate the reliability of the analysed variable. Per-case dispersion is kept in `breadth_run_sd`, which is the column to filter on when selecting cases for human adjudication.

Both rows below are estimated from **all 3 runs**; α cannot be computed from one run. What differs is how many runs make up the measure being evaluated, not how much data the estimate uses. This is the usual distinction between the reliability of one rater and the reliability of an average of several: α answers the first by construction, Spearman-Brown extrapolates to the second.

| Measure being evaluated | α (ratio) | α (interval) | Reading |
|---|---|---|---|
| One run, if it were used alone | 0.568 | 0.567 | Conservative floor; not what is analysed. |
| Median of 3 runs — **the analysed variable** | **0.798** | 0.797 | tentative (0.67–0.80) at ratio, tentative (0.67–0.80) at interval. |

Ceiling on an observed correlation given this reliability: **0.893** — divide an observed correlation by it for the disattenuated bound.

Spearman-Brown is exact for the mean of k and the pipeline uses the median, so for k=3 the aggregate figures are close approximations and should be read as upper bounds — the median of three is slightly noisier than their mean. Median is retained deliberately, because it is what prevents one runaway run from moving a case.

Because measurement error in an independent variable biases coefficients toward zero, breadth effects estimated from this data are attenuated rather than inflated: an observed association is a lower bound on the true one, while a null result is weaker evidence of absence than it would be under perfect measurement. Report the aggregate reliability alongside any breadth coefficient. Note also that this addresses random error only — systematic over- or under-splitting is shared across runs of the same model and survives aggregation, which is what human–model agreement is needed to detect.

Breadth is a count with a true zero, so α is computed at **ratio** level per
`prompts/registry.md` § Agreement protocol. Because α on a count is sensitive to
between-case range restriction, the mean absolute difference is reported alongside it,
and the interval-level figure is disclosed as a sensitivity check:
α (interval) = **0.567**.

## Pass C — Domains (modularity)

**Question:** Given the *same* frozen premise list, does the model group premises
into the same strategic domains across repeated runs?

- Cases with all 1 domain runs: **0/375**
- Krippendorff α on domain count (n_domains): **n/a**
- Mean pairwise ARI on grouping: **n/a**
- Per-case detail: `validation/reliability_domains_per_case.csv`

## What this report does *not* include

- **Human–model agreement** (compare model to human-coded gold standard).
- **Within-human agreement** (two human coders on the same pitch).
- **DFV tag agreement** (Pass B); run k≥3 on `dfv` separately if needed.

See `prompts/registry.md` § Agreement protocol for the full reliability design.
