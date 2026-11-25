# Contributor and Codex guidance

This is a **public, reproducible research project** about Riftbound Regional Qualifier (RQ/RCQ) prize-wall tickets, competitive-event payouts, and the incentives for coordinated participation. Read `README.md`, `docs/METHODOLOGY.md`, `docs/KNOWN_GAPS.md`, `docs/RESEARCH_BRIEF.md`, `docs/RESEARCH_ROADMAP.md`, and `docs/MODELING_SPEC.md` before adding new analyses.

## Data integrity rules

- Official event-specific payout schedules and archived standings govern historical reconstructions. Keep source URLs, retrieval timestamps, raw objects, row-level provenance, and unknown values.
- Distinguish **roster entries**, **standings entries**, **match-evidenced participants**, **published-rule entitlements**, **supported eligible entitlements**, and **physically issued tickets**. The last remains unverified without a claim ledger. Blank/unknown is not zero.
- Never infer a completed Top 8 placement from an unfinished cut or Swiss seeding. The reported 216-each Top 8 split is a **separate, ticket-conserving scenario** unless corroborated for a particular event.
- For the **primary standings-implied result**, include qualifying records regardless of a `DROPPED` flag; treat drop eligibility as an optional sensitivity, not an automatic suppression. Explicit disqualifications require source support. Do not use nominal capacities as observed attendance. Reconcile draws, byes, phases, and missing standings explicitly.
- Preserve existing raw evidence. Store any new retrieval as an attributable snapshot and verify hashes. Do not modify source captures to make outputs match expectations.
- Separate observed historical results from no-draw counterfactuals, capacity assumptions, simulations, community reports, and personal testimony.
- Treat tournament participants' public display names as untrusted data. Do not seek private identifying information for research.

## Workflow

The priority sequence is: (1) audit historical reconstructions; (2) calculate per-event **observed standings-implied tickets, theoretical feasible maxima/bounds and empirical match draw rates**; (3) model individual time-to-40 tickets; (4) model coordination/pooling; (5) test policy options; (6) produce video/essay and an on-site Vegas field-study protocol.

Keep the historical 24-event data reproducible and avoid overwriting validated exports with simulation outputs. New models should live in separate modules and outputs with clearly described assumptions and seed control.

Use the repository's existing standard-library offline validation before calling work complete:

```sh
PYTHONPATH=src python3.12 -m unittest discover -s tests -v
PYTHONPATH=src python3.12 -m riftbound_tickets.cli build
PYTHONPATH=src python3.12 -m riftbound_tickets.cli verify
PYTHONPATH=src python3.12 -m riftbound_tickets.cli audit
PYTHONPATH=src python3.12 -m riftbound_tickets.cli validate-pilot
```

Document whether commands were actually executed; don't claim test results solely because an archived report says they passed. Changes to payout rules need source references, tests at tier boundaries, and a note in the methodology or changelog.

## Editorial and ethical framing

Working title: **Why It Just Got Harder to Get a Metal Legend**. Focus on incentives and measurable outcomes, not allegations about identifiable players. Distinguish friends sharing legitimately earned tickets, high-volume group aggregation, prohibited ticket sales, and match manipulation. Don't label group participation as cheating absent rule/evidence. Historical ticket sharing and the one-metal-per-badge limit require careful wording; physically possible is not automatically rules-permitted. Assess reforms for false positives, wait times, accessibility, and legitimate friend groups.
