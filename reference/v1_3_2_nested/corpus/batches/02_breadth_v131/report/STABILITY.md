# Machine stability report

Cases: 30 · Runs: 3

## Gate (evaluated on the k-run aggregate actually used in analysis)

| Metric | Value | Target | Pass |
|---|---:|---:|---|
| α breadth, k=3 aggregate | 0.8888 | ≥ 0.80 | yes |
| Mean ARI vs consensus partition | 0.955 | ≥ 0.70 | yes |
| Share of cases outside two modal D | 0.0667 | ≥ 0.10 | no |

**Overall gate:** FAIL

## Single-run diagnostics (not the analysis object)

| Metric | Value |
|---|---:|
| α breadth, single run | 0.7272 |
| α n_domains (nominal) | 0.4681 |
| α balance | 0.4686 |
| α granularity | 0.5453 |
| α pair judgments (diagnostic) | None |
| Mean pairwise ARI | 0.9153 |
| Mean pairwise Rand (uncorrected) | 0.9683 |
| Share cases with identical D across runs | 0.7667 |
| Cases flagged unstable | 2/30 |

## Alignment diagnostics (how readable the ARI is)

| Metric | Value |
|---|---:|
| Mean alignment rate | 0.1787 |
| Cases with alignment rate < 0.75 | 30/30 |

A low ARI on a case with a low alignment rate reflects premises that could not be matched across runs, not necessarily a different partition.

## Variance of the aggregated IVs

- Domain-count distribution (median across runs): {'2.0': 2, '3.0': 25, '4.0': 3}
- Between-case SD of median breadth: 1.129

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
