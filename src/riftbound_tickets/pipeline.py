"""Normalize archived observations and export conservative ticket reconstructions."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.locator import read_collection
from .collectors.schedules import schedule_rule
from .payouts.rules import saturday_placement, saturday_top8_split, win_record_payout


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def provenance(wrapped: dict, prefix: str = "") -> dict:
    return {prefix + key: wrapped.get(key) for key in ("source_id", "source_url", "raw_path", "retrieved_at", "page", "row_index")}


def match_audit(collection: dict) -> tuple[dict, list[dict], list[str]]:
    records = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "byes": 0, "played": 0, "issues": [], "sources": set()})
    observations, issues = [], []
    for group in collection["match_sets"]:
        issues.extend(f"matches_round_{group['round_number']}:{x}" for x in group["issues"])
        seen = set()
        for wrapped in group["rows"]:
            match = wrapped["row"]
            relationships = match.get("player_match_relationships", [])
            for relationship in relationships:
                status = relationship.get("user_event_status") or {}
                registration_id = status.get("id")
                player_id = (relationship.get("player") or {}).get("id")
                if registration_id is None:
                    issues.append(f"match_{match['id']}_missing_registration")
                    continue
                rec = records[registration_id]
                rec["sources"].add(wrapped["source_id"])
                if registration_id in seen:
                    rec["issues"].append("duplicate_round_match")
                seen.add(registration_id)
                outcome = None
                if match.get("status") != "COMPLETE" or match.get("reports_are_in_conflict"):
                    rec["issues"].append("incomplete_or_conflicted_match")
                elif match.get("match_is_bye"):
                    outcome = "win"
                    rec["byes"] += 1
                elif match.get("match_is_intentional_draw") or match.get("match_is_unintentional_draw"):
                    outcome = "draw"
                elif match.get("winning_player") is not None:
                    outcome = "win" if match["winning_player"] == player_id else "loss"
                elif match.get("match_is_loss"):
                    outcome = "loss"
                else:
                    rec["issues"].append("unresolved_match_outcome")
                rec["played"] += 1
                if outcome:
                    rec[{"win": "wins", "loss": "losses", "draw": "draws"}[outcome]] += 1
                observations.append({"event_key": collection["event_key"], "round_id": group["round_id"],
                                     "round_number": group["round_number"], "phase_type": group["phase_type"],
                                     "match_id": match["id"], "registration_id": registration_id, "player_id": player_id,
                                     "outcome": outcome, "explicit_bye": match.get("match_is_bye"),
                                     "ghost_match": match.get("is_ghost_match"), "match_status": match.get("status"),
                                     **provenance(wrapped)})
    return dict(records), observations, issues


def normalize(collection: dict, rule: dict, payout_source: dict) -> tuple[list, list, list, dict, list]:
    spec, meta = collection["spec"], collection["metadata"]
    event_key, event_type = spec["event_key"], spec["event_type"]
    source_warnings = []
    published_capacity = rule.get("published_capacity")
    if published_capacity and meta.get("capacity") and published_capacity != meta["capacity"]:
        source_warnings.append("metadata_capacity_differs_from_schedule")
    if published_capacity and (collection["roster"]["expected_count"] or 0) > published_capacity:
        source_warnings.append("roster_count_exceeds_published_capacity")
    description_rounds = re.findall(r"(\d+) Rounds\.", meta.get("description", ""))
    if description_rounds and int(description_rounds[0]) != rule["rounds"]:
        source_warnings.append("event_description_round_limit_differs_from_schedule")
    prize_rounds = re.findall(r"Prizes are awarded (?:by|at) the end of Round (\d+)", meta.get("description", ""))
    if event_type != "saturday" and prize_rounds and int(prize_rounds[0]) != rule["rounds"]:
        source_warnings.append("event_description_prize_round_differs_from_published_round_limit")
    issues = [f"standings:{s}" for s in collection["standings"]["issues"]]
    issues += [f"roster:{s}" for s in collection["roster"]["issues"]]
    matches, match_rows, match_issues = match_audit(collection)
    issues += match_issues
    all_match_pages = bool(collection["match_sets"]) and all(g["complete"] for g in collection["match_sets"])
    phases = sorted(meta["tournament_phases"], key=lambda x: x["order_in_phases"])
    swiss = [p for p in phases if p["round_type"] == "SWISS"]
    cuts = [p for p in phases if p["round_type"] != "SWISS"]
    completed_rounds = [r for p in phases for r in p["rounds"] if r["status"] == "COMPLETE"]
    event_finished = meta["settings"]["event_lifecycle_status"] == "EVENT_FINISHED"
    scheduled_complete = bool(phases) and all(p["status"] == "COMPLETE" and p["rounds"] and all(r["status"] == "COMPLETE" for r in p["rounds"]) for p in phases)
    final_order_resolved = event_finished and scheduled_complete
    if not event_finished:
        issues.append("event_not_marked_finished")
    if not scheduled_complete:
        issues.append("scheduled_phases_or_rounds_incomplete")
    if event_type == "saturday" and not cuts:
        final_order_resolved = False
        issues.append("published_top_cut_missing")
    quarterfinal_losers = set()
    if event_type == "saturday":
        cut_groups = [g for g in collection["match_sets"] if g["phase_type"] != "SWISS"]
        if len(cut_groups) != 3:
            issues.append("top_cut_match_coverage_incomplete")
            final_order_resolved = False
        for index, group in enumerate(cut_groups):
            expected_matches = 4 // (2 ** index)
            if not group["complete"] or len(group["rows"]) != expected_matches:
                issues.append(f"top_cut_round_{group['round_number']}_match_count:{len(group['rows'])}!={expected_matches}")
                final_order_resolved = False
        unresolved_cut = [r for r in match_rows if r["phase_type"] != "SWISS" and r["outcome"] is None]
        if unresolved_cut:
            issues.append("top_cut_matches_without_resolved_outcomes")
            final_order_resolved = False
        if cut_groups:
            quarterfinal_losers = {r["registration_id"] for r in match_rows if r["round_id"] == cut_groups[0]["round_id"] and r["outcome"] == "loss"}
    if event_type != "saturday":
        swiss_rounds = [r for p in swiss for r in p["rounds"] if r["status"] == "COMPLETE"]
        if len(swiss_rounds) != rule["rounds"]:
            issues.append(f"published_round_limit_disagrees:{len(swiss_rounds)}!={rule['rounds']}")
            final_order_resolved = False
    roster_by_id = {w["row"]["id"]: w for w in collection["roster"]["rows"]}
    standing_ids = {w["row"]["user_event_status"]["id"] for w in collection["standings"]["rows"] if w["row"].get("user_event_status")}
    missing_ids = sorted(set(roster_by_id) - standing_ids)
    extra_ids = sorted(standing_ids - set(roster_by_id))
    if missing_ids:
        issues.append(f"roster_entries_without_standings:{len(missing_ids)}")
    if extra_ids:
        issues.append(f"standings_entries_without_roster:{len(extra_ids)}")
    if meta.get("starting_player_count") != collection["roster"]["expected_count"]:
        issues.append("starting_player_count_disagrees_with_roster")
    normalized, roster_rows, row_issues = [], [], []
    for wrapped in collection["roster"]["rows"]:
        r = wrapped["row"]
        roster_rows.append({"event_key": event_key, "registration_id": r["id"], "player_id": (r.get("user") or {}).get("id"),
                            "player_name": r.get("best_identifier"), "registration_status": r.get("registration_status"),
                            "roster_recorded_wins": r.get("matches_won"), "roster_recorded_losses": r.get("matches_lost"),
                            "roster_recorded_draws": r.get("matches_drawn"), "roster_recorded_final_placement": r.get("final_place_in_standings"),
                            "has_standings_row": r["id"] in standing_ids, "has_match_observation": r["id"] in matches,
                            "registration_completed_datetime": r.get("registration_completed_datetime"), **provenance(wrapped)})
    ranks = []
    for wrapped in collection["standings"]["rows"]:
        raw = wrapped["row"]
        status = raw.get("user_event_status") or {}
        reg_id, rank = status.get("id"), raw.get("rank")
        player_id = (raw.get("player") or {}).get("id")
        ranks.append(rank)
        record = raw.get("match_record")
        record_match = re.fullmatch(r"(\d+)-(\d+)-(\d+)", record or "")
        wins, losses, draws = (tuple(map(int, record_match.groups())) if record_match else (None, None, None))
        flags = []
        if not record_match:
            flags.append("missing_or_unparseable_match_record")
        if (wins, losses, draws) != tuple(status.get(k) for k in ("matches_won", "matches_lost", "matches_drawn")):
            flags.append("standing_record_disagrees_with_status")
        reg_wrap = roster_by_id.get(reg_id)
        reg = reg_wrap["row"] if reg_wrap else {}
        if reg_wrap and (wins, losses, draws) != tuple(reg.get(k) for k in ("matches_won", "matches_lost", "matches_drawn")):
            flags.append("standing_record_disagrees_with_roster")
        if reg_wrap and reg.get("final_place_in_standings") not in (None, rank):
            flags.append("standing_rank_disagrees_with_roster")
        if raw.get("round_number") != collection["selected_round_number"]:
            flags.append("standing_round_disagrees")
        if wins is not None and raw.get("match_points") != 3 * wins + draws:
            flags.append("standing_points_disagree")
        audit = matches.get(reg_id)
        if all_match_pages and audit:
            if (wins, losses, draws) != (audit["wins"], audit["losses"], audit["draws"]):
                flags.append("standing_record_disagrees_with_match_history")
            flags += audit["issues"]
        elif all_match_pages and wins is not None and wins + losses + draws:
            flags.append("record_without_match_observation")
        # Swiss seeds do not determine the 1st/2nd/3rd/5th ticket tiers.
        final_placement = rank if final_order_resolved else None
        if event_type == "saturday" and rank and rank > 8 and swiss and swiss[-1]["status"] == "COMPLETE":
            final_placement = rank
        if event_type == "saturday" and not final_order_resolved and 5 <= (rank or 0) <= 8 and status.get("registration_status") == "ELIMINATED" and reg_id in quarterfinal_losers:
            final_placement = rank
        if event_type == "saturday":
            award = saturday_placement(final_placement)
            scenario_award = saturday_top8_split(rank)
        else:
            award = win_record_payout(wins, losses, draws, rounds=rule["rounds"], table={int(k): v for k, v in rule["win_tickets"].items()})
            scenario_award = None
        record_conflict = any(x in flags for x in (
            "standing_record_disagrees_with_status", "standing_record_disagrees_with_roster",
            "missing_or_unparseable_match_record", "standing_rank_disagrees_with_roster",
            "standing_round_disagrees", "standing_points_disagree",
            "standing_record_disagrees_with_match_history", "record_without_match_observation",
            "unresolved_match_outcome", "incomplete_or_conflicted_match", "duplicate_round_match"))
        if record_conflict:
            award = None
        eligibility = "unknown"
        eligible_award = None
        if award == 0:
            eligibility, eligible_award = "no_ticket_entitlement", 0
        elif award is not None:
            status_ok = status.get("registration_status") in ("COMPLETE", "ELIMINATED")
            record_complete = wins is not None and (event_type == "saturday" or wins + losses + draws == rule["rounds"])
            if status_ok and record_complete:
                eligibility, eligible_award = "supported_by_final_record_and_status", award
            else:
                eligibility = "unknown_drop_or_short_record"
        if award is None:
            flags.append("published_payout_unresolved")
        if award and eligible_award is None:
            flags.append("prize_eligibility_unresolved")
        byes = audit["byes"] if all_match_pages and audit else None
        # A zero is justified only by complete match coverage for that player.
        if all_match_pages and audit is None and wins == losses == draws == 0:
            byes = 0
        row = {"event_key": event_key, "official_event_id": spec["official_event_id"], "registration_id": reg_id,
               "player_id": player_id, "player_name": status.get("best_identifier"), "final_placement": final_placement,
               "source_reported_final_placement": reg.get("final_place_in_standings"),
               "final_placement_status": "resolved_from_archived_results" if final_placement is not None else "unresolved_phase_or_bracket",
               "latest_completed_round_rank": rank, "round_id": collection["selected_round_id"], "round_number": raw.get("round_number"),
               "match_record": record, "match_wins": wins, "match_losses": losses, "match_draws": draws,
               "match_points": raw.get("match_points"), "byes": byes, "bye_evidence_status": "complete_match_coverage" if all_match_pages else "unknown_incomplete_match_coverage",
               "registration_status": status.get("registration_status"), "dropped": True if status.get("registration_status") == "DROPPED" else False if status.get("registration_status") in ("COMPLETE", "ELIMINATED") else None,
               "observed_match_count": audit["played"] if audit else 0 if all_match_pages else None,
               "opponent_match_win_percentage": raw.get("opponent_match_win_percentage"), "game_win_percentage": raw.get("game_win_percentage"),
               "opponent_game_win_percentage": raw.get("opponent_game_win_percentage"),
               "published_ticket_entitlement": award, "eligibility_status": eligibility, "supported_eligible_tickets": eligible_award,
               "verified_tickets_issued": None, "issuance_evidence_status": "not_observed_no_claim_ledger",
               "top8_equal_split_scenario_tickets": scenario_award,
               "split_observed_for_this_event": False if event_type == "saturday" else None,
               "flags": ";".join(sorted(set(flags))), **provenance(wrapped),
               "roster_source_id": reg_wrap["source_id"] if reg_wrap else None,
               "payout_source_id": payout_source["source_id"], "payout_source_url": payout_source["url"],
               "match_source_ids": ";".join(sorted(audit["sources"])) if audit else ""}
        normalized.append(row)
        row_issues.extend({"event_key": event_key, "registration_id": reg_id, "issue": f} for f in sorted(set(flags)))
    if len(set(ranks)) != len(ranks) or set(ranks) != set(range(1, len(ranks) + 1)):
        issues.append("noncontiguous_or_duplicate_standings_ranks")
    unknown_payouts = sum(r["published_ticket_entitlement"] is None for r in normalized)
    unknown_eligibility = sum(r["published_ticket_entitlement"] not in (None, 0) and r["supported_eligible_tickets"] is None for r in normalized)
    exact = bool(normalized) and not issues and not row_issues and not unknown_payouts and not unknown_eligibility and final_order_resolved
    known = sum(r["published_ticket_entitlement"] or 0 for r in normalized)
    eligible_known = sum(r["supported_eligible_tickets"] or 0 for r in normalized)
    observed_participants = len(matches) if all_match_pages else None
    summary = {"event_key": event_key, "city": spec["city"], "event_type": event_type, "official_event_id": spec["official_event_id"],
               "event_name": meta["name"], "start_datetime_source": meta["start_datetime"],
               "roster_count": collection["roster"]["expected_count"], "roster_rows_extracted": len(roster_rows),
               "published_capacity": published_capacity, "metadata_capacity_source": meta.get("capacity"),
               "starting_player_count_source": meta.get("starting_player_count"), "registered_user_count_source": meta.get("registered_user_count"),
               "standings_count_source": collection["standings"]["expected_count"], "standings_rows_extracted": len(normalized),
               "participants_with_match_evidence": observed_participants,
               "roster_only_rows": len(missing_ids), "standings_only_rows": len(extra_ids),
               "standings_pagination_complete": collection["standings"]["complete"], "roster_pagination_complete": collection["roster"]["complete"],
               "match_pagination_complete": all_match_pages, "published_round_limit": rule["rounds"],
               "latest_completed_round": collection["selected_round_number"], "final_order_resolved": final_order_resolved,
               "published_entitlement_tickets_known": known, "supported_eligible_tickets_known": eligible_known,
               "unknown_payout_rows": unknown_payouts, "unknown_eligibility_rows": unknown_eligibility,
               "reconstructed_event_tickets": known if exact else None,
               "reconstruction_status": "validated_published_entitlement" if exact else "partial_or_inconsistent_evidence",
               "verified_tickets_issued": None, "verified_tickets_per_entrant": None,
               "issuance_status": "not_observed_no_claim_ledger",
               "reconstructed_tickets_per_standings_entry": round(known / len(normalized), 8) if exact else None,
               "known_tickets_per_standings_entry": round(known / len(normalized), 8) if normalized else None,
               "known_tickets_per_roster_entry": round(known / len(roster_rows), 8) if roster_rows else None,
               "top8_equal_split_scenario_total": sum(r["top8_equal_split_scenario_tickets"] or 0 for r in normalized) if event_type == "saturday" and normalized else None,
               "official_schedule_pool_for_observed_rank_slots": sum(saturday_placement(r) for r in ranks) if event_type == "saturday" and all(type(r) is int and r > 0 for r in ranks) else None,
               "split_observed_for_this_event": False if event_type == "saturday" else None,
               "row_issue_count": len(row_issues), "event_issues": ";".join(sorted(set(issues))),
               "source_warnings": ";".join(source_warnings),
               "standings_url": f"https://locator.riftbound.uvsgames.com/events/{spec['official_event_id']}",
               "payout_source_url": payout_source["url"], "payout_source_id": payout_source["source_id"]}
    for missing_id in missing_ids:
        row_issues.append({"event_key": event_key, "registration_id": missing_id, "issue": "roster_entry_without_final_standings_row"})
    return normalized, roster_rows, match_rows, summary, row_issues


def build(root: Path, keys: list[str] | None = None) -> list[dict]:
    store = EvidenceStore(root)
    specs = json.loads((root / "data" / "events.json").read_text())
    summaries, distributions, all_issues, rule_catalog = [], [], [], []
    used_source_ids = set()
    for spec in specs:
        key = spec["event_key"]
        if keys and key not in keys:
            continue
        try:
            collection = read_collection(root, key)
        except FileNotFoundError:
            continue
        # Rebuild is strictly offline; no silently refreshed payout evidence.
        retrievals = [json.loads(line) for line in store.ledger.read_text().splitlines()]
        source = next((r for r in reversed(retrievals) if r["url"] == spec["payout_url"] and r["http_status"] == 200), None)
        if not source:
            raise ValueError(f"No archived payout source: {key}")
        rule = schedule_rule(store.read(source).decode(), spec["event_type"])
        used_source_ids.update((source["source_id"], collection["metadata_source"]["source_id"]))
        for group in [collection["standings"], collection["roster"], *collection["match_sets"]]:
            used_source_ids.update(page["source"]["source_id"] for page in group["pages"])
        normalized, roster, matches, summary, issues = normalize(collection, rule, source)
        summaries.append(summary)
        all_issues.extend(issues)
        rule_catalog.append({"event_key": key, "source": source, **rule})
        out = root / "data" / "processed" / key
        write_csv(out / "standings.csv", normalized)
        write_csv(out / "roster.csv", roster)
        write_csv(out / "match_observations.csv", matches)
        write_csv(root / "outputs" / "tables" / "events" / (key + ".csv"), [summary])
        event_distribution_start = len(distributions)
        for metric in ("published_ticket_entitlement", "supported_eligible_tickets", "top8_equal_split_scenario_tickets"):
            if metric.startswith("top8") and spec["event_type"] != "saturday":
                continue
            counts = Counter(row[metric] for row in normalized)
            for ticket, count in sorted(counts.items(), key=lambda kv: -1 if kv[0] is None else kv[0]):
                distributions.append({"event_key": key, "basis": metric, "tickets_per_player": ticket,
                                      "player_rows": count, "tickets_total": ticket * count if ticket is not None else None,
                                      "evidence_class": "scenario_event_agreement_unverified" if metric.startswith("top8") else "reconstructed_published_entitlement"})
        write_csv(root / "outputs" / "tables" / "events" / (key + "-distribution.csv"), distributions[event_distribution_start:])
    write_csv(root / "outputs" / "tables" / "event_summary.csv", summaries)
    write_csv(root / "outputs" / "tables" / "payout_distribution.csv", distributions)
    write_csv(root / "outputs" / "tables" / "record_issues.csv", all_issues, ["event_key", "registration_id", "issue"])
    (root / "data" / "processed" / "payout_rules.json").write_text(json.dumps(rule_catalog, indent=2, ensure_ascii=False) + "\n")
    sources = [json.loads(line) for line in store.ledger.read_text().splitlines()]
    fields = ["source_id", "category", "url", "final_url", "retrieved_at", "http_status", "content_type", "sha256", "raw_path", "storage_encoding", "error", "used_in_normalization", "verification_status"]
    source_rows = []
    for source in sources:
        row = {k: source.get(k) for k in fields}
        row["used_in_normalization"] = source["source_id"] in used_source_ids
        row["verification_status"] = "raw_hash_and_data_schema_checked_see_event_flags" if row["used_in_normalization"] else "retained_discovery_or_context_not_used_in_calculations"
        if source["category"] == "community_split_report":
            row["verification_status"] = "challenge_page_not_post_contents_http_200_not_content_success"
        if source["http_status"] != 200:
            row["verification_status"] = "retrieval_failed_not_evidence_of_empty_results"
        source_rows.append(row)
    write_csv(root / "data" / "sources.csv", source_rows, fields)
    write_research_indexes(root, summaries, sources)
    return summaries


def write_research_indexes(root: Path, summaries: list[dict], sources: list[dict]):
    """Generate source-linked coverage from the same event summary rows."""
    lines = ["# Collection coverage", "", "Generated by the offline build from the archived snapshots.", "",
             "Known tickets are published-rule subtotals, not verified issuance. Blank exact totals remain unknown.", "",
             "| Event | Official ID | Roster | Standings | Match participants | Known tickets | Unknown payout / eligibility rows | Exact reconstruction |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for s in summaries:
        lines.append(f"| {s['event_key']} | [{s['official_event_id']}]({s['standings_url']}) | {s['roster_rows_extracted']} | {s['standings_rows_extracted']} | {s['participants_with_match_evidence']} | {s['published_entitlement_tickets_known']:,} | {s['unknown_payout_rows']} / {s['unknown_eligibility_rows']} | {'yes' if s['reconstructed_event_tickets'] is not None else 'withheld'} |")
    lines += ["", "## Event issues and source contradictions", ""]
    for s in summaries:
        details = []
        if s['event_issues']:
            details.append(s['event_issues'])
        if s['row_issue_count']:
            details.append(f"{s['row_issue_count']} standings-row flags; see record_issues.csv")
        if s['source_warnings']:
            details.append("source warnings: " + s['source_warnings'])
        if details:
            lines.append(f"- **{s['event_key']}**: {'; '.join(details)}.")
    lines += ["", "Utrecht's three official row sets were recovered; its payout/eligibility contradictions remain explicit.",
              "See [known gaps](KNOWN_GAPS.md), [methodology](METHODOLOGY.md), and [field definitions](DATA_DICTIONARY.md).", ""]
    (root / "docs" / "COVERAGE.md").write_text("\n".join(lines))
    lines = ["# Source guide", "", "All primary responses and exact retrieval timestamps are indexed in `data/sources.csv` and the raw JSONL ledger.", "",
             "## Official event and payout sources", "",
             "| Event | Official standings page | Published payout schedule | Latest completed round |",
             "| --- | --- | --- | ---: |"]
    for s in summaries:
        lines.append(f"| {s['event_key']} | [{s['official_event_id']}]({s['standings_url']}) | [{s['city']}]({s['payout_source_url']}) | {s['latest_completed_round']} |")
    lines += ["", "The public API base is `https://api.cloudflare.riftbound.uvsgames.com/hydraproxy/api/v2`.",
              "Read-only routes used: `/events/{id}/`, `/events/{id}/registrations/`,",
              "`/tournament-rounds/{round_id}/standings/paginated/`, and `/tournament-rounds/{round_id}/matches/paginated/`.",
              "Page-specific URLs, raw response hashes, and row pointers are preserved in the CSVs.", "", "## Historical policy and secondary leads", ""]
    seen = set()
    for source in sources:
        if source['category'] in ('historical_tournament_rules', 'historical_rules_discovery', 'community_split_report', 'discovery') and source['url'] not in seen:
            seen.add(source['url'])
            lines.append(f"- [{source['category']}]({source['url']}), retrieved {source['retrieved_at']}; raw `{source['raw_path']}`.")
    lines += ["", "The Reddit HTTP snapshot is a JavaScript challenge, not the post contents; its HTTP 200 is not successful content verification.",
              "The separately preserved web-search excerpt in `data/observations.json` corroborates only a reported split practice.",
              "Third-party sites were discovery leads; official standings/payout sources own all normalized calculations.", ""]
    (root / "docs" / "SOURCES.md").write_text("\n".join(lines))
