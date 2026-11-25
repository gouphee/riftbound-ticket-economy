# Research brief: Riftbound's prize-wall ticket economy

## Purpose

Produce a reproducible analysis and a companion video/essay, provisionally titled **Why It Just Got Harder to Get a Metal Legend**, with a subsequent on-site Convergence Fest field report. The question is not simply whether the highest prize was reduced. It is whether successive event designs changed (a) how many tickets are awarded, (b) how hard it is for one player to reach the **40-ticket metal threshold**, and (c) the relative incentive to coordinate and consolidate tickets.

The working concern is **organized high-throughput farming**, not metal-card sellouts. A few friends pooling spare tickets to help obtain a single metal is meaningfully different from large groups repeatedly concentrating hundreds of tickets. Neither grouping nor pooled accumulation alone proves match fixing. Acknowledge that lowering the former 432-ticket first prize is a defensible competitive-design choice.

## Historical scope and comparable events

Use **Atlanta, Sydney, Vancouver, Utrecht, Hartford, Barcelona, Singapore, and Los Angeles (2026)** as the historical cohort. The repository holds **24 events: three per RCQ**, listed with exact identifiers in `data/events.json`.

| Historical event | Closest Vegas event | Main comparison |
| --- | --- | --- |
| Friday Pre-Regional Challenge (five or six rounds, depending on city) | Sunday five-round Standard Challenge | Win-threshold tickets, variance, tickets per participant and hour |
| Sunday Regional Rebound (six-round standalone 1v1) | Sunday five-round Standard Challenge | Same, carefully controlling for the extra historical round |
| Saturday Super Saturday Challenge (seven Swiss + Top 8) | Vegas two-day Standard Rebound (six rounds + five for qualifiers) | Official placement pool, maximum personal payout, pooled Top 8 alternative, maximum-capacity and equal-entrant counterfactuals |
| Historical competitive and casual on-demand events | Vegas casual on-demand events | Entry cost, duration, payout structure, repeated-pod throughput |
| Nexus Night | Vegas Nexus Nights | Win-based ticket reliability and time efficiency |

TFT events at Convergence Fest contribute to the same prize-wall ticket economy but have **no direct historical Riftbound-RCQ counterpart**. Track separately, not as a replacement event. Tournament time overlaps prevent simply summing individual expected values as if every event were accessible to one person.

## Payout accounting

- The historical Saturday published Top 128 pool is **4,992 tickets** when all prize positions are awarded. Its Top 8 pool totals **1,728**. An equal Top 8 split gives **216 each**, preserving the total. This is a **reported practice**, not an independently verified agreement for every scoped RCQ.
- Friday/Sunday historical payouts are city-specific; use `data/processed/payout_rules.json` and the official source for each event, not one remembered universal table.
- The public standings support reconstruction of **published-rule entitlements**, not proof of physical prize claims. For unresolved drops/brackets use labeled subtotals/bounds/scenarios rather than false exactness.
- Vegas forecasts must use its current, separately sourced event tables and attendance caps. Distinguish *no-draw expected/fixed-cap distribution* from a genuine *maximum over all legally possible results*. The two are not automatically identical.
- A metal's 40-ticket redemption is a useful threshold, but receiving a metal and ultimately owning one are different outcomes where badges and gifting are involved.

## Research questions and deliverables

1. **Historical change:** event-by-event actual standings-based published ticket entitlements, plus fixed-participation counterfactuals showing the impact of payout changes.
2. **Opportunity/time:** how skill, event choices, brackets, duration, queues, conflicting schedules and risk affect an individual player's probability of accumulating 40 tickets during a weekend.
3. **Coordination:** how much faster a group can concentrate 40 or more tickets in wall-clock time; report aggregate participant-hours separately.
4. **Design:** sensitivity of the outcomes to organizer training/enforcement, centralized or randomized ODE queues, repeated-entry cooldowns, and account-linked tickets; identify effects on legitimate friends.
5. **Reporting:** source-backed essay and 12–15-minute video before Vegas, followed by an on-site observational follow-up with careful consent and non-accusatory claims.

## Evidence standard

Use the repository's `docs/METHODOLOGY.md`, `docs/DATA_DICTIONARY.md`, and `docs/KNOWN_GAPS.md`. A community photo or first-person account can motivate a hypothesis but should not be used to calculate aggregate prevalence. Source the latest official rules for prohibitions on sales, transfers, pooling, concessions and organized play before asserting an official policy. Riot's claim about increasing tickets for revised **2v2** payouts is not automatically a claim about all 1v1 events.

See `docs/AUDIT_2026-11-24.md` for the initial static repository review, `docs/MODELING_SPEC.md` for the updated **observed versus theoretical maximum** and draw-rate requirements, and `docs/RESEARCH_ROADMAP.md` for the prioritized next tasks.
