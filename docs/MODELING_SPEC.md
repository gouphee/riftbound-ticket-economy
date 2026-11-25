# Modeling specification: historical ticket totals and draws

Updated 2026-11-24 after domain clarification from a competitive participant. This document specifies the *primary research estimands*. It does **not** rewrite the archival data, assert proof of physical ticket collection, or supersede event-specific official payout schedules.

## Distinguish the numbers

For each historical **Friday/Sunday win-based event**, publish at least:

1. **Observed standings-implied tickets** — apply the official event-specific prize table to each player in the final completed standings using their recorded match wins, regardless of `DROPPED` status. This represents the payout implied by observed tournament results, **not** receipts or physical issuance. Only exclude/flag explicit disqualifications when a documented policy and source record justify doing so. The organizer's status labels may not reliably indicate prize eligibility. The user's firsthand experience is that qualifying records generally received their published awards; this is an assumption for reporting, not independently verified for all events.
2. **Theoretical maximum tickets at the observed field size** — optimize over results attainable under a clearly defined tournament format, player count, number of rounds, pairing constraints, byes, and payout table. Define whether draws are disallowed in the reference calculation. If an exact feasible maximum cannot be established, report a **proved upper bound**, and separately a constructed attainable value, not a falsely precise maximum.
3. **Optional capacity-normalized theoretical maximum** — repeat at the *published capacity* and at a common attendance baseline for old/new comparisons. Clearly separate these from the observed-attendance metric.

Also report the payout thresholds' number of earning players, share with 40+ tickets, share earning zero, and tickets per standings entry. Preserve per-row exceptions and distinguish roster-only from standings participants. The missing Atlanta Friday 0-0-0 roster entry does not invalidate the observed-standings sum, but it prevents asserting a complete roster-based observed result.

For historical **Saturday placement-based events**, the **published Top 128 schedule pool is 4,992 tickets** whenever all Top 128 advertised slots are funded, as they are assumed to be in the scenario. All eight observed Saturday standings datasets have at least 128 entries, so their combined **conditional published schedule pool = 39,936 tickets**. This total is independent of who finishes 1st through 8th and independent of whether those players split the Top 8 pool. The top-eight **individual** distribution does depend on finishing order or splitting, so keep (a) official finishing-place allocation and (b) the reported 216-each split scenario separate. Missing cut matches and unexpected statuses are audit flags, *not reasons to suppress the conditional 4,992-ticket schedule pool*. Do not call the pool independently verified physical issuance.

## Treatment of status and missing records

- `DROPPED` alone **does not remove a qualifying recorded result from the primary observed standings-implied calculation**. Retain original status and issue flags in the data, and optionally report an eligibility-conservative sensitivity analysis.
- Do not guess the UVS registration-status enum or what the third status label is. If a source explicitly records disqualification, investigate the documented effect on eligibility separately. Missing final standings rows are **unknown**, not assumed DQ.
- Do not adjust match wins for byes twice. Draws do not count as wins, unless the official event prize rule explicitly specifies another scoring rule. Keep payouts city-specific and per-format.
- Keep the original `reconstructed_event_tickets`/strict gate available, but add a **primary published-results-based total** and a separate `conditional_schedule_pool` field. The former strict six-of-24 count is an archival eligibility-and-evidence certification standard, **not** a count of events with usable tournament results.

## Empirical draw-rate baseline

Calculate from the archived **actual completed matches**, not by averaging per-player draw counts and not by using raw `DROPPED` status:

- Deduplicate match/player relationships by **event, round, match ID**; one drawn match appears for two players.
- Denominator: completed played matches in the applicable Swiss rounds. Exclude explicit byes, ghost matches, non-games, and incomplete/conflicted matches; report excluded counts and coverage.
- Numerator: completed matches explicitly reported as draws. Where distinguishable, break out intentional vs unintentional draws; keep uncertain flags separate. Beware that underlying API records may lack a clear draw flag despite standings showing a draw—reconcile or report this as missing coverage.
- Report draw frequency overall, **by event**, **by Friday/Sunday**, **by Swiss round**, and if supported **by record bracket**. Use match-weighted rates for pooled summaries, not an unweighted mean of event rates.
- Record both match count and empirical draw-rate uncertainty. Preserve format/time-limit differences and use sensitivity analysis rather than assuming a single universal draw probability.
- Use observed draw rates to calibrate Vegas Monte Carlo; validate simulated W/L/D distributions against historical results before predicting time-to-40.

## Maximum versus observed: avoid a common error

The maximum is **not** entrant_count × maximum_personal_prize, because matches generate both wins and losses (and can include byes or draws). Nor is simply setting every record to the minimum prize-winning threshold necessarily achievable under Swiss pairing. Specify if the benchmark is a relaxed mathematical ceiling, an exact format-constrained maximum, or a simulated high outcome. For reproducibility, provide the construction/proof and tests for small player counts and rounds.

When comparing Friday/Sunday against Vegas, present a no-draw benchmark and a draw-calibrated simulation. Do not conflate "theoretical maximum" with the "mean expected payout" or with an event's fixed prize pool.

## Outputs requested for Codex

Implementation and limitations: [Phase 2 historical analysis](PHASE2_HISTORICAL_ANALYSIS.md),
added 2026-11-25. The maximum is reported as a proved win-budget ceiling with
Swiss constraints relaxed, alongside an independently replayable feasible
Swiss example. No exact Swiss maximum or expected draw-free payout is claimed.

- `outputs/tables/historical_ticket_economy.csv`: per-event observed ticket total, theoretical maximum/bound and status, observed N, relevant cap, payouts per entrant, threshold counts, exclusions/unknown records, and source links.
- `outputs/tables/historical_draw_rates.csv`: by event / Swiss round / event format, completed non-bye matches, drawn matches, draw-rate, uncertain/excluded match counts.
- Historical comparison figures (Friday, Sunday, Saturday separately), with observed versus maximum side-by-side for win-based events and fixed 4,992-ticket pool for Saturday.
- Tests checking draw de-duplication, byes, disqualification ambiguity, incomplete final bracket independence, missing standings, changing Friday payout tables, and a brute-force small-case theoretical bound.

Document any changed reporting behavior without deleting the original strict validation and evidence chain. Do not yet claim the 29 tests or new tests were run unless actually executed.
