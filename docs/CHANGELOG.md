# Research changes

## 2026-11-25 — Phase 3B draw sensitivity and conditional outcomes

- Added exact point-generating-function dynamic programming for independent
  W/D/L probabilities at four draw rates. The Day 2 gate uses points, including
  qualifying three-win/three-draw records. Nonqualifiers stop after Round 6.
  Full point/ticket PMFs and fractional expected participant counts are exported.
- Reused and hash-verified the existing official Vegas schedule/eleventh-round
  announcement and all eight historical schedules. No payout amounts, source
  captures, eligibility rules or Phase 3A baseline files changed. The stale
  Round 10 prose remains documented; six plus five governs the model.
- Added conditional Round 11 payout and Round 6 qualification/future-EV grids.
  Scores are individually feasible without prior draws; simultaneous Swiss
  pairing feasibility/frequency is not asserted. Equal terminal scores conserve
  combined tickets, but threshold-recipient counts can differ. No agreements,
  concession strategies or permission claims are modeled.
- Added seven CSVs, five SVG/PNG pairs, source review and a hash/recalculation
  audit preserving 750 previous data/code/research artifacts. New execution logs
  are isolated under `outputs/phase3b/`. The general validation report refreshes
  only its current-code inventory. See [the report](PHASE3B_DRAW_SENSITIVITY.md)
  and [project handoff](PROJECT_HANDOFF.md).
- Added an independent multinomial-count oracle and deterministic tests. No
  Monte Carlo, full Swiss simulator, ratings, ODE economics, pooling model or
  video script was added.

## 2026-11-25 — Phase 3A exact Saturday comparison

- Added exact marginal binomial paths for Vegas Standard Rebound with six
  Saturday rounds, a 12-point advancement cut, and five Sunday rounds.
  Nonqualifiers receive no Sunday outcomes. Verified the complete official
  point table against the [Riot schedule](https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/)
  and [eleventh-round announcement](https://x.com/RiotSherman/status/2122889583201591569).
  Retained two stale Round 10 sentences as an explicit source discrepancy.
- Added uniform historical rank-slot probabilities using the unchanged
  archived payout functions; official and 216-each Top 8 allocations conserve
  4,992 tickets. No historical payout amount or eligibility rule changed.
- Added 12 attendance comparisons, full PMFs, stage/path probabilities,
  payout thresholds, marginal concentration measures, and five SVG/PNG pairs.
  Historical 1,024 entrants is hypothetical beyond the advertised cap;
  Barcelona's observed 518 versus published 512 remains a source exception.
- Isolated new evidence in a separate ledger and fingerprinted 615 historical
  files, including all Phase 2 data, reports, witnesses and figures. Phase 2
  integration rebuilds now use disposable outputs so testing new modules does
  not overwrite the archived all-code report inventory. The checks themselves
  are retained. See [the Phase 3A report](PHASE3A_SATURDAY_COMPARISON.md).
- No Swiss simulator, draw/skill model, ticket-pooling model or video script
  was implemented. Expected Vegas totals are not tournament maxima or claims.

## 2026-11-25 — Phase 2 historical tickets and draws

- Added primary Friday/Sunday final-record sums including qualifying dropped
  entries. No event-specific payout amount changed. Rules are parsed from the
  same preserved official [city schedules](SOURCES.md); amounts and tier
  boundaries remain independently tested. Byes are already credited in the
  final record and receive no second award.
- Added the conditional 4,992-ticket funded Top 128 pool for every Saturday,
  irrespective of missing cut results. Individual unresolved finishes and
  the ticket-conserving 216-each split scenario remain separate.
- Preserved raw objects, source timestamps/hashes, the original strict CSVs,
  conservative eligibility fields, and pilot baseline. Added a fingerprint
  audit of 610 pre-existing archival/legacy artifacts.
- Added a proved no-draw win-budget upper bound and separately constructed,
  replayed, no-rematch Swiss witnesses at recorded field size. The exact
  Swiss-constrained maximum is explicitly unknown. No Vegas forecast or Monte
  Carlo simulation is implemented.
- Added unique-match Swiss draw rates, explicit non-game/bye exclusions,
  source-marked draw subtypes, Wilson intervals with qualifications, record
  brackets where supported, and draw-credit reconciliation.
- Added source-linked comparison tables and six standalone PNG/SVG figure pairs.
  [The method and findings](PHASE2_HISTORICAL_ANALYSIS.md) document denominators,
  exceptions, and assumptions. Actual command results are stored separately;
  an archived success report alone is not treated as a fresh test run.
