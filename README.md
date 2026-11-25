# Riftbound ticket economy

Reproducible research on the Friday Pre-Regional Challenge, Super Saturday
Standard Challenge, and Sunday Regional Rebound at the 2026 Atlanta, Sydney,
Vancouver, Utrecht, Hartford, Barcelona, Singapore, and Los Angeles Regional
Qualifiers.

The repository preserves official public standings, separate rosters, explicit
bye/match evidence, and each city's historical payout tables. It reconstructs
published ticket entitlements. **Actual physical ticket issuance is unverified:**
no claim/distribution ledger was recovered, so verified-issuance fields are blank.

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
src/riftbound_tickets/models/    Reserved; no simulation
src/riftbound_tickets/charts/    Reserved for figures
tests/                         Unit tests and archived pilot regression checks
notebooks/                     Exploration guidance
outputs/tables/                Event summaries, distributions, and issue ledger
outputs/figures/                Reserved for figures
docs/                          Method, field definitions, sources, and gaps
```

Read [the methodology](docs/METHODOLOGY.md) and
[data dictionary](docs/DATA_DICTIONARY.md) before interpreting the outputs.
No Monte Carlo simulation or video scripting has been started.
