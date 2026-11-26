# Riftbound ticket economy

Reproducible research on the Friday Pre-Regional Challenge, Super Saturday
Standard Challenge, and Sunday Regional Rebound at the 2026 Atlanta, Sydney,
Vancouver, Utrecht, Hartford, Barcelona, Singapore, and Los Angeles Regional
Qualifiers.

The repository preserves official public standings, separate rosters, explicit
bye/match evidence, and each city's historical payout tables. It reconstructs
published ticket entitlements. **Actual physical ticket issuance is unverified:**
no claim/distribution ledger was recovered, so verified-issuance fields are blank.

## Phase 5 team events and ticket aggregation

[Phase 5](docs/PHASE5_GROUP_AND_TEAM_ECONOMICS.md) adds exact group sizes 1/2/4/8,
historical sampling without replacement, Vegas independence sensitivities,
partial contributions, Friday team allocations and controlled competitive ODE
comparisons. At eight people, pooling adds **21.82 percentage points historically
versus 33.87 in Vegas**, while the absolute pooled chance falls **62.36% to
57.23%**. This does not establish a whole-weekend historical decline. Ticket
pooling permission, individual team entitlements and actual redemption remain
unresolved; mathematical capacities are conditional counterfactuals.

Friday 2v2 expands the individual menu, but conflicts with Friday Nexus and
requires fee/allocation clarification. All eight historical cities offered the
winner-only competitive ODE; its mean per pod matches Vegas at equal skill,
while ceilings and published durations differ. The first video remains a
15–18-minute research essay; beginner education, buying recommendations and
scripting are separate tasks.

Start with [video findings](outputs/tables/phase5_video_findings.csv),
[Saturday comparison](outputs/tables/phase5_saturday_comparison.csv),
[weekend groups](outputs/tables/phase5_weekend_groups.csv), and four
`outputs/figures/phase5_*` SVG/PNG pairs. Fresh policy/official source captures
are isolated under `data/raw/phase5/`; the current October 9 tournament rules
and evidence review are under `data/phase5/`. Prior research is hash protected.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.phase5 build
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.phase5 figures
PYTHONPATH=src python3.12 -m riftbound_tickets.phase5 audit
python3.12 scripts/validate_phase5.py
```

## Phase 4 individual acquisition economics

[Phase 4](docs/PHASE4_INDIVIDUAL_ACQUISITION.md) inventories all 33 official
Vegas schedule rows and models individual awards, realistic time reservations,
finite ODE throughput, hard entry/time budgets and a limited adaptive menu.
At equal skill/no draws, representative mixed Riftbound success is **11.93%**;
the conditional adaptive menu reaches **18.84%**, averaging about **$176** in
entry fees and **21.2 occupied hours**. These require available seats/pods and
exclude festival passes/travel. They are not player forecasts or redemption odds.
Published-duration Constructed ODEs alone cannot reach 40 from zero in the
modeled weekend, even with every match won. A whole-weekend historical decline
remains unproven; the supported Saturday-event result is a separate finding.

Start with [strategy results](outputs/tables/phase4_strategy_results.csv),
[event inventory](outputs/tables/phase4_event_inventory.csv),
[hard budget/time comparisons](outputs/tables/phase4_budget_time_constraints.csv),
and the seven `outputs/figures/phase4_*` SVG/PNG pairs. New official captures,
source review and preservation hashes live under `data/raw/phase4/` and
`data/phase4/`. Prior research artifacts remain protected.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.phase4 build
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.phase4 figures
PYTHONPATH=src python3.12 -m riftbound_tickets.phase4 audit
python3.12 scripts/validate_phase4.py
```

## Phase 3B draw sensitivity and local match outcomes

The [draw analysis](docs/PHASE3B_DRAW_SENSITIVITY.md) extends the Saturday model
with exact 0%, 1%, 2% and 5% draw scenarios. At **2% draws**, Vegas's modeled
40+ chance is **2.8167%**, expected tickets per entrant are **5.40862**, and the
expected field total at 1,024 entrants is **5,538.43**. The no-draw result
reproduces Phase 3A exactly. These are hypothetical independent-outcome
sensitivities; historical strategic-draw rates are not treated as Vegas rates.

See [scenario totals](outputs/tables/saturday_draw_sensitivity.csv),
[award distributions](outputs/tables/saturday_draw_ticket_distributions.csv),
[point distributions](outputs/tables/saturday_draw_final_points.csv), and
[Round 6/11 outcome matrices](outputs/tables/saturday_final_round_outcomes.csv).
Five additional SVG/PNG pairs use the `saturday_draw_*` prefix. Round 11
equal-score cases without prior draws conserve combined tickets across
outcomes, while the number reaching 40 can change. Round 6 qualification and
future expected awards are reported separately. Pairing frequencies and
strategic outcome choices are not modeled.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.phase3b build
PYTHONPATH=src python3.12 -m riftbound_tickets.phase3b audit
python3.12 scripts/validate_phase3b.py
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.phase3b figures
```

Start a new research conversation with [PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md).
Previous raw data, Phase 2/3A exports, figures, execution logs and source code
remain unchanged. Phases 4 and 5 above extend individual and group economics. Field-composition
assessment and recommendation synthesis are next; scripting remains future work.

## Phase 3A Saturday analytical comparison

The [Saturday comparison](docs/PHASE3A_SATURDAY_COMPARISON.md) compares the
historical fixed placement pool with Vegas Standard Rebound's updated **6 + 5
rounds**, using exact equal-skill probabilities and the Day 2 qualification gate.
At 512 entrants, the modeled chance of earning 40+ tickets is **6.25% historical
versus 3.2715% Vegas**; expected tickets per entrant are **9.75 versus 5.6592**.
These are structural benchmarks, not observed Vegas results or physical claims.

See the [attendance comparisons](outputs/tables/saturday_analytical_comparison.csv),
[complete award distributions](outputs/tables/saturday_ticket_distributions.csv),
and five SVG/PNG figure pairs under `outputs/figures/saturday_analytical_*`.
Published full caps, hypothetical attendance, and eight recorded historical
field sizes are distinguished, including Barcelona's over-advertised-cap record.
The historical Top 8 split is a separate scenario conserving the same pool.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.phase3a build
PYTHONPATH=src python3.12 -m riftbound_tickets.phase3a audit
python3.12 scripts/validate_phase3a.py
# Optional figures using the pinned Matplotlib environment:
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.phase3a figures
```

The source snapshots and ledger are isolated under `data/raw/phase3a/`.
Historical and Phase 2 artifacts remain unchanged; the existing Phase 2
integration tests now rebuild into disposable outputs. No Monte Carlo, player
ratings, Swiss simulator, pooling model, or script is included in this stage.

## Phase 2 historical analysis

The [historical analysis](docs/PHASE2_HISTORICAL_ANALYSIS.md) adds primary
standings-implied totals including qualifying `DROPPED` records, the conditional
4,992-ticket Saturday pools, no-draw feasible Swiss constructions and proved
upper bounds, and match-weighted empirical draw rates. The exact Swiss maximum
is not claimed. Original strict exports and eligibility sensitivities remain.

Start with [Phase 2 event comparisons](outputs/tables/historical_ticket_economy.csv),
[cohort summaries](outputs/tables/historical_cohort_summary.csv), and
[draw rates](outputs/tables/historical_draw_rates.csv). Six PNG/SVG figure pairs
are available under `outputs/figures/historical_*`.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.cli phase2
PYTHONPATH=src python3.12 -m riftbound_tickets.cli audit-phase2
```

For optional Matplotlib figures, see the pinned environment instructions in
[the Phase 2 method](docs/PHASE2_HISTORICAL_ANALYSIS.md#files-and-reproducibility).

## Original strict extraction and audit

Start with [event totals](outputs/tables/event_summary.csv),
[payout distributions](outputs/tables/payout_distribution.csv), and the
[coverage and gaps](docs/COVERAGE.md). A known subtotal is not an exact event total.
The initial run recovered **20,651 standings rows across all 24 events**, including
all three Utrecht events. See [known gaps](docs/KNOWN_GAPS.md) for source contradictions.

## Reproduce offline

Python 3.10+ is required; the commands below use the available Python 3.12.
Collection, calculations, and tests use only the standard library. No API key,
account, notebook package, or external database is required.

```sh
PYTHONPATH=src python3.12 -m unittest discover -s tests -v
PYTHONPATH=src python3.12 -m riftbound_tickets.cli build
PYTHONPATH=src python3.12 -m riftbound_tickets.cli verify
PYTHONPATH=src python3.12 -m riftbound_tickets.cli audit
PYTHONPATH=src python3.12 -m riftbound_tickets.cli validate-pilot
```

`build` verifies that collection manifests replay from the raw evidence and
recalculates CSVs without network access. `verify` hashes all raw objects.
`audit` reconciles every event export and payout distribution, saving a validation
report with input/code hashes in `outputs/tables/validation_report.json`.
`validate-pilot` checks the reviewed Atlanta Friday/Sunday extraction, payout
bins, and documented one-entry Friday reconciliation gap.

Optional editable installation provides the `riftbound-tickets` command:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/riftbound-tickets build
```

## Collect or refresh public evidence

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.cli collect --scope pilot
PYTHONPATH=src python3.12 -m riftbound_tickets.cli validate-pilot
PYTHONPATH=src python3.12 -m riftbound_tickets.cli collect --scope all --workers 3
PYTHONPATH=src python3.12 -m riftbound_tickets.cli build
```

Broader collection reruns the pilot gate first. Existing successful URL captures
are cached. Add `--refresh` to preserve new snapshots; prior evidence remains.
Use `--event utrecht-saturday` to target one event. A changed pilot snapshot fails
the reviewed baseline until the differences are investigated and documented.
Network failures are recorded rather than replaced with synthetic standings.

## Important distinctions

- Roster counts, final standings rows, and participants with match evidence are
  distinct columns. Missing standings are never supplied from a roster count.
- Match wins, losses, draws, explicit byes, and drops are preserved. Unknown
  fields are blank. Draws do not count as wins for a win-threshold payout.
- Historical payout changes are parsed from each official schedule. There is
  no single universal Friday or Sunday table.
- Saturday official placement payouts and the reported **216 per Top 8 player**
  equal-split practice are separate outputs. The split conserves the 1,728-ticket
  Top 8 pool. Event-specific split agreements remain unverified.
- “Complete” round metadata alone is insufficient to verify a Top 8 finish;
  missing or unresolved bracket matches are flagged.

The first pilot recovered 1,019 Atlanta Friday standings rows (1,020 roster
entries), yielding 9,432 known published entitlements, and all 612 Atlanta Sunday
rows, yielding a fully reconciled 5,496-ticket entitlement reconstruction. These
are historical rule calculations, not confirmed prize claims.

## Layout

```text
data/raw/                      Original HTTP evidence and retrieval ledger
data/interim/                  Compressed collection manifests
data/processed/<event>/         Standings, separate roster, match observations
data/events.json                Explicit official identifier registry
data/sources.csv                Source URLs, retrievals, hashes, raw paths
src/riftbound_tickets/collectors Public-source extraction and pagination
src/riftbound_tickets/payouts/   Independently testable historical payout functions
src/riftbound_tickets/models/    Deterministic historical bounds; no Monte Carlo
src/riftbound_tickets/charts/    Standalone historical research figures
tests/                         Unit tests and archived pilot regression checks
notebooks/                     Exploration guidance
outputs/tables/                Event summaries, distributions, and issue ledger
outputs/figures/                Reserved for figures
docs/                          Method, field definitions, sources, and gaps
```

Read [the methodology](docs/METHODOLOGY.md) and
[data dictionary](docs/DATA_DICTIONARY.md) before interpreting the outputs.
No Monte Carlo simulation or video scripting has been started.
