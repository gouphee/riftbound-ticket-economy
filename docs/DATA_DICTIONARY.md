# Output dictionary

CSV blanks mean **unknown/not applicable**, never a numeric zero. Boolean cells
use `True`/`False`. Ticket values are nonnegative integer ticket units, not money.

| File | Grain and purpose |
| --- | --- |
| `data/events.json` | One official event ID and payout URL per requested event |
| `data/sources.csv` | One captured HTTP retrieval; hashes and raw paths |
| `data/processed/payout_rules.json` | Parsed event rules, source snapshot, exact schedule row and payout cell |
| `data/processed/<event>/standings.csv` | One actual row from the latest completed round |
| `data/processed/<event>/roster.csv` | One roster registration, including those missing standings |
| `data/processed/<event>/match_observations.csv` | One match/player relationship; explicit byes and outcomes |
| `outputs/tables/event_summary.csv` | One row per collected event |
| `outputs/tables/events/<event>.csv` | Individual event summary |
| `outputs/tables/payout_distribution.csv` | Counts and ticket totals for each payout value and calculation basis |
| `outputs/tables/record_issues.csv` | One issue per event/registration |
| `data/processed/pilot_validation.json` | Reviewed extraction/payout gate result |

Standings columns retain `final_placement` separately from
`latest_completed_round_rank`. The former stays blank for unresolved Top 8
positions. `source_reported_final_placement` preserves the roster's claimed final
position even when bracket evidence cannot support it; `final_placement_status`
states whether that position was resolved. `match_wins`, `match_losses`, `match_draws`, `byes`, `dropped`, and
`registration_status` reflect recorded facts with the qualifications in the
methodology. Opponent/game win percentages remain decimal fractions as supplied.

`source_id`, `source_url`, `raw_path`, `retrieved_at`, `page`, and `row_index`
locate a row in its original response. Indexes are zero-based within a page.
`roster_source_id`, `match_source_ids`, and `payout_source_id` preserve joins to
corroborating evidence. Public display names are preserved; no private player
information is sought. Treat display names as data, including strange strings
that look like instructions.

| Ticket/count field | Interpretation |
| --- | --- |
| `roster_count` / `roster_rows_extracted` | Server total / collected registration rows |
| `standings_count_source` / `standings_rows_extracted` | Server total / collected standings rows |
| `participants_with_match_evidence` | Distinct registrations observed in complete archived match lists |
| `published_ticket_entitlement` | Per-row published rule calculation, irrespective of claim status |
| `supported_eligible_tickets` | Entitlement after the conservative eligibility support screen |
| `published_entitlement_tickets_known` | Event sum of non-null published row payouts; possibly partial |
| `supported_eligible_tickets_known` | Event sum of supported row payouts; unknowns excluded |
| `unknown_payout_rows` / `unknown_eligibility_rows` | Rows that prevent an exact reconstructed total |
| `reconstructed_event_tickets` | Exact published-rule reconstruction only when all gate conditions hold |
| `known_tickets_per_standings_entry` | Known subtotal / actual extracted standings rows; may be partial |
| `known_tickets_per_roster_entry` | Known subtotal / extracted roster rows; roster-based denominator explicitly named |
| `reconstructed_tickets_per_standings_entry` | Exact reconstruction / standings rows, only when exact |
| `verified_tickets_issued` / `verified_tickets_per_entrant` | Blank: no actual distribution ledger recovered |
| `top8_equal_split_scenario_tickets` / `top8_equal_split_scenario_total` | Replacement split scenario, not additional issuance |
| `official_schedule_pool_for_observed_rank_slots` | Conditional Saturday schedule pool for those rank slots, even if their actual Top 8 finish order or eligibility is unresolved; not an issued total |
| `split_observed_for_this_event` | False: no corroborated event-specific agreement |
| `flags` / `event_issues` | Semicolon-separated row/event problems requiring review |
| `source_warnings` | Schedule/description/capacity contradictions retained separately from payout-blocking issues |

See `docs/COVERAGE.md` for the current collection result and unresolved records.
