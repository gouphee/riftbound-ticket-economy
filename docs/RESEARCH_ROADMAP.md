# Research roadmap

The research proceeds in auditable stages. Historical observations, counterfactual calculations, and behavioral simulations must remain separate data products.

## Stage 0 — collection infrastructure (implemented, not fully independently audited)

- 24 historical events, 20,651 standings rows, 20,652 roster rows, with source URLs and archived retrieval hashes.
- Payout functions, pilot checks, offline rebuilds and a reported passing validation report.
- Six events passed a **stricter full-evidence/eligibility reconstruction gate**. The other 18 events remain useful for standings-implied totals and conditional published Saturday prize pools; see `MODELING_SPEC.md`.
- Initial repository audit: `docs/AUDIT_2026-11-24.md`.

**Exit criterion:** source-to-export checks validated, errors tracked, reported test suite independently run by an execution environment. Don't represent archived validation output as a fresh test run.

## Stage 1 — usable historical totals and uncertainty (implemented with labeled bounds)

**2026-11-25 implementation:** the task called Phase 2 now supplies additive
historical outputs, draw rates, proof certificates, feasible no-draw Swiss
constructions, and figures. See [the implementation report](PHASE2_HISTORICAL_ANALYSIS.md).
Exact Swiss maxima remain unresolved; labeled proved relaxed ceilings are used.
Command results are recorded in `historical_execution_validation.json` after
execution. This does not start the following Vegas comparison/simulation stages.

- For Friday and Sunday publish **two primary numbers** per event: (a) observed standings-implied prize allocation including qualifying `DROPPED` records, and (b) a theoretically feasible maximum at the observed attendance, or a labeled proved upper bound if feasibility cannot be established. Optional capacity-normalized results are secondary. For Saturday use the conditional published **4,992-ticket Top 128 pool** as the primary fixed-schedule comparison, independent of Top 8 bracket completion. See `MODELING_SPEC.md`.
- Derive empirical **draw rates by event, format and Swiss round**, deduplicating match/player relationships and excluding byes and incomplete matches. Include match coverage and uncertainty; use these rates to calibrate Vegas simulations.
- Preserve anomalies from `docs/KNOWN_GAPS.md` as provenance and uncertainty flags. `DROPPED` does not disqualify a qualifying result from the primary standings-implied figure, and missing Saturday bracket winners do not affect the fixed Top 128 schedule total. Still investigate Hartford Friday's missing match observation, Atlanta Friday's roster-only row, Singapore Friday's extra empty round, and explicit disqualifications where documented.
- Distinguish exact reconstructions from partial totals; never call either actual physical issuance.
- Add source-driven tests for each corrected assumption and record a before/after audit.
- Prepare three historical views: Friday and Sunday **observed tickets versus theoretical maximum/bound** and draw rates; Saturday **fixed published prize pool and participant-normalized ticket availability**. Keep audit qualifications visible.

**Exit criterion:** 24 events have clearly labeled numerical outputs and confidence/status fields suitable for interpretation, even if some remain unresolved.

## Stage 2 — controlled old/new event comparisons

**2026-11-25 Phase 3A:** the [Saturday analytical comparison](PHASE3A_SATURDAY_COMPARISON.md)
implements the historical placement pool versus updated 11-round Vegas Rebound
with exact equal-skill probabilities, a correctly ordered Day 2 gate, common
attendance scenarios and separate published-cap comparisons. This completes
only the initial Saturday no-draw benchmark. Phase 3B below adds independent
draw sensitivities; other formats, individual weekend/time models, and
simulations remain future stages.

**2026-11-25 Phase 3B:** [exact draw sensitivity](PHASE3B_DRAW_SENSITIVITY.md)
adds 0%, 1%, 2% and 5% independent W/D/L scenarios, preserving the six-round
qualification gate before Sunday's five rounds. It also tabulates conditional
Round 11 ticket outcomes and Round 6 qualification/future ticket expectations
for individually feasible no-prior-draw scores. This is not a strategic-choice
model, joint Swiss tournament, or calibration from historical Round 7 draws.
The no-draw result reproduces Phase 3A; previous artifacts remain unchanged.
Next resolve any desired state-dependent draw sensitivity and finite-field
pairing/bye assumptions, then source the remaining like-for-like event
comparisons before weekend opportunity/time analysis. See
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) for context and boundaries.

- Old Saturday 4,992-ticket published Top 128 pool versus the Vegas two-day Standard Rebound **using both published full caps and equal-entrant scenarios**, with draws excluded in the first benchmark. Distinguish mathematical upper bounds from one no-draw tournament distribution.
- Friday Pre-Regional and six-round Sunday Rebound versus Vegas Sunday five-round Challenge; don't conflate event-day labels.
- Compare ticket totals, per-entrant tickets, share attaining 40+, share earning zero, and payout concentration, not only maxima.
- Historical competitive/casual ODE and Nexus Night payout/time comparisons, with published duration and realistic throughput sensitivity; TFT Vegas-only sidebar.
- Document any event overlap and attendee duplication; do not sum participation counts to estimate distinct attendees.

**Exit criterion:** cross-event figures accompanied by source/payout-table links and identical-attendance normalization.

## Stage 3 — individual time-to-metal model

- Simulate real weekend constraints: scheduled starts/ends, conflicts, check-in windows, ODE queue times and 45/60/90/135-minute completion scenarios.
- Model varied match skill and strength of field, draws (calibrated against deduplicated historical completed matches), tournament participation constraints and budget sensitivity; state whether 60% match win rate is a hypothetical baseline. Do not use the raw UVS `DROPPED` flag as automatic prize ineligibility.
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
