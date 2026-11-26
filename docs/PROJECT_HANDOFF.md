# Project handoff

Updated 2026-11-25 after Phase 3B. Read `AGENTS.md` and inspect `git status`
before continuing. This file preserves research context; fresh execution claims
must come from newly run commands, not earlier success reports.

## Research question and framing

Working video title: **Why It Just Got Harder to Get a Metal Legend**. Analyze
how event design changes ticket generation, an individual's chance of reaching
40 tickets, and the incentive to consolidate tickets. Later work can distinguish
ordinary friends sharing spare tickets from high-volume coordinated aggregation.
Neither grouping nor pooling establishes match manipulation. A lower 432-ticket
first prize can be a defensible design change even when ordinary entrants face
a harder 40-ticket path. No video script has been written.

## Completed work and principal findings

- **Historical collection/audit:** 24 Friday/Saturday/Sunday events across
  Atlanta, Sydney, Vancouver, Utrecht, Hartford, Barcelona, Singapore and Los
  Angeles. There are 20,651 standings entries and 20,652 roster entries.
  Reproducible official captures preserve URLs, timestamps and hashes.
- **Phase 2:** qualifying Friday/Sunday records count even if `DROPPED`.
  Primary entitlements total 119,587 Friday and 60,556 Sunday tickets. Each
  Saturday has a conditional funded Top 128 pool of 4,992; all eight total
  39,936. Unique completed Swiss matches contain 1,150 draws / 50,262 = 2.2880%,
  excluding 130 byes and 234 one-player non-games. Exact Friday/Sunday Swiss
  maxima remain unresolved; proved relaxed ceilings and feasible witnesses
  are separate outputs.
- **Phase 3A:** exact equal-skill/no-draw Saturday comparison. At N=512,
  historical P(40+)=6.25%, mean=9.75 tickets; Vegas P(40+)=3.271484375%,
  mean=5.6591796875. Vegas qualification=34.375%. The gate precedes Sunday.
  Separate full caps compare old 512 with Vegas 1,024: 4,992 fixed versus
  5,795 expected tickets. Attendance is not assumed to reach capacity.
- **Phase 3B:** exact 0/1/2/5% independent draw sensitivity. At 2% and
  hypothetical N=1,024: 333.016318208 expected qualifiers, P(40+)≈2.8167%,
  mean≈5.40862, total≈5,538.43, 28.84299 expected 40+ entrants. At 5%, P(40+)
  is ≈2.2368%. Zero draws reproduces Phase 3A exactly.
- **Local outcomes:** at Round 11, all seven equal-score cases without prior
  draws preserve combined tickets. Unequal pairs can differ across realized
  results, but the draw total equals the average of the two decisive totals
  on this score grid. At 24–24 a draw pays 35+35 versus decisive 40+30, changing
  who reaches 40. Round 6 at 9–9 advances nobody on a draw and one on a decisive
  result. Qualification is separate from future ticket EV.

## Sources and implementation pointers

- Historical identifiers: [`data/events.json`](../data/events.json).
  Raw ledger: `data/raw/retrievals.jsonl`; source index: `data/sources.csv`.
  Every historical schedule is parsed event-specifically.
- Vegas official [Riot schedule](https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/)
  and [eleventh-round announcement](https://x.com/RiotSherman/status/2122889583201591569)
  were archived in Phase 3A and reused in Phase 3B. The schedule specifies
  **six rounds + five for qualifiers, cut ≥12 points, cap 1,024**, despite stale
  Round 10 sentences. Phase 3B did not check for later live revisions.
- Vegas awards: 19–20 points→10; 21→20; 22–23→25; 24→30; 25–26→35;
  27→40; 28–29→50; 30→60; 31–32→70; 33→80. Below 19 pays zero.
- Start with [Phase 2](PHASE2_HISTORICAL_ANALYSIS.md),
  [Phase 3A](PHASE3A_SATURDAY_COMPARISON.md), and
  [Phase 3B](PHASE3B_DRAW_SENSITIVITY.md). Core analytical modules are
  `models/saturday_analytical.py` and `models/saturday_draws.py` under
  `src/riftbound_tickets/`. No Monte Carlo or player-rating model exists.
- New outputs use `saturday_draw_*`; local matrices use
  `saturday_final_round_outcomes.csv`. Phase 3B preserves 750 prior files with
  hashes in `data/phase3b/preserved_artifacts.json`. General validation metadata
  can refresh its code inventory; historical/Phase 3A artifacts remain intact.

## Assumptions and unresolved evidence

Physical ticket issuance is unverified without a claim ledger. Unknown final
placements, eligibility and records must not become zeros. `DROPPED` is not
automatic prize ineligibility; keep the original conservative fields as a
sensitivity. No explicit DQ is established by these archived status labels.

Historical Top 8 split=216 each is a separate scenario conserving 1,728 tickets;
no event-specific agreement is newly verified. Several cuts are incomplete.
Atlanta Friday has one roster-only entry. Hartford Friday's 0–3–0 has no match
observations. Utrecht Saturday has unresolved cut results/draw credits.
Barcelona Saturday observed 518 entries exceeds advertised 512; keep the gap.
See [KNOWN_GAPS.md](KNOWN_GAPS.md) and the later Phase 2 reporting distinctions.

The Vegas analyses are marginal equal-skill benchmarks with independent
outcomes, no byes, drops or finite-field Swiss enforcement. Rates are scenarios,
not fitted forecasts; historical strategic Round 7 draws do not automatically
transfer to Vegas. Matrices establish individual path feasibility, not joint
Swiss pairings or likely matchup frequencies. Field-strength differences from
Friday-eliminated RC players entering Saturday are qualitative. Current policy
on transfers, concessions and prize arrangements needs separate official
verification before making permission claims. Having 40 tickets does not prove
Metal Legend inventory, badge eligibility, redemption or ownership.

## Verification and next tasks

Run `python3.12 scripts/validate_phase3b.py` for the complete current offline
suite and new isolated logs. It runs the existing historical checks and
Phase 2/3A/3B audits. Read `outputs/tables/saturday_draw_execution_validation.json`
for actual results and log hashes. Optional figures use the pinned
`.venv-figures` environment and `python -m riftbound_tickets.phase3b figures`.
The completed Phase 3B run passed 113 tests and all nine recorded commands;
750 prior research files remained byte-identical. This is the recorded run,
not a substitute for running checks after subsequent edits.

Next specify a small stage-/record-dependent draw sensitivity and review
finite-field byes/pairings before making forecasts. Complete separately sourced
Friday/Sunday and other like-for-like comparisons, then identify weekend time,
schedule-conflict and queue assumptions. Weekend ODE economics, coordinated
pooling, full Swiss/ratings models and a video script require a later task;
none was started in Phase 3B. Stuttgart Nation Clash is only a potential future
observational comparator; no Stuttgart collection was performed.
