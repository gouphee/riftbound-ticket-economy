# Authoritative video claim index

Research handoff dated 2026-11-26. This is an evidence index, not narration or a replacement script. The machine-readable authority is [phase6_claims.csv](../outputs/tables/phase6_claims.csv), including exact evidence cells and selectors. Supported means supported within the written scope; conditional and anecdotal claims require their qualification. Unresolved/contradicted rows are **not assertions for production**.

The first eight sequences already have narration in a separate project. Use the correction notes below to check it; no narration was imported, reviewed line by line or replaced here.

## S01

### S01-01 — conditional

The working title is defensible for the changed Saturday competitive route, not as a measured whole-weekend decline.

**Evidence:** editorial_scope_synthesis. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Scope the hook and conclusion to the demonstrated route.
**On screen:** Scope the hook and conclusion to the demonstrated route.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** docs/RESEARCH_BRIEF.md; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Check the existing hook; no narration was inspected or rewritten.

### S01-02 — supported

Advertised Plated Legend catalog entries cost 40 tickets.

**Evidence:** official_catalog. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Tickets do not guarantee stock, eligibility or successful redemption.
**On screen:** Tickets do not guarantee stock, eligibility or successful redemption.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S01-03 — unresolved

The number and identity of metals shown in the owner’s collection are verified here.

**Evidence:** outside_research_scope. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Owner footage and collection facts were not examined in this repository.
**On screen:** Owner footage and collection facts were not examined in this repository.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** owner footage in separate production project; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** DO_NOT_ASSERT. Do not supply an invented collection count.

## S02

### S02-01 — supported

All eight historical Saturday events advertised seven Swiss rounds followed by Top 8.

**Evidence:** official_historical_schedules. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** 5–1 and 6–0 are checkpoints before Round 7.
**On screen:** 5–1 and 6–0 are checkpoints before Round 7.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** data/phase3a/sources.csv;outputs/tables/conditional_historical_checkpoint_rows.csv; machine-readable cells preferred.
**Official source:** https://uvsgames.com/rq-atlanta-schedule/; see data/phase3a/sources.csv for all eight.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S02-02 — conditional

The historical 512-cap Saturday schedule funded 4,992 tickets, 128 positive slots and 32 slots paying at least 40.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Conditional on all advertised prizes being funded; not verified issuance.
**On screen:** Conditional on all advertised prizes being funded; not verified issuance.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv;outputs/tables/saturday_payout_thresholds.csv; machine-readable cells preferred.
**Official source:** https://uvsgames.com/rq-atlanta-schedule/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S02-03 — conditional

The published individual maximum was 432 tickets; the Top 8 pool was 1,728.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** A Swiss seed is not a completed cut placement.
**On screen:** A Swiss seed is not a completed cut placement.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S03

### S03-01 — supported

Vegas Rebound is six Saturday rounds, a 12-point continuation gate and five Sunday rounds, with no elimination cut.

**Evidence:** official_published_format. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Use eleven rounds; retain stale Round 10 prose as a documented source inconsistency.
**On screen:** Use eleven rounds; retain stale Round 10 prose as a documented source inconsistency.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv;data/phase3a/vegas_rules.json; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S03-02 — supported

Vegas Rebound advertises 1,024 seats, including 256 held for RC competitors.

**Evidence:** official_schedule. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Cap and reserved seats are not observed entries.
**On screen:** Cap and reserved seats are not observed entries.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S03-03 — conditional

Vegas’s published maximum is 80 tickets; the baseline zero-ticket probability is 79.1504%.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Equal-skill independent marginal model, no draws, byes or drops; 80 is the schedule ceiling.
**On screen:** Equal-skill independent marginal model, no draws, byes or drops; 80 is the schedule ceiling.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S04

### S04-01 — conditional

The full-cap comparison is 32 historical 40+ slots versus 33.5 expected Vegas 40+ recipients.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Different capacities: 512 versus 1,024; the Vegas count is an expectation, not actual metals.
**On screen:** Different capacities: 512 versus 1,024; the Vegas count is an expectation, not actual metals.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; outputs/figures/saturday_analytical_chance_40.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S04-02 — conditional

At matched N=512, individual 40+ probability falls from 6.25% to 3.2715%.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Analytical equal-skill/no-draw comparison; historical funded rank slots, Vegas marginal outcomes.
**On screen:** Analytical equal-skill/no-draw comparison; historical funded rank slots, Vegas marginal outcomes.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S05

### S05-01 — conditional

At matched 512 entrants, mean tickets per entrant fall from 9.75 to 5.6592.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** Means are not a person’s chance of a metal.
**On screen:** Means are not a person’s chance of a metal.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S05-02 — conditional

At their different full caps, Vegas generates 5,795 expected tickets versus the old 4,992-ticket funded pool.

**Evidence:** exact_model. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** 1,024 versus 512 capacity; Vegas total is expected, not a feasible maximum or observed issuance.
**On screen:** 1,024 versus 512 capacity; Vegas total is expected, not a feasible maximum or observed issuance.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv; outputs/figures/saturday_analytical_expected_tickets.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S05-03 — unresolved

Actual physical ticket issuance and successful Metal Legend redemption have been established.

**Evidence:** explicit_evidence_gap. Reports: [PHASE3A_SATURDAY_COMPARISON.md](PHASE3A_SATURDAY_COMPARISON.md).
**Spoken qualification:** No claim ledger or redemption/inventory evidence was recovered.
**On screen:** No claim ledger or redemption/inventory evidence was recovered.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** docs/KNOWN_GAPS.md; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** DO_NOT_ASSERT. Describe entitlements, models and potential units instead.

## S06

### S06-01 — conditional

At p=50%, exact 5–1 after six rounds is 9.375%; exact 8–2 after ten is 4.3945%.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Exact records, independent no-draw matches, and checkpoints before the final Swiss round.
**On screen:** Exact records, independent no-draw matches, and checkpoints before the final Swiss round.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_record_probabilities.csv; outputs/figures/conditional_record_difficulty.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S06-02 — conditional

At p=50%, 5–1 or better is 10.9375%; 8–2 or better is 5.46875%.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Cumulative probabilities differ from the exact-record calculation.
**On screen:** Cumulative probabilities differ from the exact-record calculation.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_record_probabilities.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S06-03 — conditional

At p=50%, 6–0 has probability 1.5625%, versus 0.09765625% for 10–0.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Perfect checkpoint runs, not completed-event results.
**On screen:** Perfect checkpoint runs, not completed-event results.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_record_probabilities.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S06-04 — conditional

At p=80%, the cumulative comparison reverses: 65.536% historical versus 67.779953% Vegas.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Do not say every strong-record comparison is harder at every skill assumption.
**On screen:** Do not say every strong-record comparison is harder at every skill assumption.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_record_probabilities.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S06-05 — contradicted

Vegas cumulative 8–2-or-better is less likely at every p from 40% to 80%.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Contradicted at p=80%; exact 8–2 and perfect 10–0 comparisons remain ordered in this range.
**On screen:** Contradicted at p=80%; exact 8–2 and perfect 10–0 comparisons remain ordered in this range.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_record_probabilities.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** DO_NOT_ASSERT. Correct any version of this universal claim in existing S06.

## S07

### S07-01 — conditional

Observed Top 8 standings conversion was 16/216 at 5–1 and 36/37 at 6–0.

**Evidence:** official_standings_reconstruction. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Descriptive eight-event cohorts; not causal or skill-conditioned forecasts; these are R6 records.
**On screen:** Descriptive eight-event cohorts; not causal or skill-conditioned forecasts; these are R6 records.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_historical_record_cohorts.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-02 — conditional

Historical hybrid conditional EVs were approximately 57.139 and 212.108 tickets.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Observed R6→R7 outcomes fixed; future bracket q=50%; these are not measured receipts.
**On screen:** Observed R6→R7 outcomes fixed; future bracket q=50%; these are not measured receipts.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_historical_hybrid_rewards.csv; outputs/figures/conditional_reward_curve.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-03 — conditional

A secured historical Top 8 slot had a published 144-ticket floor, exceeding Vegas’s 80-ticket ceiling.

**Evidence:** published_payout_comparison. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** The cut must be secured; a 6–0 checkpoint did not always secure it. Eligibility and settlement still apply.
**On screen:** The cut must be secured; a 6–0 checkpoint did not always secure it. Eligibility and settlement still apply.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_secured_cut_rewards.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-04 — anecdotal

The owner personally received 216 tickets from a Top 8 split after an undefeated Swiss run.

**Evidence:** owner_firsthand_observation. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Firsthand anecdote; event/date/final Swiss record and frequency unknown.
**On screen:** Firsthand anecdote; event/date/final Swiss record and frequency unknown.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** data/conditional_rewards/observations.json; machine-readable cells preferred.
**Official source:** No official event-specific corroboration.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-05 — conditional

An equal Top 8 split pays 216 each and conserves the 1,728 pool.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Separate scenario, not a universal historical agreement; Top4/Top2 scenarios are later stages.
**On screen:** Separate scenario, not a universal historical agreement; Top4/Top2 scenarios are later stages.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_secured_cut_rewards.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-06 — conditional

Historical prize sharing and Vegas match draws are different mechanisms.

**Evidence:** mechanism_distinction. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** A split reallocates placement prizes; a draw changes points and point-band awards.
**On screen:** A split reallocates placement prizes; a draw changes points and point-band awards.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_secured_cut_rewards.csv;outputs/tables/conditional_vegas_final_round_rewards.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S07-07 — conditional

Vegas final-match expected payouts are 35/50/70 from 8–2/9–1/10–0 at p=50%.

**Evidence:** exact_model. Reports: [CONDITIONAL_PERFORMANCE_AND_SPLITS.md](CONDITIONAL_PERFORMANCE_AND_SPLITS.md).
**Spoken qualification:** Entering Round11; completion/eligibility assumed; draw outcomes are local cases, not guaranteed strategies.
**On screen:** Entering Round11; completion/eligibility assumed; draw outcomes are local cases, not guaranteed strategies.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/conditional_vegas_final_round_rewards.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S08

### S08-01 — supported

All eight archived regional schedules offered the BO3 three-win competitive ODE paying 12 to the winner.

**Evidence:** official_offer_inventory. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** That historical-style offer is absent from the current Vegas inventory, not proven absent from every future organizer revision.
**On screen:** That historical-style offer is absent from the current Vegas inventory, not proven absent from every future organizer revision.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_historical_ode_offers.csv;outputs/tables/phase4_event_inventory.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S08-02 — supported

The matching casual ODE also existed historically in all eight cities.

**Evidence:** official_offer_inventory. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Do not present today’s casual option as a newly introduced mean-throughput improvement.
**On screen:** Do not present today’s casual option as a newly introduced mean-throughput improvement.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_historical_ode_offers.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Correct any implied competitive-to-casual replacement narrative in S08.

### S08-03 — conditional

At 50% match p, competitive and casual ODEs both average 1.5 tickets per pod.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Same p across BO3/BO1 is imposed; old maximum12 versus casual3. Old EV=12p³, casual EV=3p.
**On screen:** Same p across BO3/BO1 is imposed; old maximum12 versus casual3. Old EV=12p³, casual EV=3p.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_ode_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S08-04 — conditional

Published mean rates were 0.4 versus 0.6667 tickets/hour before queues at p=50%.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Per-pod equality is not per-hour equality; the casual offer already existed.
**On screen:** Per-pod equality is not per-hour equality; the casual offer already existed.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_ode_comparison.csv; outputs/figures/phase5_competitive_ode.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S08-05 — conditional

The primary Vegas solo Constructed ODE schedule fits eight pods, maximum24; even zero queue fits eleven, maximum33.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Published duration/window model with available pods; this rules out40 from zero within those modeled constraints, not all real throughput.
**On screen:** Published duration/window model with available pods; this rules out40 from zero within those modeled constraints, not all real throughput.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase4_queue_duration_sensitivity.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S09

### S09-01 — conditional

For eight people, pooling’s first-threshold increment is 21.82 points historically versus33.87 in Vegas.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** N512/equal skill/no draws; finite historical rank sampling versus independent Vegas paths; unrestricted pooling hypothetical.
**On screen:** N512/equal skill/no draws; finite historical rank sampling versus independent Vegas paths; unrestricted pooling hypothetical.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_saturday_comparison.csv; outputs/figures/phase5_pooling_advantage.png.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S09-02 — conditional

Absolute pooled success is still lower:62.36% historically versus57.23% Vegas for eight.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** First group threshold, not one metal per person.
**On screen:** First group threshold, not one metal per person.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_saturday_groups.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S09-03 — conditional

Potential-unit efficiency does not uniformly become more aggregation-favorable.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Increment per person:0.06763 old official versus0.06597 Vegas; old split0.06528 reverses the small comparison.
**On screen:** Increment per person:0.06763 old official versus0.06597 Vegas; old split0.06528 reverses the small comparison.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_saturday_groups.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S09-04 — conditional

Historical independent sampling gives62.18% pooled success and21.85-point pooling increment at eight.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Sensitivity, not finite-field truth; the larger Vegas pooling increment persists.
**On screen:** Sensitivity, not finite-field truth; the larger Vegas pooling increment persists.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_group_sampling_sensitivity.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S09-05 — conditional

Pooling consolidates remainders but creates no additional gross tickets.

**Evidence:** ticket_conservation_identity. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Potential unit capacity does not prove permitted transfers, claims or actual aggregation prevalence.
**On screen:** Potential unit capacity does not prove permitted transfers, claims or actual aggregation prevalence.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_saturday_groups.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S09-06 — unresolved

Unrestricted cross-attendee ticket pooling is a verified current permission.

**Evidence:** policy_gap. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Ticket-specific transfer/control rules were not established; general sharing provisions are conditional.
**On screen:** Ticket-specific transfer/control rules were not established; general sharing provisions are conditional.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** DO_NOT_ASSERT. Do not conflate ordinary friends, large groups and match manipulation.

## S10

### S10-01 — conditional

Historical main-event registry overlap is about79% Friday,4% Saturday and71% Sunday.

**Evidence:** aggregate_official_ID_linkage. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Shares of side standings entries, exact identifiers; not physical attendance, skill or unique people across cities.
**On screen:** Shares of side standings entries, exact identifiers; not physical attendance, skill or unique people across cities.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_weekday_summary.csv; outputs/figures/phase6_field_composition.png.
**Official source:** https://locator.riftbound.uvsgames.com/events/502327; all eight official IDs in data/phase6/main_events.json; side sources in data/events.json.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S10-02 — conditional

Most main-linked Sunday entrants were below the main-event Day2 gate.

**Evidence:** aggregate_qualification_reconstruction. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Qualification inferred from published18-point gate and R8 standings; observed R9 pairings are separate.
**On screen:** Qualification inferred from published18-point gate and R8 standings; observed R9 pairings are separate.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_sunday_qualification.csv; machine-readable cells preferred.
**Official source:** https://locator.riftbound.uvsgames.com/events/502327; all eight official IDs in data/phase6/main_events.json; side sources in data/events.json.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S10-03 — conditional

Main-linked players have different observed cross-group match results within the same side events.

**Evidence:** descriptive_within_event_match_association. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Selected participants and repeated matches; pooled win fractions do not estimate field skill or assign Vegas p.
**On screen:** Selected participants and repeated matches; pooled win fractions do not estimate field skill or assign Vegas p.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_weekday_summary.csv; machine-readable cells preferred.
**Official source:** https://locator.riftbound.uvsgames.com/events/502327; all eight official IDs in data/phase6/main_events.json; side sources in data/events.json.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S10-04 — supported

Vegas’s championship begins Friday and leaves only semifinalists competing Sunday.

**Evidence:** official_RC_schedule. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Theoretical availability shifts; eliminated RC players need access and separately booked side entries.
**On screen:** Theoretical availability shifts; eliminated RC players need access and separately booked side entries.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://playriftbound.com/en-us/news/organizedplay/north-american-regional-championship-info/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S10-05 — unresolved

Friday is the weakest Vegas side-event field.

**Evidence:** unsupported_field_strength_ranking. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Not established: RC qualification, self-selection, other competitors and side entries remain unknown.
**On screen:** Not established: RC qualification, self-selection, other competitors and side entries remain unknown.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_composition.csv; machine-readable cells preferred.
**Official source:** https://playriftbound.com/en-us/news/organizedplay/north-american-regional-championship-info/.
**Production action:** DO_NOT_ASSERT. Present Friday as potentially less exposed to active RC competitors, not easier matches.

## S11

### S11-01 — conditional

Sunday Challenge averages10.625 tickets but gives only3.125% chance of40 from zero at p50.

**Evidence:** exact_model. Reports: [PHASE4_INDIVIDUAL_ACQUISITION.md](PHASE4_INDIVIDUAL_ACQUISITION.md).
**Spoken qualification:** Mean value and threshold acquisition are different objectives.
**On screen:** Mean value and threshold acquisition are different objectives.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_event_objectives.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S11-02 — conditional

Friday 2v2 averages11.875 tickets/team, hypothetically5.9375/person under equal allocation.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** Team win probability50%; fee25/50 per person and individual division remain unresolved.
**On screen:** Team win probability50%; fee25/50 per person and individual division remain unresolved.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_friday_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S11-03 — conditional

Friday Sealed plus Nexus averages9 personal tickets at75USD and6.5 occupied hours.

**Evidence:** exact_model. Reports: [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
**Spoken qualification:** More mean tickets/less time than equal-allocated Friday team at p50, but no40-from-zero tail; products unvalued.
**On screen:** More mean tickets/less time than equal-allocated Friday team at p50, but no40-from-zero tail; products unvalued.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase5_friday_comparison.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S12

### S12-01 — conditional

The mixed reference reaches40 with11.93% probability,135USD entry spend and19.5 occupied hours.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Conditional fixed schedule and hypothetical p50; booked seats, queues and prize settlement assumptions apply.
**On screen:** Conditional fixed schedule and hypothetical p50; booked seats, queues and prize settlement assumptions apply.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_itineraries.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-02 — conditional

The adaptive finite-menu benchmark reaches18.84%, averaging175.64USD and21.16 occupied hours.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Availability of future actions is unverified; not a guaranteed bookable itinerary or global optimum.
**On screen:** Availability of future actions is unverified; not a guaranteed bookable itinerary or global optimum.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_itineraries.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-03 — conditional

At a hypothetical70% across formats, mixed gives51.09% versus35.57% competitive-first.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** No measured classification of real people; premier competition can be the objective regardless of threshold ranking.
**On screen:** No measured classification of real people; premier competition can be the objective regardless of threshold ranking.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_itineraries.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-04 — supported

Rebound qualification blocks the11AM Sunday Challenge.

**Evidence:** schedule_conflict. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Do not assume late entry, post-elimination availability, refunds or early release.
**On screen:** Do not assume late entry, post-elimination availability, refunds or early release.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** AVAILABLE_WITH_STATED_SCOPE. Use with the specified qualification.

### S12-05 — conditional

The equal-allocation Friday-team mixed example gives17.47% personal success and23.49 occupied hours.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Expected selected entry spend131.56/156.56USD under25/50USD fee scenarios; full booking135/160; allocation unverified.
**On screen:** Expected selected entry spend131.56/156.56USD under25/50USD fee scenarios; full booking135/160; allocation unverified.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_itineraries.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-06 — conditional

With20/25/30 tickets, Sunday Challenge reaches40 with18.75%/50%/50% at p50.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Gap-aware advice depends on the remaining schedule and advance registration.
**On screen:** Gap-aware advice depends on the remaining schedule and advance registration.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_close_to_40.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-07 — conditional

With35 tickets, Nexus succeeds31.25% and Sealed50% at p50.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** One casual pod and Trial cannot fill a five-ticket gap; choose using fee/time/product preference.
**On screen:** One casual pod and Trial cannot fill a five-ticket gap; choose using fee/time/product preference.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_close_to_40.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-08 — conditional

With38 tickets, casual pod/Trial/Sealed give50%/87.5%/100% conditional threshold chance at p50.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Sealed’s two-ticket floor assumes completion and eligibility; none guarantees inventory or redemption.
**On screen:** Sealed’s two-ticket floor assumes completion and eligibility; none guarantees inventory or redemption.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_close_to_40.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-09 — conditional

With Sunday Challenge p=50%, Rebound’s standalone p40 break-even is about49.7%. The tiny p50 no-draw edge also reverses under the existing2% independent-draw sensitivity.

**Evidence:** exact_model. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Same50USD fee, different time commitments; hypothetical p/draw assumptions, not a weekend optimum or field forecast.
**On screen:** Both cost50USD, but different time commitments; not a weekend optimum or forecast.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_performance_thresholds.csv;outputs/tables/phase6_draw_robustness.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

### S12-10 — conditional

Scheduled entry needs advance purchase and a valid festival pass; current availability and exact cutoffs remain unknown.

**Evidence:** official_operations_plus_gap. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Entry-only cost models exclude passes/fees; fallback booking can leave unused nonrefundable tickets.
**On screen:** Entry-only cost models exclude passes/fees; fallback booking can leave unused nonrefundable tickets.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/phase6_operations.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.

## S13

### S13-01 — unresolved

The research establishes a comprehensive historical whole-weekend decline in metal accessibility.

**Evidence:** scope_limit. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Not established; no comparable historical whole-weekend optimizer, observed issuance or redemption baseline.
**On screen:** Not established; no comparable historical whole-weekend optimizer, observed issuance or redemption baseline.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** docs/PHASE4_INDIVIDUAL_ACQUISITION.md;docs/PHASE5_GROUP_AND_TEAM_ECONOMICS.md; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** DO_NOT_ASSERT. Conclude with demonstrated Saturday changes, lost competitive ODE upside and conditional practical choices.

### S13-02 — conditional

The strongest result is lower matched-attendance Saturday opportunity and reduced competitive upside, with stronger pooling incentives for the first group threshold.

**Evidence:** cross_phase_synthesis. Reports: [PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md](PHASE6_FIELD_COMPOSITION_AND_RECOMMENDATIONS.md).
**Spoken qualification:** Keep field composition descriptive and actual whole-weekend redemption unresolved.
**On screen:** Keep field composition descriptive and actual whole-weekend redemption unresolved.
**Assumptions:** Published schedules; model assumptions where numerical; no physical issuance/redemption inference.
**Support:** outputs/tables/saturday_analytical_comparison.csv;outputs/tables/phase5_saturday_comparison.csv;outputs/tables/phase6_weekday_summary.csv; machine-readable cells preferred.
**Official source:** https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/.
**Production action:** INCLUDE_QUALIFICATION. Use with the specified qualification.
