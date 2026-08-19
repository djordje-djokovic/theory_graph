# Survival dependent variable for Startup Battlefield

This folder contains the survival and funding outcome variables for the Startup Battlefield corpus, ready to be joined to `../cases.csv` by `case_id` / `name` / `event` for later regression analysis (including the breadth/modularity Cox model).

**Files:**

- `survival_dv.csv` — one row per firm-event, with both theory_graph `case_id` and the original attractiveness `name`/`event` keys.
- `survival_panel.csv` — person-year panel for the primary discrete-time cloglog estimator, carrying `case_id` and `firm_id` so it joins directly to `../cases.csv`.
- `diagnostics/` — match logs, conflict flags, scan results, and the recorded data vintages.

**How the two files relate.** Both are produced from the same exit table in a single pipeline run, and the panel is expanded *after* the join to `cases.csv`, so it inherits `case_id`. `survival_panel.csv` is therefore a row-per-year expansion of `survival_dv.csv`, not an independently derived file: every firm-event in one appears in the other, and the panel's failure indicators sum to the DV's failure count. `toolkit/survival_dv/audit.py` asserts this.

**Analysis sample.** The pipeline covers all 1,300 Battlefield firm-events, but `cases.csv` is a 376-case corpus and all 376 match. Within that analysis sample there are **73 failures, 77 acquisitions, 4 IPOs and 222 censored** firms, across 2,639 person-years (7.0 years observed per case on average). 12 of the 73 failures are undated. Run `toolkit/survival_dv/coverage.py` for the current breakdown. Note that `cases.csv` covariates such as `BMI` are not copied into the DV; join them yourself on `case_id`.

**Source data:** raw labels and website URLs come from the adjacent `attractiveness` repo (`C:/Projects/uni/sources/attractiveness/startup_battlefield/`). The pipeline reads from there and writes the derived DV here.

---

## 1. Design principles

- **TechCrunch is the unconditional exit-type authority.** A dead domain cannot distinguish *acquired* from *failed* and cannot distinguish a *rebrand* from a *death*, so the website classifier is never allowed to flip a TechCrunch label.
- **Crunchbase is the preferred date source** where it has a clean date.
- **Wayback Machine is the residual date source** for the rest.
- **Time origin is the Battlefield pitch**, not the founding date. Founding age is a covariate (`age_at_pitch_years`), not the clock.
- **Death dates are intervals**, not points. Every failure carries `time_lower_years` and `time_upper_years`; `time_years_midpoint` is provided only for the Cox robustness specification.
- **A known failure with an unknown date is bounded, never deleted or recoded as censored.** Both of those choices bias the estimated hazard downward.
- **No horizon dummies.** Durations and the panel carry strictly more information than 1y/5y dummies, and five dummies invite reporting the one that reaches significance.
- **Funding is a separate outcome family**, not a survival proxy.
- **The pitch is the unit of observation.** Three firms pitched twice; both pitches are retained and `firm_id` is provided so standard errors can be clustered by firm.

### Data vintages

Survival and funding are observed through **different** dates, because they come from different sources:

| Quantity | Source | Observed through | Constant |
|---|---|---|---|
| Exit type, survival censoring | TechCrunch re-scrape, Wayback scan | 2026-08-18 | `ANALYSIS_END_DATE` |
| Funding rounds, funding censoring | Crunchbase dump | 2024-04-10 | `CB_DUMP_DATE` |

Censoring funding at the survival date would silently record about 2.4 years of "no funding raised" that were never observed, so funding exposure is capped at the Crunchbase vintage. Both dates are recorded in `diagnostics/`.

---

## 2. Algorithm for exit type

For every firm:

1. **Normalize the raw `status` column.** The source file contains both `Open` and `open`; we lowercase on load. A bare `== 'open'` filter would silently drop one firm.
2. **Use the TechCrunch status as the exit type.**
   - `open` → `censored`
   - `ipo` → `ipo`
   - `acquired` → `acquired`
   - `closed` → `failure`
3. **Website sanity check.** Reject or flag domains that are known aggregators or that already point at another company (e.g., `crunchbase.com` for Wisebatt, `alida.com` for Pressly). These do not affect the exit type but are logged in `diagnostics/`.
4. **Crunchbase cross-validation.** If TechCrunch says `open` but Crunchbase has a dated `acquired_on`, flag `tc_cb_conflict = 1` and log the case; do not auto-recode until the fresh TechCrunch re-scrape is available.

---

## 3. Algorithm for exit dates

### 3.1 Time origin

The time origin is the month of the Battlefield pitch, not January 1 of the event year. A 45-row lookup table maps each `event` string to a `(year, month)` pair. Six event names carry no year in the string and were verified against TechCrunch/contemporaneous press:

| Event | Date used |
|---|---|
| `TechCrunch 40` | 2007-09 |
| `Hardware Battlefield` | 2014-01 |
| `TechCrunch Startup Battlefield Africa` | 2017-10 |
| `Startup Battlefield Australia` | 2017-11 |
| `Startup Battlefield Latin America` | 2018-11 |
| `TC Hardware Battlefield at TC Shenzhen` | 2019-11 |

The remaining 39 events derive a month from family conventions (SF = September, NY = May, Berlin/London = December, etc.), with known exceptions hard-coded (e.g., Disrupt SF 2019 and TechCrunch Disrupt 2022 were October).

### 3.2 Acquisitions (207 firms)

A five-step ladder, applied in order:

1. **Crunchbase domain path.** Match our website domain to `organizations.domain`, then join `acquisitions` on `acquiree_uuid`. Use `acquired_on` if available. **132 firms** dated this way.
2. **Crunchbase acquiree-name path.** Normalize our company name and `acquisitions.acquiree_name`; accept a unique match only when `acquirer_name` is a plausible, recognizable company. This recovers firms whose CB acquiree record has a different domain (rebrand, redirect, stale CB domain). **19 firms** dated this way, including `Mint` → Intuit and `Swype` → Nuance.
3. **Wayback redirect detection.** A redirect to a *different* company domain, or the year the site went dark, is a positive acquisition signal. **45 firms** dated this way. Because a site usually goes dark at or after the acquisition, this is a lagged upper bound rather than an exact date, and it is never allowed to overwrite a Crunchbase date.
4. **TechCrunch article search.** TechCrunch labelled the firm acquired, so a dated article usually exists.
5. **Undated fallback.** If no source gives a date, the acquisition is left undated and is censored at `analysis_end_date` while retaining the `acquired` exit type. In the current run, **11 acquisitions** are undated.

`acquired_on` dates that are `YYYY-01-01` are treated as year-stamps, not exact days, and are bracketed to that calendar year.

### 3.3 Failures (264 firms)

1. **Crunchbase `closed_on`.** If a unique CB match has a `closed_on` and no `acquired_on`, use it. **31 firms** in the current CB dump. `YYYY-01-01` dates are treated as year-stamps and bracketed to the year.
2. **Annual Wayback scan.** For the remaining failures, query the Wayback CDX for one status-200 snapshot per calendar year from the pitch onward and classify each snapshot as alive/dead. **183 firms** dated this way.
3. **Undated fallback.** If Wayback gives no usable death year, bound from `max(pitch, last_funding_on, last_alive_year)` to `ANALYSIS_END_DATE`. **50 failures** remain undated: the exit type is still `failure`, but `exit_date` is missing and the firm is bounded rather than dropped.

Two rules make the Wayback dating defensible:

**The death is the first dead year with no live year after it**, not simply the first dead reading. A dead snapshot followed by a later live snapshot is a false positive caused by a transient outage, a fetch error, or a relaunch. Taking the first dead reading naively placed 24 deaths *before* the site was last seen alive, and in some cases before the pitch itself. Where a death year is contradicted by a later live snapshot, the death year is discarded and the firm falls through to the undated branch.

**The point estimate is the end of the year** (`YYYY-12-31`), for both failures and acquisitions, so a death is never placed before a pitch that happened late in the same year.

The interval is what should be used in estimation. `last_alive_year_wb` and `first_dead_year_wb` carry the raw bounds, `time_lower_years` / `time_upper_years` express them relative to the pitch, and `death_interval_days` is the width. Where no snapshot was ever confidently classified as alive, the lower bound falls back to the pitch, because all that is known is that the site was dead *by* the first dead year. Of the 264 failures, **240 are interval-censored**; only the 28 with a Crunchbase day-precision `closed_on` are exact.

---

## 4. Algorithm for the person-year panel

The panel is built from the firm-level exit table:

1. For each firm, expand one row per year from the pitch to the earlier of the exit event or `analysis_end_date`.
2. For a `failure`, the row in which the death interval falls is coded `failed = 1`; all prior rows are `failed = 0` and `at_risk = 1`.
3. For `acquired`/`ipo`/`censored`, the row in which the censoring occurs is coded `censored = 1`, and the firm leaves the risk set after that year.
4. Firms with no usable pitch date are dropped from the panel.

The primary estimator is a discrete-time complementary log-log model on this panel, with standard errors clustered on `firm_id`. Cox with midpoint-imputed dates (`time_years_midpoint`) is a robustness specification. Fine-Gray on the same panel is the required competing-risks robustness check.

For an undated failure the panel places the event in the final year of observation, which is the *latest* possible placement. The `undated_exit` and `interval_censored` flags are carried on every panel row so these observations can be dropped, reweighted, or handled with an interval-censored estimator instead.

---

## 5. Algorithm for the funding DV

Funding is a separate outcome family, not a survival proxy.

1. **Match to the same Crunchbase organization** used for the exit dates.
2. **Keep only equity rounds.** Included: `pre_seed`, `seed`, `angel`, `series_a`–`series_j`, `series_unknown`, `convertible_note`, `corporate_round`, `equity_crowdfunding`, `private_equity`. Excluded: `grant`, `debt_financing`, `non_equity_assistance`, `product_crowdfunding`, `initial_coin_offering`, `secondary_market`, and all `post_ipo_*`.
3. **The pre/post split is keyed on the firm-event, not the firm name**, because three firms pitched at two different events and each pitch has its own clock. Keying on name alone assigns one pitch's round to the other, which produced a negative duration for `Glide` and `Lori Systems`. `audit.py` now asserts that no post-pitch round predates its own pitch.
4. **Primary funding DV:** `time_to_first_post_event_round`, a duration **in years** from the pitch to the next qualifying round, paired with `post_event_round_observed` (1 = observed, 0 = right-censored). This avoids the exposure-time confounding that affects a raw count or dollar sum. Exposure ends at the earliest of `CB_DUMP_DATE` and the firm's own exit, since a firm that has failed or been acquired is no longer at risk of raising; `funding_exposure_years` records that window.
5. **Secondary outcomes.** `first_post_event_round_usd` (amount of that next round), `first_post_event_round_type`, `first_post_event_round_investors`, `post_event_rounds`, `post_event_funding_usd`, and `reached_series_a` (graduation to an institutional round). Counts and sums are exposure-confounded, so they belong in a specification that controls exposure or as robustness rather than as the headline DV.
6. **Covariates (not DVs):** `pre_event_rounds`, `pre_event_rounds_with_amount`, `pre_event_funding_usd`, `last_funding_on`. Unmatched firms stay NA on all funding fields; matched firms with zero rounds are coded as true zeros only for the counts, not for dollar amounts.

### Disclosure is the binding constraint on dollar outcomes

Timing is near-complete; amounts are not. Among analysis-sample firms that actually raised a next round:

| Field | Coverage |
|---|---|
| Timing of the next round | 100% of Crunchbase-matched firms |
| Investor count | 86% |
| Amount of the next round | 80% |
| Max post-pitch valuation | 13% |
| Valuation at the next round | 4% |

Valuation is effectively unusable. Amounts are usable but missing-not-at-random, since less successful rounds disclose less often, which biases a dollar sum downward exactly where the outcome is weakest. This is why timing is the primary DV and `reached_series_a` is the preferred value-adjacent outcome: both are defined for every matched firm and need no disclosure. `pct_amount_disclosed` is carried per firm so the selection can be modelled or reported.

### Pitch-month contamination

The event-date table resolves each pitch to a **month**, so `origin_date` is the first of that month. A round announced later in the pitch month is therefore classified as post-pitch even though it may have closed before the firm actually presented. This affects **58 firms in the full corpus and 24 in the analysis sample**, around 11–13% of observed next rounds, and it inflates any pitch-to-funding effect. `first_round_same_month_as_pitch = 1` flags them; the intended robustness specification re-estimates with those firms excluded. Resolving it properly requires exact pitch days for the 45 events.

---

## 6. Known limitations and data-quality flags

- **The Wayback scan has been run at scale** for all 294 firms needing timing. The incremental results are saved in `diagnostics/wayback_scan_results.csv`, and re-running the full pipeline reuses them.
- **The Wayback scan window ends in 2024**, because it ran while the censoring date was still the old `2024-03-31` placeholder. Survival status through 2026 rests on the fresh TechCrunch statuses, which is sound for exit *type*, but a death occurring in 2025–2026 cannot currently be dated from the archive and lands in the undated bucket. Re-running the scan with the 2026 window would narrow those intervals.
- **Date conflicts.** `date_conflict = 1` flags any firm whose exit date falls before its pitch, and also sets `manual_review = 1`. The current run has **zero** conflicts; the flag is retained so a future data refresh surfaces the problem instead of silently dropping firms from the panel.
- **Duplicate firm names.** Three firms pitched at more than one event: `FLUIX`, `Glide`, and `Lori Systems`. Both pitches are kept, so the 1,300 rows contain 1,297 unique `firm_id` values. Cluster on `firm_id`.
- **Degenerate funding exposure.** A small number of firms have an exit date within days of the pitch, giving a near-zero funding exposure window. They are visible via `funding_exposure_years` and flagged by `interval_censored`.
- **Gold-standard validation.** A sample of archived snapshots is prepared in `diagnostics/gold_standard_sample.csv` for human dual-coding; classifier precision/recall and inter-rater kappa are still pending. This is the one substantive item still outstanding.

### Key columns

| Column | Meaning |
|---|---|
| `exit_type` | `failure`, `acquired`, `ipo`, or `censored`; from TechCrunch |
| `exit_date` | Point estimate of the exit; missing for undated exits |
| `time_lower_years` / `time_upper_years` | Bounds on the failure time in years since the pitch |
| `time_years_midpoint` | Midpoint point-estimate, for the Cox robustness run only |
| `death_interval_days` | Width of the failure interval |
| `interval_censored` | 1 when the failure time is known only to an interval |
| `undated_exit` | 1 when a known failure or acquisition has no date |
| `date_conflict` / `manual_review` | Integrity flags |
| `firm_id` | Clustering key; repeated across a firm's multiple pitches |
| `time_to_first_post_event_round` | Years from pitch to next equity round, censored |
| `post_event_round_observed` | 1 = round observed, 0 = right-censored |
| `funding_exposure_years` | Funding risk window, capped at the Crunchbase vintage |
| `first_post_event_round_usd` | Amount of that next round; missing where undisclosed |
| `first_post_event_round_type` | Crunchbase `investment_type` of that round |
| `post_event_rounds` / `post_event_funding_usd` | Post-pitch count and sum, exposure-confounded |
| `reached_series_a` | 1 if a `series_a`–`series_j` round followed the pitch |
| `first_round_same_month_as_pitch` | 1 if the round may predate the pitch |

---

## 5b. Other feasible performance outcomes

Everything below is available in the loaded Crunchbase schema but is **not currently built**. Listed with the constraint that governs whether it is worth building.

| Candidate outcome | Source | Constraint |
|---|---|---|
| Acquisition price | `acquisitions.price_usd` | Disclosed for a small minority of acquisitions; check before committing |
| IPO proceeds and valuation | `ipos.money_raised_usd`, `valuation_price_usd` | Only 11 IPOs in the corpus, so descriptive at best |
| Total funding raised to date | `organizations.total_funding_usd` | Not pitch-clocked, so it mixes pre- and post-pitch funding |
| Number of rounds to date | `organizations.num_funding_rounds` | Same clocking problem; use the pitch-clocked `post_event_rounds` instead |
| Employee count | `organizations.employee_count` | A current-state band, not a time series, so it cannot be clocked to the pitch |
| Investor quality or prominence | `investments` joined to `investors` | Buildable and pitch-clockable; `investors.investment_count` and `total_funding_usd` give a tier proxy |
| Lead investor identity | `funding_rounds.lead_investor_uuids` | Buildable; supports a "attracted a top-tier lead" indicator |
| Subsequent exits | `organizations.num_exits` | Not clocked, and mostly zero for this population |

The two worth adding if a second outcome is needed are **investor prominence at the next round** and **reaching an institutional lead**, because both are pitch-clockable and neither depends on amount disclosure. Employee count and the `organizations` totals should be avoided as outcomes: they describe the firm as of the dump date rather than a measured interval after the pitch, so they cannot support a causal claim about the pitch.

---

## 7. How to run

```powershell
# Crunchbase-only output (fast, no network scan)
python -m toolkit.survival_dv.main cb_outputs

# Full pipeline. Re-uses the cached Wayback scan results, so this takes about a
# minute; it only re-queries the archive for firms not already in
# diagnostics/wayback_scan_results.csv.
python -m toolkit.survival_dv.main full
```

Verify and inspect:

```powershell
# Integrity checks on the written CSVs; exits non-zero on failure
python -m toolkit.survival_dv.audit

# Coverage for the 376-case analysis sample
python -m toolkit.survival_dv.coverage

# Unit and regression tests
python -m pytest toolkit/survival_dv/tests/test_survival_dv.py -v
```

`audit.py` is the check to run after any data refresh. It verifies that no exit predates its pitch, that every failure carries interval bounds, that censoring respects the survival vintage, that the panel and the DV agree on every firm-event and on the total failure count, and that funding durations exist exactly for Crunchbase-matched firms.
