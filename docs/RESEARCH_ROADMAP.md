# Research roadmap

The research proceeds in auditable stages. Historical observations, counterfactual calculations, and behavioral simulations must remain separate data products.

## Stage 0 — collection infrastructure (implemented, not fully independently audited)

- 24 historical events, 20,651 standings rows, 20,652 roster rows, with source URLs and archived retrieval hashes.
- Payout functions, pilot checks, offline rebuilds and a reported passing validation report.
- Six exact published-entitlement reconstructions; remaining events have documented missing evidence and/or uncertain eligibility.
- Initial repository audit: `docs/AUDIT_2026-11-24.md`.

**Exit criterion:** source-to-export checks validated, errors tracked, reported test suite independently run by an execution environment. Don't represent archived validation output as a fresh test run.

## Stage 1 — usable historical totals and uncertainty (NEXT)

- For each event produce: recorded standings participants, known published-rule tickets, supported-eligibility tickets, unknown payout/eligibility count, conditional published rank-slot pool (Saturday), and a defensible lower/upper bound or unbounded/unknown status.
- Resolve discrepancies from `docs/KNOWN_GAPS.md` where the official archives allow; prioritize Utrecht Sunday (268 drop-eligibility records), Vancouver/Singapore/Los Angeles unfinished Saturday cuts, Hartford Friday match gap, Atlanta Friday roster-only row, and Singapore Friday round mismatch.
- Distinguish exact reconstructions from partial totals; never call either actual physical issuance.
- Add source-driven tests for each corrected assumption and record a before/after audit.
- Prepare three separate historical visualizations: Friday, Saturday, and Sunday **ticket entitlements by event** (with uncertainty annotations).

**Exit criterion:** 24 events have clearly labeled numerical outputs and confidence/status fields suitable for interpretation, even if some remain unresolved.

## Stage 2 — controlled old/new event comparisons

- Old Saturday 4,992-ticket published Top 128 pool versus the Vegas two-day Standard Rebound **using both published full caps and equal-entrant scenarios**, with draws excluded in the first benchmark. Distinguish mathematical upper bounds from one no-draw tournament distribution.
- Friday Pre-Regional and six-round Sunday Rebound versus Vegas Sunday five-round Challenge; don't conflate event-day labels.
- Compare ticket totals, per-entrant tickets, share attaining 40+, share earning zero, and payout concentration, not only maxima.
- Historical competitive/casual ODE and Nexus Night payout/time comparisons, with published duration and realistic throughput sensitivity; TFT Vegas-only sidebar.
- Document any event overlap and attendee duplication; do not sum participation counts to estimate distinct attendees.

**Exit criterion:** cross-event figures accompanied by source/payout-table links and identical-attendance normalization.

## Stage 3 — individual time-to-metal model

- Simulate real weekend constraints: scheduled starts/ends, conflicts, check-in windows, ODE queue times and 45/60/90/135-minute completion scenarios.
- Model varied match skill and strength of field, draws, drops, eligibility and budget sensitivity; state whether 60% match win rate is a hypothetical baseline.
- Output probability of reaching 40 tickets by elapsed time, distribution of tickets per attendee, risk of zero payout, and expected tickets per participant-hour.
- Independently verify exact small-event formulas before running Monte Carlo; reproducible random seeds and convergence checks.

**Exit criterion:** charts make it clear that expected tickets is not the same as probability of acquiring one metal.

## Stage 4 — coordinated ticket aggregation

- Separate: solo players; friends pooling to reach a single redemption; repeat eight-player groups; larger coordinated groups; direct ticket transactions (policy-sensitive); match fixing (separate prohibited-conduct scenario).
- Pooling changes **who controls tickets and wall-clock time to one redemption**, not total tickets created under ordinary honest matches.
- Report participant-hours, group operating costs, badge/redemption constraints, and sensitivity to repeated-pod throughput.
- Do not infer behavior prevalence from isolated photos or anecdotes. Ask how evidence could distinguish honest group play from manipulated results.

**Exit criterion:** scenario results with uncertainty and no blanket accusation about entrants.

## Stage 5 — policy tradeoffs

Compare current rules with documented judge guidance, enforcement on proven collusion, central queue with optional staffed/kiosk registration, random seating, cooldowns, and account-linked tickets or limited gifting. Consider queue utilization, privacy, accessibility without smartphones, ordinary friends' ability to participate, organizer workload, and the potential for badge-based card gifting after redemption.

**Exit criterion:** policy comparison documents both the measured incentive changes and practical downsides.

## Stage 6 — communication and Vegas follow-up

- **Pre-Vegas:** verify final current payout schedules; write a 12–15-minute video and an evidence-rich companion essay. Use title *Why It Just Got Harder to Get a Metal Legend* provisionally.
- **On site:** record publicly observable ODE throughput, wait times and announced policies; interview consenting players and judges. Avoid recording identifying information without permission. Do not characterize repeated participation as wrongdoing alone.
- **Post-Vegas:** add observed attendance, participant-perspective survey limitations and rule enforcement; evaluate predictions, including mistakes.

## Scope discipline

Metal inventory/character resale prices and all-event, TFT-inclusive ticket issuance are secondary. Revisit full convention issuance only if testing an explicit claim covering the entire convention, not merely the revised 2v2 structure. Favor accurate changed-event comparisons over an unsound grand total.

Keep a changelog or PR for each substantive modeling assumption. Figures presented in the video should trace to specific source rows and tested calculations.
