# Project handoff

Updated **2026-11-25 America/Chicago after Phase 4**. Read `AGENTS.md`, inspect
`git status` and use actual validation logs for execution claims. Phase 4 changes
are left for review; no commit, push or deployment is included.

## Framing and preserved findings

Working title: **Why It Just Got Harder to Get a Metal Legend**. The title is
supported at the matched-attendance Saturday-event level, but **not established
for equivalent entire weekends**. Analyze incentives and measurable outcomes;
no grouping or legitimate ticket sharing alone establishes manipulation.
No final video script exists. Physical issuance and redemption remain distinct
from published-rule entitlements and modeled accumulation.

The historical 24-event archive spans Atlanta, Sydney, Vancouver, Utrecht,
Hartford, Barcelona, Singapore and Los Angeles. It preserves 20,651 standings
entries and 20,652 roster entries. Phase 2 Friday/Sunday qualifying entitlements,
including qualifying `DROPPED` entries, are **119,587 / 60,556**. Each Saturday
has a conditional **4,992-ticket** funded Top 128 pool. Swiss draws are
**1,150 / 50,262 = 2.2880%**, excluding byes/non-games. Exact Swiss maxima remain
unresolved; ceilings and feasible witnesses are separate. All old exceptions
in [KNOWN_GAPS.md](KNOWN_GAPS.md) remain unchanged.

At equal N=512, the Saturday equal-skill/no-draw benchmark is **6.25% historical
versus 3.271484375% Vegas** for 40+, with means **9.75 versus 5.6591796875**.
Vegas has six rounds, ≥12 points to qualify, then five Sunday rounds. At 2%
independent draws, P(40+)≈2.8167%, mean≈5.40862; these are scenarios, not fitted
forecasts. Old Phase 3A/3B source captures, outputs and local outcome matrices
remain intact. Do not infer strategic-draw frequency from the local matrices.

## Phase 4: current evidence and reusable implementation

Read [PHASE4_INDIVIDUAL_ACQUISITION.md](PHASE4_INDIVIDUAL_ACQUISITION.md).
The directly retrieved official US schedule is byte-identical to Phase 3A;
all 33 event rows match. It lists 29 ticket-awarding offers, three continuation
rows and one Learn to Play offer without advertised prizes. ODE offers are
repeatable types, not observed pod counts. The live search snippet was stale;
use the preserved direct capture. Two stale Round 10 sentences persist, while
explicit six-plus-five and the earlier official announcement govern Rebound.

- Sources: `data/raw/phase4/retrievals.jsonl`, `data/phase4/sources.csv` and
  `data/phase4/source_review.json`. Failed initial network captures and Tixr's
  403 are preserved. Exact badge cost/cutoffs remain unknown. The catalog confirms
  40-ticket plated Legend prices, without inventory/transfer/redemption policy.
- Core model: `src/riftbound_tickets/models/individual.py`; orchestration:
  `src/riftbound_tickets/phase4.py`; isolated collector and figures are in
  `collectors/phase4_sources.py` and `charts/individual.py`.
- Standard-library exact fractions, PMFs, convolution and finite-menu Bellman
  decisions. No Monte Carlo, player-rating or finite-field Swiss model.
- Outputs: `outputs/tables/phase4_*.csv`, including complete event PMFs/economics,
  all performance/draw sensitivities, finite ODE sensitivity, nonoverlapping
  schedules, adaptive menu/reachable decisions, final strategy results/primary
  PMFs, starting tickets, hard budgets/time and an evaluated-strategy frontier.
- Seven SVG/PNG pairs: `outputs/figures/phase4_*`; manifest hashes table inputs,
  renderer and figure bytes. Report summary table is rebuilt/audited from CSV.
- 16 historical Friday/Sunday rule rows are re-parsed separately. The closest
  five-round comparison is historical Friday to Vegas Sunday. All 128 archived
  historical side-offer rows are indexed; they are not a historical attendee
  weekend/queue model.

## Individual findings and practical limits

Equal-skill/no-draw, conditional on admission, with published durations and
15-minute ODE queues:

| Strategy | P(40+) | Expected entry spending | Occupied hours |
|---|---:|---:|---:|
| Sunday Challenge only | 3.125% | $50.00 | 7.75 |
| Competitive first | 5.32% | $107.81 | 19.73 |
| Mixed Riftbound | 11.93% | $135.00 | 19.50 |
| Adaptive Riftbound menu | 18.84% | $175.64 | 21.16 |

The adaptive menu has a $200 cap, 30 occupied-hour cap and $185 maximum actually
spent in its primary policy. It excludes Rebound, teams and TFT, so it is not
a global festival optimum. At 70% p in every Riftbound format, mixed/adaptive
are about 51.09%/65.35%; constant strong performance can overstate later Swiss
results. Separate competitive-only sensitivities hold BO1 performance at 50%.
TFT exchangeable-rank models never inherit Riftbound skill.

Eight repeated Constructed ODEs fit the main windows: mean 12, maximum 24 tickets.
Zero queue permits 11 pods but still a maximum of 33. Thus these published-duration
solo ODE paths cannot reach 40 from zero even at 100% wins. Small events can
still supplement an existing balance; from 35, scheduled sealed succeeds 50%
at equal skill, reserving three event hours instead of Sunday's 7.5 for the
same $50. A complete limited-product valuation is intentionally absent.

Rebound blocks Saturday Nexus and qualifiers cannot enter Sunday Challenge.
Eliminated players' alternatives require timely advance purchase and seats.
No mid-event dropping/refund/early-release privilege is invented. The model stops
at event-boundary settlement; per-win prizes might be collected earlier.
Budgets include unsuccessful entrants. Conditional success costs/time and surplus
are separate; E[tickets]/40 is never a success probability.

Active hours are explicit proxies, not measured play. Occupied hours include
queue/check-in but exclude separate-event gaps and sleep. CSV calendar spans
start Friday 11:00 and include overnight gaps. Required pass, transaction charges,
travel, lodging, food, decks, actual stock and badge restrictions are outside
ticket-only cost and remain unknown where not sourced.

## Validation and preservation

Run:

```sh
python3.12 scripts/validate_phase4.py
```

The runner executes unittest, the five required legacy commands, Phase 2/3A/3B
audits and Phase 4 build/figures/audit. Read the actual result in
`outputs/tables/phase4_execution_validation.json` and isolated logs under
`outputs/phase4/validation/`. All commands are offline; fresh collection is an
explicit separate command. Figures use the existing pinned `.venv-figures`.
Do not treat this description as proof of a newly executed run.

The completed Phase 4 run actually passed **139 tests and all 11 recorded
commands** on 2026-11-25 America/Chicago (2026-11-26 UTC), with all 794 protected
files unchanged. This is a record of that run, not a substitute for rerunning
checks after later edits. Earlier attempt logs/summaries remain available.

`data/phase4/preserved_artifacts.json` fingerprints 794 prior tracked files
from `ab77b63`; only authorized navigation/handoff/roadmap/changelog and general
current-code validation inventory updates are excluded. Legacy raw data, source
code, tests, exports, reports, figures and execution logs must remain identical.
Phase 4 tests cover independent small-case outcomes, source-payout checks,
qualification, old-model agreement, PMF/mean accounting, schedules, repeat limits,
resources, stopping, surplus, nonclairvoyant decisions and preservation.

## Remaining evidence and Phase 5 boundary

Material unknowns: per-event purchase cutoffs and real-time seats, ODE desk hours
and last launches, queues/pod availability, early check-in access, actual playing
and meal-break times, dropping and claims, individual team entitlements, full
entry cost, metal inventory/redemption/badge restrictions and transfer permission.
Historical side offers alone do not justify an observed whole-weekend baseline.
No player/organizer messages or private-identification research were undertaken.

**Do not start Phase 5 without the next task.** It will compare solo acquisition
with groups of 2/4/8, ordinary sharing of legitimately earned spares and ticket
concentration, reporting participant-hours as well as wall time. Reuse individual
PMFs and constraints, but verify ticket-transfer/control policy before assuming
pooling permission. No group allocation, ticket sale, manipulated-match strategy
or prevalence estimate is implemented. Policy options and video scripting remain
later work.
