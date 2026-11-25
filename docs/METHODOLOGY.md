# Evidence and calculation method

The official organizer calls these events **Regional Qualifiers (RQs)**. This
repository covers the three requested flagship side events at eight 2026 RQs;
it does not include main-event cash prizes or other side events.

## Source hierarchy

1. Official event metadata and completed-round standings from the UVS public
   locator/API establish event identity, round state, ranks, and match records.
2. Official schedule tables establish that city's historical ticket payouts.
   Event descriptions are retained for corroboration and contradictions.
3. Official round match observations establish byes and independently replay
   match wins, losses, and draws. No match result is inferred from points.
4. Official roster rows are collected separately for reconciliation. Neither a
   roster count nor a roster-only entry becomes a standings row.
5. Community reports and the user's brief establish reported practices only.
   They cannot replace official payouts or prove an event-specific split.

The rendered locator may display “No standings available” while its public API
still returns completed-round records. The collector uses the same read-only
public API routes found in the site's JavaScript. No credentials are required.
Technical discovery evidence is retained in the source ledger. No organizer,
registration, payment, or authenticated mutation endpoints are used.

## Collection and preservation

`data/events.json` is the explicit, reviewed 24-event identifier registry.
Each event is checked against both its ID and its official name. The collector
chooses the latest completed round in phase order, retaining every phase and
round state. “Final round” flags in the source are not consistently populated;
the code does not rely on them.

Every response is preserved under `data/raw/objects/`, with URL, UTC retrieval
timestamp, HTTP status, original SHA-256, selected HTTP headers, and storage
encoding in the append-only `data/raw/retrievals.jsonl`. Larger new captures are
gzip compressed losslessly; hashes identify the **decompressed response bytes**.
Earlier uncompressed captures remain intact. `data/sources.csv` is a convenient
flat index, not a replacement for the ledger. UTC captures can cross midnight
while the user's research date in America/Chicago remains November 24.

Pagination follows the server's `next_page_number` until a terminal page. It
checks count stability, current page, next-field agreement, repeated pages,
duplicate IDs, and extracted-row totals. The server can choose a page size
different from the requested size. An unavailable page produces a collection
issue and preserves preceding rows; it never becomes an empty successful page.

`data/interim/*.json.gz` records collection manifests and row copies. Offline
rebuilds replay every row from the raw response pages and require exact equality
with those copies. Raw evidence is authoritative. `verify` checks every object
against its recorded SHA-256. `--refresh` makes a new capture without deleting
old responses; rerun validation after a refresh, and compare the ledger.

## Records, participants, and eligibility

The standings `match_record` is parsed as match wins-losses-draws and checked
against status fields, roster recorded results, points, selected round, and
complete match history. Draws are never promoted to wins. Explicit bye matches
are counted separately; their credited wins are already in the record, so no
additional tickets are awarded. Incomplete match coverage leaves bye counts
unknown. Drops, eliminations, and zero-match rows remain visible.

Counts remain separate: advertised cap, source starting-player count,
source registered-user count, roster rows, standings rows, and participants
with explicit match evidence measure different things. There is no unqualified
`entrants` denominator. Match-evidence participants include an explicit awarded
bye and can differ from both roster and standings counts. Registration IDs are
the join key; display names are neither unique nor stable.

Published ticket entitlement is the amount obtained from an observed record or
resolved final placement and that event's published table. For win events,
unlisted valid win totals pay zero under the published schedule; invalid or
unknown records yield null. Records beyond the published round limit remain
unresolved rather than being capped. A flagged record/roster contradiction
suppresses that row's payout until reviewed.

`supported_eligible_tickets` requires a prize-level record, complete published
round count for Friday/Sunday, and a completed or eliminated source status.
A prize-level dropped or short record is explicitly unknown. This conservative
screen is **not an organizer eligibility ruling** and does not claim that other
restrictions or later sanctions have been audited. Zero-ticket results remain
zero regardless of eligibility.

There is no prize claim/distribution ledger. Therefore `verified_tickets_issued`
and `verified_tickets_per_entrant` are blank throughout. Exact reconstructed
event totals require reconciled rows, completed phases, no record issues, and
no unresolved payouts or eligibility. Other totals are clearly labeled known
subtotals; they must not be described as verified physical issuance. Scenarios
and inferred eligibility support are separated from observed standings facts.

## Saturday placement and the split

The published placement table pays 432, 288, 216, 144, 72, 48, 24, and 18 tickets
for 1st, 2nd, 3rd–4th, 5th–8th, 9th–16th, 17th–32nd, 33rd–64th, and 65th–128th.
Above 128th pays zero. A Swiss seed is not a final Top 8 placement. If a cut is
unfinished, unresolved Top 8 individual payouts remain null; resolved placements
below the cut, and eliminated quarterfinalists where supported, can still be used.

The Top 8 pool is 1,728 tickets. An equal split pays 216 each and conserves that
pool; it is a replacement distribution, never an extra payment. The full Top 128
schedule pool is 4,992 tickets. `data/observations.json` records the reported
practice and its evidence limits. No event-specific agreement has been verified,
so every split output remains a scenario, even if the bracket was left unfinished.
An unfinished bracket alone is not proof of a split.

## Historical tournament policy

The retained official PDF URL's search title suggests March 9, but its actual
first page says **Last Updated: 2026-03-30**. The content date takes precedence.
The original is indexed as `historical_tournament_rules` in the ledger. Relevant
sections are 414 (drops; pages 12–13), 701.2.d (disqualification and prizes;
page 31), and 704.5 (prize sharing; page 44). Page 44 was rendered and visually
checked. The document permits certain prize-sharing arrangements; that is not
evidence that one occurred. Later revisions/addenda may apply to later events;
this repository does not assert that this revision governed every city.

## Validation gate

The first reviewed pilot is Atlanta Friday and Atlanta Sunday. The manually
reviewed bins in `docs/pilot_reference.json` are independent checkpoints for the
computed distributions. Atlanta Friday's one roster-only registration is an
explicit accepted extraction gap, not a fabricated row or an exact event total.
The gate validates extraction of all available rows, record replay, pagination,
and payout arithmetic. It does not validate physical issuance.

`collect --scope all` reruns this gate before broader collection. Automated tests
cover historical changes, every placement boundary, draws, invalid/missing
records, pagination failures, duplicate IDs, dropped eligibility, unknown byes,
and unresolved Top 8 payouts. Test-only synthetic fixtures are confined to tests.
No Monte Carlo simulation or video scripting is included.
