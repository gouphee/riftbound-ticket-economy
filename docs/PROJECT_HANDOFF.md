# Project handoff

Updated **2026-11-26 America/Indianapolis after Phase 5**. Read `AGENTS.md`, inspect
`git status`, and distinguish recorded executions from newly run checks.
Phase 4 is committed at `4c59142`; Phase 5 changes are left for review without
commit or push. The next task is **competitive field-composition assessment and
final recommendation synthesis**, not video scripting or production.

## Purpose and boundaries

The first of three planned videos is the provisional **Why It Just Got Harder
to Get a Metal Legend**, an accessible 15–18-minute research essay for Vegas
attendees outside the invitational Regional Championship. Beginner prize-wall
education and prize-buying recommendations are separate videos, outside this
repository's current task. No secondary-market valuations or final script exist.
Ordinary grouping/sharing is not evidence of manipulation. Actual issuance and
redemption remain distinct from published entitlements and model capacities.

A harder matched-attendance Saturday event is supported. An equivalent **whole-
weekend historical decline remains unestablished**. Do not force that title
claim or use individual/group means as probabilities of redeeming metals.

## Earlier research retained

The historical archive covers 24 events across Atlanta, Sydney, Vancouver,
Utrecht, Hartford, Barcelona, Singapore and Los Angeles: 20,651 standings and
20,652 roster entries. Phase 2 qualifying-record entitlements, including
qualifying `DROPPED` entries, total **119,587 Friday / 60,556 Sunday**. Saturday
is a conditional funded **4,992-ticket** Top 128 pool per event. Swiss draws are
**1,150 / 50,262 = 2.2880%**, excluding byes/non-games. Exact Swiss maxima remain
unresolved; ceilings/witnesses are separate. See [KNOWN_GAPS.md](KNOWN_GAPS.md).

At matched N=512, the Saturday equal-skill/no-draw chance of 40+ is **6.25% old
versus 3.271484375% Vegas**, with means **9.75 / 5.6591796875**. Vegas has six
rounds, ≥12 points to qualify, then five Sunday rounds; stale Round 10 prose
remains documented. At 2% independent draws, P(40+)≈2.8167%, mean≈5.40862.
Local outcome grids do not establish strategic-draw frequency or likely pairings.

Phase 4's no-draw conditional individual weekend results remain:

| Strategy | P(40+) | Expected entry USD | Occupied hours |
|---|---:|---:|---:|
| Sunday Challenge | 3.125% | 50.00 | 7.75 |
| Competitive first | 5.32% | 107.81 | 19.73 |
| Mixed Riftbound | 11.93% | 135.00 | 19.50 |
| Adaptive Riftbound menu | 18.84% | 175.64 | 21.16 |

The adaptive menu is limited to its defined actions/resources, not a global
optimum. Individual stopping is event-boundary settlement at 40+. Costs include
failures. Eight published-duration Constructed ODEs fit the 15-minute queue
reference, mean 12 tickets, maximum 24; even zero queue's 11 pods cap at 33.
Required passes, transaction fees, travel, decks, actual seats and queues are
outside those ticket-only forecasts or remain unknown. No physical claims are
verified. [Phase 4 report](PHASE4_INDIVIDUAL_ACQUISITION.md) and all its artifacts
are protected.

## Phase 5 principal findings

Read [PHASE5_GROUP_AND_TEAM_ECONOMICS.md](PHASE5_GROUP_AND_TEAM_ECONOMICS.md).
At N=512/equal skill/no draws, historical ranks are sampled without replacement;
Vegas group members are independent marginal paths, not a joint Swiss field.

| Group size | Old pooled 40+ | Vegas pooled 40+ | Pooling increment old → Vegas |
|---:|---:|---:|---:|
| 2 | 14.07% | 9.53% | 1.94 → 3.09 percentage points |
| 4 | 31.48% | 25.89% | 8.67 → 13.43 percentage points |
| 8 | 62.36% | 57.23% | 21.82 → 33.87 percentage points |

Absolute and relative pooling **increments** increase, while absolute pooled
success falls. At eight people the relative lift is 53.80% historical versus
144.95% Vegas. Complete-unit efficiency is not uniformly more aggregation-
favorable: incremental units per person are **0.06763 old official / 0.06597
Vegas**. The separate historical Top 8 split has an increment of 0.06528,
reversing that small comparison. It is not an observed event-specific agreement.

Four mixed players have 99.47% potential aggregate 40+, versus 39.83% with any
individual independently at 40. Expected ticket capacity is 1.777 units/group,
with $540 expected entry spend and 78 occupied participant-hours. Capacity for
one unit **each** is only 0.405%. Pooling creates no gross tickets; residuals and
personal holdings retain value. Two explicitly defined partial-contribution
protocols substantially reduce sharing/capacity relative to full pooling.

Friday 2v2 pays per team, with mean 11.875 tickets at 50% team p/no draws. Its
$50 fee unit and individual allocation remain ambiguous. Hypothetical equal
integer allocation gives mean 5.9375/person and P(40+)=3.125%; team aggregate
P(40+)=18.75%. No individual probability is multiplied/averaged to derive team p.
It conflicts with Friday Nexus. Replacing mixed Friday Nexus with team play
raises a member example to **17.47%**, with **23.49 expected occupied hours**
and **$131.56/$156.56 expected entry cost** for $25/$50 individual fee scenarios.
Teammates share the Friday outcome; never convolve their team prizes as if
independent. Individual stopping can change later production under allocations.

All eight historical cities advertised competitive BO3 single-elimination ODEs
with 12 tickets for three consecutive wins. At equal p, both old and Vegas
Constructed ODEs mean 1.5/pod; published rates are 0.4 versus 0.6667 tickets/hour.
The old competitive ceiling is higher. The higher-rate casual offer also
existed in all eight historical schedules; it is not a new Vegas improvement.
Common-window examples are conditional on unknown historical desk hours and
full-slot reservation after losses. Native currencies are retained, not all USD.

## Policy evidence and operational cautions

Fresh sources: `data/raw/phase5/retrievals.jsonl`, `data/phase5/sources.csv` and
`source_review.json`. The official current Rules Hub links a PDF dated **October
9, 2026**. Pages 1/48 were extracted and visually checked. Section 704.5.b permits
conditional general prize-sharing; 704.5.a bars outcome-contingent incentives;
104.3 gives event addenda precedence. None establishes unrestricted post-award
prize-ticket pooling across attendees. Ticket transfer/control, per-person/badge
limits, inventory and identification requirements remain unresolved. Tixr again
returned 403. No organizer/player messages were sent.

A fresh verified primary announcement specifies **TFT ODEs begin noon Saturday**.
Do not promote Phase 4's preserved all-weekend TFT conditional rows as itinerary
advice. Phase 5's modeled weekends use Riftbound, so this discovery does not
alter their results. Team inventory retains TFT offers, but its focused W/D/L
models cover the four Riftbound team formats rather than assigning an arbitrary
W/D/L model to TFT lobbies.

The Friday field may differ because Vegas main-event competitors play Friday
where historical RQs generally began Saturday; this is **not measured field
strength**. Assess it in the next focused task using current official evidence,
without assigning weaker fields or higher p by assumption. Exact registration
cutoffs, sold-out states, queues, early check-in, drop/claim timing, actual play
and meals still need evidence before strong attendee recommendations.

## Reusable outputs and validation

New core: `models/aggregation.py`; orchestrator: `phase5.py`; isolated collector:
`collectors/phase5_sources.py`; figures: `charts/aggregation.py` under
`src/riftbound_tickets/`. Exact fractions, hypergeometric compositions and shared
team blocks; no Monte Carlo, rating/Swiss simulator or shared-target optimizer.

Fourteen `outputs/tables/phase5_*.csv` files cover policy/team evidence, team PMFs
and allocations, Saturday comparisons, stopped-weekend groups, partial protocols,
team weekend PMFs, historical ODE offers/controlled throughput and video claims.
Four SVG/PNG pairs are hashed in `outputs/figures/phase5_manifest.json`. Every
video finding has a claim, plain-English explanation, qualification and support.

```sh
python3.12 scripts/validate_phase5.py
```

The runner executes unittest, the five required legacy commands, Phase 2/3A/3B/4
audits and Phase 5 build/figures/audit. Read actual results in
`outputs/tables/phase5_execution_validation.json` and timestamped logs under
`outputs/phase5/validation/`. Do not substitute archived results for fresh checks.
`data/phase5/preserved_artifacts.json` fingerprints **875 prior tracked files**
from `4c59142`, except authorized navigation/handoff/changelog and the general
current-code validation report. Old data, code, reports, figures and execution
records must stay byte-identical.

The final Phase 5 run actually passed **161 tests and all 12 recorded commands**
on 2026-11-26 (America/Indianapolis), with all 875 protected prior files unchanged.
All four figure pairs passed hash checks and visual review. Earlier summaries,
including the pre-rebuild stale-schema failure, remain available. Rerun checks
after future edits; this records the completed run rather than promising later
execution results.

Next complete field-composition assessment and final recommendation synthesis.
Do not begin scripting/production, a full historical weekend optimizer, private
player identification, misconduct investigation, ticket-transaction strategies
or comprehensive policy redesign without the next authorized task.
