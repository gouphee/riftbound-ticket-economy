# Phase 2: historical ticket generation and draw rates

Implementation date: 2026-11-25. This is the historical-analysis task called
Phase 2 in the request; it implements the roadmap's usable historical totals
stage. Vegas comparisons, simulations, coordination models, and scripting have
not been started.

## Principal results

| Cohort | Events | Standings entries | Primary tickets | Tickets / entry | Entries earning 40+ | Zero-ticket share | Swiss draws / completed played matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Friday | 8 | 11,571 | 119,587 | 10.3351 | 334 (2.89%) | 53.42% | 344 / 26,805 (1.2833%) |
| Saturday | 8 | 3,165 | 39,936 conditional | 12.6180 conditional | 256 (8.09%) conditional | 67.65% conditional | 554 / 9,142 (6.0599%) |
| Sunday | 8 | 5,915 | 60,556 | 10.2377 | 547 (9.25%) | 68.74% | 252 / 14,315 (1.7604%) |

Friday/Sunday are sums implied by the recorded final match records, **including
qualifying `DROPPED` entries**. Saturday assumes all 128 advertised places were
funded at every event. Saturday's threshold/distribution counts refer to these
conditional rank slots, without assigning unresolved Top 8 finish positions to
players. None of these totals proves physical issuance. The cohort entry counts
are not distinct people across events or distinct convention attendees.

All **17,486 Friday/Sunday** final match records can be priced; all 24 events
have a primary comparison figure. The one Hartford Friday record without match-history support is
explicitly recorded as 0-3-0 and therefore implies zero tickets; it remains
unresolved in the unchanged legacy strict export. No missing record is filled.

The combined Swiss census has **1,150 explicit draws / 50,262 completed played
matches = 2.2880%**. Of 50,626 unique Swiss match records, 130 are explicit byes
and 234 are one-player automatic-loss non-games; these are excluded. No Swiss
records in this archive require exclusion for an unknown result, conflict,
ghost flag, or incomplete status. There are 36 additional cut match records,
which are not part of this Swiss baseline. Subtypes are source-marked: 38
intentional and 1,112 unintentional. These flags do not establish player intent
beyond the recorded classification.

The descriptive independent-match 95% Wilson interval for the pooled rate is
**2.1609%–2.4224%**. The historical fraction is a census calculation, not an
estimate requiring sampling error. The interval is a working binomial model for
comparison; repeated players and rounds are correlated, and the interval is
not cluster adjusted. Differences between event cohorts do not identify causal
effects of format, skill, time limit, or participant incentives.

## Observed field size and denominators

`observed_n` is the number of final standings entries, the conventional recorded
field-size proxy. It includes zero-match entries and does not assert physical
attendance. No published cap is used as attendance. The CSV separately reports
roster entries, match-evidenced participants, and tickets divided by each
applicable denominator. It also gives the upper-bound sensitivity at the
match-evidenced N. Across cohorts, 20,628 event entries have match evidence,
versus 20,651 standings entries and 20,652 roster entries.

Saturday illustrates the denominator's importance: the same **4,992 tickets**
means **37.82 tickets per standings entry in Sydney (N=132)** and **9.64 in
Barcelona (N=518)**. Missing cut results cannot change the conditional pool.
The Top 8 official pool is 1,728; redistributing it as 216 each generates no
additional tickets. The split is not verified for any particular scoped event.

## What changed from the strict reconstruction

Published payout amounts have not changed. Phase 2 adds a new reporting basis;
the existing `event_summary.csv`, individual conservative eligibility fields,
strict gates, raw captures, and pilot references are retained.

- Friday's primary sum is **119,587**; its conservative supported-eligibility
  known subtotal is **119,437**, a 150-ticket difference.
- Sunday's primary sum is **60,556**; the conservative known subtotal is
  **50,636**, a 9,920-ticket difference. Utrecht accounts for 8,840 of that
  difference: 268 qualifying dropped records contribute to its 10,920-ticket
  primary total; the conservative supported known subtotal is 2,080.
- Saturday's conditional funded pool is **39,936**. The preserved strict
  individual-placement known subtotal is 33,744 and the conservative supported
  known subtotal is 33,600. Missing Top 8 allocations explain why these answer
  different questions; neither subtotal changes the funded-pool assumption.

`DROPPED` and the source's actual `ELIMINATED` label are not converted into
disqualification. No explicit disqualification status occurs in these archived
standings. That does not prove there were no disqualifications outside the
available data. `data/phase2_disqualification_reviews.json` is an empty review
register. A future exclusion must reference archived record evidence and a
historical policy interpretation; ambiguous status alone does not authorize it.

## No-draw feasible construction and proved ceiling

**The exact Swiss-constrained maximum is unresolved for every Friday/Sunday
event.** Two different, labeled numbers are provided:

1. A constructed attainable value under the explicit reference pairing policy.
   All N standings entries remain enrolled for R published rounds, every
   two-player match is decisive, opponents never repeat, and an odd field has
   one lowest-eligible bye each round, without repeated byes. Pairing processes
   descending win-score groups, with single-player downfloats when necessary.
   A floater may pass another group if rematch constraints require it. The
   lower synthetic integer ID wins; this is a deterministic example, not a
   skill model, an expected payout, or optimization. Every pairing and pre-match
   score is retained and independently replayed for identity coverage, unique
   opponents, bye eligibility, win conservation, and payout arithmetic.
2. A proved upper bound that relaxes Swiss/opponent and integer-count constraints.
   It is valid for any Swiss outcome under the full-participation, fixed-field,
   no-draw reference. It is **not** asserted to be attainable or tight under the
   organizer's pairing algorithm.

The construction respects a clearly defined Swiss policy, while the ceiling
deliberately permits more final win distributions. This avoids presenting one
binomial-looking no-draw distribution as a maximum, or giving everyone the
maximum personal award. The legal organizer pairing/tiebreak implementation has
not been recovered, so an exact maximum under that implementation is not claimed.

### Upper-bound proof

Let `n_w` count players finishing with `w` credited wins, and `p(w)` be the
event-specific published ticket table (unlisted valid wins pay zero). With a
fixed field, full participation and no draws, each round supplies `floor(N/2)`
played-match wins and `N mod 2` bye wins. Therefore:

```text
sum(n_w) = N
sum(w * n_w) = W = R * ceil(N/2)
ticket total = sum(p(w) * n_w)
0 <= w <= R
```

Every feasible Swiss tournament satisfies these equations. Relax `n_w` to
nonnegative real numbers and remove opponent/score-group restrictions. A vertex
of this two-equality linear program uses at most two win levels. The code
enumerates all such pairs using exact rational arithmetic and retains a
fractional-count proof certificate. The relaxed optimum upper-bounds every
legal Swiss result. Because an actual ticket total is a multiple of the payout
GCD, rounding the relaxed optimum down to that multiple preserves the bound.
Fractional certificate counts are never written into observed standings.

| Cohort | Observed tickets | Constructed no-draw total | Sum of proved relaxed ceilings |
| --- | ---: | ---: | ---: |
| Friday | 119,587 | 124,519 | 275,880 |
| Sunday | 60,556 | 66,452 | 141,998 |

The wide construction-to-ceiling gap is real uncertainty about the maximum.
Do not call the ceiling expected generation, interpret observed/ceiling ratios
as efficiency, or attribute differences from either benchmark solely to draws.
Drops, participation, pairing, floats, and observed results also differ from
the full-participation reference. The strict no-repeat reference also limits R
to the available opponents/one-time bye slots; impossible small-field requests
are rejected. Tests brute-force all outcomes and nonrepeating pairings for small
cases independently of the analytic relaxation.

Witnesses and certificates live in `outputs/phase2/constructions/*.json.gz`,
with event keys, table values, and source links. They are counterfactual
artifacts, never additions to `data/raw/` or the historical standings.

## Draw-rate accounting and remaining exceptions

- Deduplication key: event key + round ID + match ID. Player relationships are
  not counted as separate matches. Conflicting duplicates would be excluded.
- Denominator: completed two-person Swiss records with an explicit winner or
  explicit draw flag, excluding byes, ghosts, non-games, incomplete/conflicted
  records, unsupported match types, and unknown results. A missing winner alone
  is not a draw. A zero denominator yields a blank rate.
- Results are pooled by summing matches and draws, not averaging event rates.
  Event, Friday/Saturday/Sunday cohort, Swiss round, cohort-round and event-round
  rows are retained. All events are 1v1 Constructed best-of-three; “event format”
  denotes the three named event cohorts, not a different gameplay ruleset.
- Pre-match record brackets are supplied only where full match history replays
  to the final record and starts in Round 1. Other histories have an explicit
  unknown bracket; no record is imputed.
- **Utrecht Saturday:** six final-record draw credits are not explained by
  explicit match results; three quarterfinal records have no resolved result.
  These remain missing cut coverage, without turning them into Swiss draws.
- **Singapore Friday:** the published five-round table governs payouts. The
  extra completed Round 6 has no matches, so its rate is blank. Atlanta is the
  only Friday event contributing played matches to the pooled Round 6 rate.
- **Atlanta Friday:** one roster-only row remains absent from final standings;
  the observed-standings sum is usable without asserting a complete roster-based
  total. No DQ or 0-0-0 final standing is invented for that registration.
- **Hartford Friday:** the archived 0-3-0 without match observations prices to
  zero in the primary record calculation and remains flagged in the legacy audit.
- Published caps, metadata caps and round-time statements sometimes disagree.
  Both schedule/metadata time limits and old warning fields are retained; this
  analysis does not infer a causal effect of those differences.
- Actual ticket claims, drop timing, later sanctions, event-specific prize
  splits, and physical play versus recorded concessions remain unverified.

## Files and reproducibility

| New artifact | Contents |
| --- | --- |
| `outputs/tables/historical_ticket_economy.csv` | All 24 primary totals, field sizes, thresholds, sensitivities, bounds, sources |
| `outputs/tables/historical_cohort_summary.csv` | Weighted cohort totals and rates |
| `outputs/tables/historical_individual_awards.csv` | 20,651 original-status rows and primary/legacy/scenario fields |
| `outputs/tables/historical_award_distribution.csv` | Individual award bins, with Saturday assumptions explicit |
| `outputs/tables/historical_unique_matches.csv` | Unique matches, classification, exclusions, source pointers, bracket support |
| `outputs/tables/historical_draw_rates.csv` | Match-weighted rates, exclusion counts, coverage and Wilson intervals |
| `outputs/tables/historical_draw_rates_by_record.csv` | Supported pre-match record bracket rates plus unknown brackets |
| `outputs/tables/historical_draw_reconciliation.csv` | Final-record draw credits versus explicit match credits |
| `outputs/tables/historical_phase2_report.json` | Numerical summaries and input/code hashes |
| `outputs/tables/historical_phase2_validation.json` | Phase 2 accounting, proof, and preservation audit |
| `outputs/tables/historical_figure_manifest.json` | Figure input hashes and renderer version |
| `outputs/figures/historical_*.svg` and `.png` | Six standalone vector/raster figure pairs |

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.cli phase2
PYTHONPATH=src python3.12 -m riftbound_tickets.cli audit-phase2
```

Core calculations and all tests use only the standard library and the archive.
Phase 2 does not fetch sources. Figures use the separately pinned optional
environment:

```sh
uv venv .venv-figures --python python3.12
uv pip install --python .venv-figures/bin/python -r requirements-figures.txt
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.cli phase2-figures
```

`data/phase2_legacy_fingerprints.json` records before-change byte hashes for
610 existing archival/legacy artifacts, including original raw objects and
conservative CSVs. Fresh validation reports may be regenerated; original data
and CSVs must remain identical. Actual command execution results are recorded
separately in `outputs/tables/historical_execution_validation.json` after the
required suite runs. Do not infer a fresh test run from an old report.
