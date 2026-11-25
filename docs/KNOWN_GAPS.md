# Known gaps and decisions

The 2026-11-24 research run recovered **20,651 standings rows across all 24
requested events**, against **20,652 roster rows**. Every published API standings
page was retrieved and reconciled to its own response total. No event's
registration count was substituted for standings.

## Atlanta Friday: one roster-only entry

Official event 511646 has 1,020 roster rows but 1,019 final-round standings rows.
Registration 3084340 has no final placement, a roster-recorded 0-0-0, and a
registration-completed timestamp on the following day. These are observations,
not proof of nonparticipation or eligibility. It remains in `roster.csv` only.
The last actual standings row separately has a recorded 0-0-0. Match evidence
establishes 1,018 distinct participants. The available standings imply 9,432
tickets; an exact event-wide total remains withheld.

## Utrecht: records recovered, payout certainty limited

- Friday 663545: 1,525 standings and roster rows. One prize-level dropped
  registration has unresolved eligibility.
- Saturday 667933: 505 standings and roster rows. Four quarterfinal matches
  exist, but three have no winner or explicit draw result. Semifinal and final
  match endpoints return zero matches even though the rounds are marked complete.
  Six match records cannot be independently replayed; seven Top 8 individual
  payouts remain unknown. The one explicitly recorded quarterfinal loser has a
  supported 5th–8th placement tier. Five other prize-level drops remain unresolved.
- Sunday 668004: 1,006 standings and roster rows. **268 prize-level records are
  marked dropped**, including some six-win players. There is no drop timestamp
  or claim ledger establishing whether this happened before or after prizes.
  Do not delete these players, turn them into nonparticipants, deny them prizes,
  or assume they received tickets. Both the published-record calculation and
  the conservative eligibility screen remain visible.

Thus Utrecht is included as recovered historical evidence, with explicit
qualification of bracket and eligibility claims. No records were synthesized.

## Other incomplete Saturday brackets

| Event | Observed bracket | Treatment |
| --- | --- | --- |
| Vancouver 613450 | All three cut rounds marked complete; zero cut matches | Eight individual Top 8 official payouts unknown |
| Singapore 891984 | Quarterfinals played; no later completed match evidence | Four remaining individual payouts unknown; quarterfinal losers' 144-ticket tier supported |
| Los Angeles 892222 | Latest completed standings are Swiss Round 7; cut unfinished | Eight individual Top 8 official payouts unknown |

The 4,992-ticket published rank-slot pool and the 216-each Top 8 split scenario
are separately calculable. These facts do **not** establish an actual split
agreement, physical issuance, or an official champion finish for a Swiss seed.

## Other record and source contradictions

- Hartford Friday 683274 has one standings record with no matching round-match
  observation despite complete archived match lists. Its payout is left unknown;
  the observed record remains intact. Two other prize-level drop records have
  unknown eligibility.
- Singapore Friday 889707 declares five rounds in its published payout schedule
  but exposes six completed rounds. The extra round has no matches. Observed
  five-round records can be evaluated under the table; the contradictory event
  metadata prevents an exact validated event total. No six-win payout is invented.
- Sydney Friday's description says five rounds and prizes at the end of Round
  6. The completed five-round standings and explicit five-win schedule table
  govern the calculation; the conflicting sentence is retained as a warning.
- Several advertised caps disagree with metadata or are exceeded by roster
  counts. Caps never replace actual extracted row counts or determine payouts.
- Other prize-level dropped records occur at Sydney, Vancouver, Hartford,
  Barcelona, Singapore, and Los Angeles. Full details and counts are generated in
  `COVERAGE.md` and `outputs/tables/record_issues.csv`.

## Physical issuance, splits, and historical policy

No official claim/distribution ledger was recovered. All verified-issuance and
verified-per-entrant fields therefore remain null, not zero. “Supported eligible”
is a transparent screening convention, not an organizer ruling.

The user's brief and a community web-search excerpt describe the 216-ticket
practice, but no agreement specific to any scoped event has been verified.
The direct Reddit HTTP response was a JavaScript challenge despite status 200;
it is retained as an unsuccessful content retrieval, not as corroborating HTML.

The original official tournament-policy PDF retained here says 2026-03-30 on its
first page. A July edition was located through a secondary index, but its
original PDF and complete event-by-event revision applicability were not
verified. Event-specific official payout schedules own the ticket calculations;
no universal historical eligibility policy is inferred from one revision.

To resolve the remaining issuance questions, useful additional evidence would
be organizer prize-claim records, contemporaneous event-specific split
agreements, drop timing, or a corrected official bracket export. This repository
does not contact players or organizers, or start simulations, on its own.
