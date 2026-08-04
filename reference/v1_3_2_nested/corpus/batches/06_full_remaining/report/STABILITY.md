# Machine stability report

Cases: 266 · Runs: 3

## Gate (evaluated on the k-run aggregate actually used in analysis)

| Metric | Value | Target | Pass |
|---|---:|---:|---|
| α breadth, k=3 aggregate | 0.8142 | ≥ 0.80 | yes |
| Mean ARI vs consensus partition | 0.9628 | ≥ 0.70 | yes |
| Share of cases outside two modal D | 0.094 | ≥ 0.10 | no |

**Overall gate:** FAIL

## Single-run diagnostics (not the analysis object)

| Metric | Value |
|---|---:|
| α breadth, single run | 0.5936 |
| α n_domains (nominal) | 0.4409 |
| α balance | 0.5312 |
| α granularity | 0.4832 |
| α pair judgments (diagnostic) | None |
| Mean pairwise ARI | 0.9292 |
| Mean pairwise Rand (uncorrected) | 0.9547 |
| Share cases with identical D across runs | 0.6165 |
| Cases flagged unstable | 12/266 |

## Alignment diagnostics (how readable the ARI is)

| Metric | Value |
|---|---:|
| Mean alignment rate | 0.1604 |
| Cases with alignment rate < 0.75 | 264/266 |

A low ARI on a case with a low alignment rate reflects premises that could not be matched across runs, not necessarily a different partition.

## Variance of the aggregated IVs

- Domain-count distribution (median across runs): {'1.0': 3, '2.0': 44, '3.0': 197, '4.0': 22}
- Between-case SD of median breadth: 0.9894

The measurement plan treats the modularity propositions as untestable if
fewer than 10% of cases fall outside the two modal domain counts.

See `stability_by_case.csv` for per-case vectors.

## Method notes

- Premises aligned across runs by evidence-span similarity (threshold 0.88).
- Pairwise ARI/Rand computed on the shared aligned premise set.
- Consensus partition: majority co-membership over runs, connected components.
- Aggregate reliability from single-run α by Spearman-Brown (k=3).
- Breadth α uses the interval/ratio form of Krippendorff's alpha.
- Pair-level α is a decidability diagnostic, not a gate.
