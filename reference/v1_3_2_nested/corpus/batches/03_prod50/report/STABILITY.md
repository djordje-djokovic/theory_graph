# Machine stability report

Cases: 50 · Runs: 3

## Gate (evaluated on the k-run aggregate actually used in analysis)

| Metric | Value | Target | Pass |
|---|---:|---:|---|
| α breadth, k=3 aggregate | 0.731 | ≥ 0.80 | no |
| Mean ARI vs consensus partition | 0.8493 | ≥ 0.70 | yes |
| Share of cases outside two modal D | 0.04 | ≥ 0.10 | no |

**Overall gate:** FAIL

## Single-run diagnostics (not the analysis object)

| Metric | Value |
|---|---:|
| α breadth, single run | 0.4753 |
| α n_domains (nominal) | 0.0489 |
| α balance | 0.2509 |
| α granularity | 0.4822 |
| α pair judgments (diagnostic) | None |
| Mean pairwise ARI | 0.6936 |
| Mean pairwise Rand (uncorrected) | 0.7468 |
| Share cases with identical D across runs | 0.26 |
| Cases flagged unstable | 15/50 |

## Alignment diagnostics (how readable the ARI is)

| Metric | Value |
|---|---:|
| Mean alignment rate | 0.218 |
| Cases with alignment rate < 0.75 | 50/50 |

A low ARI on a case with a low alignment rate reflects premises that could not be matched across runs, not necessarily a different partition.

## Variance of the aggregated IVs

- Domain-count distribution (median across runs): {'1.0': 1, '2.0': 22, '3.0': 26, '4.0': 1}
- Between-case SD of median breadth: 1.0768

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
