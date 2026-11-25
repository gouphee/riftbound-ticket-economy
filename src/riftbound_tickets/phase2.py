"""Additive historical ticket generation, no-draw bounds, and draw-rate exports.

All observed rows replay from immutable archived sources. Counterfactual pairing
witnesses and figures have separate destinations. Legacy strict eligibility
exports are read as a sensitivity and never overwritten by this module.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.locator import LOCATOR, read_collection
from .collectors.schedules import schedule_rule
from .draws import classify_match, summarize_matches, unique_matches
from .models.historical_bounds import construct_no_draw_swiss, no_draw_upper_bound
from .payouts.historical import recorded_award, saturday_pool
from .payouts.rules import saturday_placement, saturday_top8_split
from .pipeline import provenance, write_csv


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _write_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _thresholds(awards: list[int | None], n: int) -> dict:
    return {"earning_entries": sum(a is not None and a > 0 for a in awards),
            "entries_at_least_40": sum(a is not None and a >= 40 for a in awards),
            "zero_award_entries": sum(a == 0 for a in awards),
            "unknown_award_entries": sum(a is None for a in awards),
            "earning_share": _rate(sum(a is not None and a > 0 for a in awards), n),
            "share_at_least_40": _rate(sum(a is not None and a >= 40 for a in awards), n),
            "zero_award_share": _rate(sum(a == 0 for a in awards), n)}


def _match_rows(collection: dict, spec: dict, rule: dict) -> tuple[list[dict], dict]:
    entries = unique_matches(collection)
    history = defaultdict(lambda: [0, 0, 0])
    uncertain_players = set()
    first_round = {}
    # Replay every phase before deciding which pre-round records are supported.
    for entry in entries:
        m = entry["match"]
        classification = classify_match(m, duplicate_conflict=entry["duplicate_conflict"])
        players = m.get("players") or []
        for player in players:
            first_round.setdefault(player, entry["round_number"])
        if entry["duplicate_conflict"] or m.get("reports_are_in_conflict") or m.get("status") != "COMPLETE":
            uncertain_players.update(players)
        elif m.get("match_is_bye"):
            if len(players) == 1:
                history[players[0]][0] += 1
            else:
                uncertain_players.update(players)
        elif m.get("match_is_loss"):
            for player in players:
                history[player][1] += 1
        elif classification["included_in_draw_denominator"]:
            for player in players:
                history[player][2 if classification["explicit_draw"] else 0 if player == m.get("winning_player") else 1] += 1
        else:
            uncertain_players.update(players)
    final = {}
    final_draw_credits, unknown_final_records = 0, 0
    for wrapped in collection["standings"]["rows"]:
        raw = wrapped["row"]
        match = re.fullmatch(r"(\d+)-(\d+)-(\d+)", raw.get("match_record") or "")
        player = (raw.get("player") or {}).get("id")
        if match and player is not None:
            final[player] = list(map(int, match.groups()))
            final_draw_credits += final[player][2]
        else:
            unknown_final_records += 1
    verified_history = {p for p in final if history[p] == final[p] and p not in uncertain_players and first_round.get(p) == 1}
    running = defaultdict(lambda: [0, 0, 0])
    rows, explicit_credits, cut_draws = [], 0, 0
    for entry in entries:
        m = entry["match"]
        classification = classify_match(m, duplicate_conflict=entry["duplicate_conflict"])
        players = m.get("players") or []
        source = entry["sources"][0]
        pre_records = ["-".join(map(str, running[p])) for p in players]
        bracket_supported = len(players) == 2 and all(p in verified_history for p in players)
        row = {"event_key": spec["event_key"], "official_event_id": spec["official_event_id"],
               "event_format": spec["event_type"], "gameplay_format": "1v1_constructed_best_of_three",
               "round_id": entry["round_id"], "round_number": entry["round_number"], "phase_type": entry["phase_type"],
               "match_id": entry["match_id"], "status_original": m.get("status"),
               "player_count": len(players), "player_ids": ";".join(map(str, players)),
               "explicit_bye": m.get("match_is_bye"), "ghost_original": m.get("is_ghost_match"),
               "non_game_loss_original": m.get("match_is_loss"),
               **classification, "included_in_swiss_draw_analysis": classification["included_in_draw_denominator"] and entry["phase_type"] == "SWISS",
               "pre_match_record_bracket": " vs ".join(sorted(pre_records)) if bracket_supported else "unknown_prior_record",
               "record_bracket_status": "verified_against_complete_final_record_replay" if bracket_supported else "unsupported_or_unreconciled_history",
               "duplicate_occurrences": entry["duplicate_occurrences"], "duplicate_conflict": entry["duplicate_conflict"],
               "match_page_coverage_complete": entry["match_page_coverage_complete"],
               **{k: source[k] for k in source},
               "all_source_pointers_json": json.dumps(entry["sources"], ensure_ascii=False, sort_keys=True)}
        rows.append(row)
        if classification["included_in_draw_denominator"] and classification["explicit_draw"]:
            explicit_credits += len(players)
            cut_draws += entry["phase_type"] != "SWISS"
        for player in players:
            if m.get("status") != "COMPLETE" or m.get("reports_are_in_conflict"):
                continue
            if m.get("match_is_bye"):
                running[player][0] += 1
            elif m.get("match_is_loss"):
                running[player][1] += 1
            elif classification["included_in_draw_denominator"]:
                running[player][2 if classification["explicit_draw"] else 0 if m.get("winning_player") == player else 1] += 1
    swiss = [row for row in rows if row["phase_type"] == "SWISS"]
    reconciliation = {"event_key": spec["event_key"], "final_standings_draw_credits": final_draw_credits,
                      "explicit_draw_player_credits_all_phases": explicit_credits,
                      "unreconciled_draw_credits": final_draw_credits - explicit_credits,
                      "unknown_final_records": unknown_final_records, "explicit_cut_draw_matches": cut_draws,
                      "record_histories_verified": len(verified_history),
                      "complete_match_page_coverage": all(g["complete"] for g in collection["match_sets"]),
                      "empty_swiss_rounds": ";".join(str(g["round_number"]) for g in collection["match_sets"] if g["phase_type"] == "SWISS" and not g["rows"]),
                      **summarize_matches(swiss)}
    return rows, reconciliation


def _group_draws(match_rows: list[dict], collections: dict) -> tuple[list[dict], list[dict]]:
    groups, brackets = defaultdict(list), defaultdict(list)
    empty_round_coverage = {}
    for key, collection in collections.items():
        spec = collection["spec"]
        for g in collection["match_sets"]:
            if g["phase_type"] == "SWISS":
                groups[("event_round", key, spec["event_type"], g["round_number"])]  # Retain empty rounds.
                empty_round_coverage[(key, g["round_number"])] = g["complete"]
    for row in match_rows:
        if row["phase_type"] != "SWISS":
            continue
        e, f, r = row["event_key"], row["event_format"], row["round_number"]
        keys = [("overall", "", "all", ""), ("event", e, f, ""), ("event_format", "", f, ""),
                ("round", "", "all", r), ("event_round", e, f, r), ("event_format_round", "", f, r)]
        for key in keys:
            groups[key].append(row)
        if row["included_in_draw_denominator"]:
            brackets[(e, f, r, row["pre_match_record_bracket"], row["record_bracket_status"])].append(row)
    rates = []
    for (scope, event, format_, round_), rows in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0]))):
        rates.append({"group_type": scope, "event_key": event, "event_format": format_, "round_number": round_,
                      "phase": "SWISS", "gameplay_format": "1v1_constructed_best_of_three",
                      **summarize_matches(rows),
                      "source_event_keys": ";".join(sorted({r["event_key"] for r in rows} or {event})),
                      "source_match_page_coverage_complete": all(r["match_page_coverage_complete"] for r in rows) if rows else empty_round_coverage[(event, round_)]})
    bracket_rows = [{"event_key": e, "event_format": f, "round_number": r, "pre_match_record_bracket": b,
                     "record_bracket_status": s, **summarize_matches(rows)}
                    for (e, f, r, b, s), rows in sorted(brackets.items())]
    return rates, bracket_rows


def build_phase2(root: Path) -> dict:
    root = Path(root).resolve()
    store = EvidenceStore(root)
    specs = json.loads((root / "data/events.json").read_text())
    captures = [json.loads(line) for line in store.ledger.read_text().splitlines()]
    capture_by_id = {r["source_id"]: r for r in captures}
    review_path = root / "data/phase2_disqualification_reviews.json"
    reviews = {}
    for review in json.loads(review_path.read_text())["reviews"]:
        for field in ("record_source_id", "policy_source_id"):
            if review[field] not in capture_by_id:
                raise ValueError("DQ review must reference preserved raw evidence")
            store.read(capture_by_id[review[field]])
        key = (review["event_key"], review["registration_id"])
        if key in reviews:
            raise ValueError("Duplicate DQ review")
        reviews[key] = review
    strict_summaries = {r["event_key"]: r for r in _read_csv(root / "outputs/tables/event_summary.csv")}
    summaries, individuals, distributions, match_rows, reconciliations = [], [], [], [], []
    collections, used_reviews, input_paths = {}, set(), {root / "data/events.json", store.ledger, review_path,
                                                       root / "data/phase2_legacy_fingerprints.json"}
    bounds_output = root / "outputs/phase2/constructions"
    bounds_output.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        key = spec["event_key"]
        collection = read_collection(root, key)
        collections[key] = collection
        input_paths.add(root / "data/interim" / (key + ".json.gz"))
        source = next(r for r in reversed(captures) if r["url"] == spec["payout_url"] and r["http_status"] == 200)
        rule = schedule_rule(store.read(source).decode(), spec["event_type"])
        legacy = strict_summaries[key]
        input_paths.add(root / "data/processed" / key / "standings.csv")
        legacy_rows = {int(r["registration_id"]): r for r in _read_csv(root / "data/processed" / key / "standings.csv")}
        n = len(collection["standings"]["rows"])
        n_match = int(legacy["participants_with_match_evidence"])
        awards, dropped_awards, dq_unresolved, unknown_records = [], [], 0, 0
        source_statuses = Counter()
        for wrapped in collection["standings"]["rows"]:
            raw = wrapped["row"]
            status = raw["user_event_status"]
            reg = status["id"]
            old = legacy_rows[reg]
            source_statuses[status.get("registration_status")] += 1
            if spec["event_type"] != "saturday":
                review = reviews.get((key, reg))
                if review:
                    used_reviews.add((key, reg))
                result = recorded_award(raw, rounds=rule["rounds"], table={int(w): p for w, p in rule["win_tickets"].items()}, dq_review=review)
                award = result["primary_ticket_award"]
                dq_unresolved += result["disqualification_status"].startswith("explicit_dq_policy_unresolved")
                unknown_records += award is None
            else:
                result, award = {}, None
            awards.append(award)
            if status.get("registration_status") == "DROPPED":
                dropped_awards.append(award)
            rank = raw["rank"]
            individuals.append({"event_key": key, "event_format": spec["event_type"], "official_event_id": spec["official_event_id"],
                                "registration_id": reg, "player_name": status.get("best_identifier"), "latest_round_rank": rank,
                                "match_record_original": raw.get("match_record"), "registration_status_original": status.get("registration_status"),
                                "observed_standings_implied_tickets": award, **result,
                                "legacy_supported_eligible_tickets": old["supported_eligible_tickets"] or None,
                                "legacy_strict_published_entitlement": old["published_ticket_entitlement"] or None,
                                "legacy_flags": old["flags"], "official_resolved_individual_tickets": old["published_ticket_entitlement"] or None if spec["event_type"] == "saturday" else None,
                                "conditional_top8_equal_split_scenario_tickets": saturday_top8_split(rank) if spec["event_type"] == "saturday" else None,
                                "event_specific_split_verified": False if spec["event_type"] == "saturday" else None,
                                "physically_issued_tickets": None, **provenance(wrapped),
                                "payout_source_id": source["source_id"], "payout_source_url": source["url"]})
        conditional_pool = saturday_pool(n) if spec["event_type"] == "saturday" else None
        total = sum(a for a in awards if a is not None) if spec["event_type"] != "saturday" else None
        comparison = conditional_pool if spec["event_type"] == "saturday" else total
        benchmark = None
        if spec["event_type"] != "saturday":
            table = {int(w): p for w, p in rule["win_tickets"].items()}
            benchmark = no_draw_upper_bound(n, rule["rounds"], table)
            construction = construct_no_draw_swiss(n, rule["rounds"], table)
            witness_path = bounds_output / (key + ".json.gz")
            witness_path.write_bytes(gzip.compress((json.dumps({"event_key": key, "reference_n_basis": "final_standings_entries_field_proxy",
                                                               "payout_source_id": source["source_id"], "payout_source_url": source["url"],
                                                               "win_tickets": table, "bound": benchmark, "construction": construction}, sort_keys=True) + "\n").encode(), mtime=0))
            match_n_bound = no_draw_upper_bound(n_match, rule["rounds"], table)
            threshold_awards = awards
            bases = {"observed_standings_implied": awards}
        else:
            construction, match_n_bound, witness_path = None, None, None
            threshold_awards = [saturday_placement(rank) for rank in range(1, n + 1)]
            bases = {"conditional_official_rank_slots_not_player_finish_claims": threshold_awards,
                     "top8_equal_split_scenario_not_extra_tickets": [saturday_top8_split(rank) for rank in range(1, n + 1)],
                     "archived_resolved_individual_subtotal": [int(r["published_ticket_entitlement"]) if r["published_ticket_entitlement"] else None for r in legacy_rows.values()]}
        for basis, values in bases.items():
            for award, count in sorted(Counter(values).items(), key=lambda kv: -1 if kv[0] is None else kv[0]):
                distributions.append({"event_key": key, "city": spec["city"], "event_format": spec["event_type"], "basis": basis,
                                      "tickets_per_entry": award, "entries": count, "share_of_standings_entries": _rate(count, n),
                                      "tickets_total": award * count if award is not None else None,
                                      "evidence_class": "observed_record_rule_calculation" if spec["event_type"] != "saturday" else "conditional_schedule_allocation" if basis.startswith("conditional") else "reported_split_scenario" if basis.startswith("top8") else "legacy_strict_subtotal"})
        metadata = collection["metadata"]
        summaries.append({"event_key": key, "city": spec["city"], "event_format": spec["event_type"], "official_event_id": spec["official_event_id"],
                          "observed_n": n, "observed_n_basis": "final_standings_entries_field_proxy_includes_zero_match_rows",
                          "roster_entries": len(collection["roster"]["rows"]), "match_evidenced_participants": n_match,
                          "roster_only_entries": int(legacy["roster_only_rows"]), "published_capacity": rule.get("published_capacity"),
                          "published_swiss_rounds": rule["rounds"], "latest_completed_round_label": collection["selected_round_number"],
                          "metadata_round_time_limit_minutes": metadata["settings"].get("round_duration_in_minutes"),
                          "schedule_round_time_limit_minutes": int(re.search(r"(\d+)m time limit", rule["schedule_row"][2])[1]),
                          "observed_standings_implied_tickets": total, "conditional_schedule_pool": conditional_pool,
                          "primary_comparison_tickets": comparison,
                          "primary_basis": "conditional_all_top128_placements_awarded" if conditional_pool is not None else "final_record_rule_sum_including_dropped",
                          "primary_result_status": "conditional_published_schedule_pool" if conditional_pool is not None else "complete_over_available_final_standings" if not unknown_records and collection["standings"]["complete"] and not dq_unresolved else "partial_or_dq_review_required",
                          "known_record_tickets": total, "unknown_final_record_awards": unknown_records,
                          "dropped_entries": source_statuses["DROPPED"], "dropped_qualifying_entries": sum(a is not None and a > 0 for a in dropped_awards),
                          "dropped_record_tickets_included": sum(a for a in dropped_awards if a is not None) if spec["event_type"] != "saturday" else None,
                          "disqualification_reviews_applied": sum((key, r) in used_reviews for r in legacy_rows), "unresolved_explicit_disqualifications": dq_unresolved,
                          "legacy_supported_eligible_tickets_known_sensitivity": int(legacy["supported_eligible_tickets_known"]),
                          "legacy_strict_reconstructed_event_tickets": legacy["reconstructed_event_tickets"] or None,
                          "tickets_per_standings_entry": _rate(comparison, n), "tickets_per_match_evidenced_participant": _rate(comparison, n_match),
                          **_thresholds(threshold_awards, n), "individual_distribution_basis": next(iter(bases)),
                          "theoretical_exact_maximum_tickets": None,
                          "theoretical_upper_bound_tickets": benchmark["upper_bound_tickets"] if benchmark else None,
                          "theoretical_result_status": benchmark["result_status"] if benchmark else "not_applicable_fixed_schedule_pool",
                          "no_draw_swiss_constructed_tickets": construction["constructed_tickets"] if construction else None,
                          "no_draw_swiss_construction_status": construction["result_status"] if construction else None,
                          "upper_bound_at_match_evidenced_n": match_n_bound["upper_bound_tickets"] if match_n_bound else None,
                          "observed_over_relaxed_upper_bound": _rate(total, benchmark["upper_bound_tickets"]) if benchmark else None,
                          "observed_over_swiss_constructed_example": _rate(total, construction["constructed_tickets"]) if construction else None,
                          "counterfactual_witness_path": str(witness_path.relative_to(root)) if witness_path else None,
                          "conservative_unknown_eligibility_rows": int(legacy["unknown_eligibility_rows"]),
                          "legacy_event_issues": legacy["event_issues"], "legacy_source_warnings": legacy["source_warnings"],
                          "physically_issued_tickets": None, "issuance_status": "unverified_no_claim_ledger",
                          "standings_url": f"{LOCATOR}/{spec['official_event_id']}", "payout_source_url": source["url"], "payout_source_id": source["source_id"]})
        event_match_rows, reconciliation = _match_rows(collection, spec, rule)
        match_rows.extend(event_match_rows)
        reconciliations.append(reconciliation)
    if set(reviews) != used_reviews:
        raise ValueError("DQ review does not match an available standings row")
    rates, brackets = _group_draws(match_rows, collections)
    output = root / "outputs/tables"
    cohort_rows = []
    for format_ in ("friday", "saturday", "sunday"):
        rows = [s for s in summaries if s["event_format"] == format_]
        field_n = sum(s["observed_n"] for s in rows)
        ticket_total = sum(s["primary_comparison_tickets"] for s in rows)
        draw_summary = next(r for r in rates if r["group_type"] == "event_format" and r["event_format"] == format_)
        cohort_rows.append({"event_format": format_, "events": len(rows), "standings_entries": field_n,
                            "match_evidenced_participants": sum(s["match_evidenced_participants"] for s in rows),
                            "primary_ticket_total": ticket_total,
                            "basis": "conditional_all_top128_placements_awarded" if format_ == "saturday" else "observed_standings_implied_including_dropped",
                            "tickets_per_standings_entry_weighted": ticket_total / field_n,
                            "entries_at_least_40": sum(s["entries_at_least_40"] for s in rows),
                            "share_at_least_40_weighted": sum(s["entries_at_least_40"] for s in rows) / field_n,
                            "zero_award_entries": sum(s["zero_award_entries"] for s in rows),
                            "zero_award_share_weighted": sum(s["zero_award_entries"] for s in rows) / field_n,
                            "no_draw_constructed_total": sum(s["no_draw_swiss_constructed_tickets"] for s in rows) if format_ != "saturday" else None,
                            "proved_relaxed_upper_bound_total": sum(s["theoretical_upper_bound_tickets"] for s in rows) if format_ != "saturday" else None,
                            "dropped_record_tickets_included": sum(s["dropped_record_tickets_included"] for s in rows) if format_ != "saturday" else None,
                            "legacy_supported_eligible_known_sensitivity": sum(s["legacy_supported_eligible_tickets_known_sensitivity"] for s in rows),
                            "drawn_matches": draw_summary["drawn_matches"], "completed_played_matches": draw_summary["completed_played_matches"],
                            "match_weighted_draw_rate": draw_summary["draw_rate"]})
    for name, rows in (("historical_ticket_economy.csv", summaries), ("historical_individual_awards.csv", individuals),
                       ("historical_award_distribution.csv", distributions), ("historical_unique_matches.csv", match_rows),
                       ("historical_draw_rates.csv", rates), ("historical_draw_rates_by_record.csv", brackets),
                       ("historical_draw_reconciliation.csv", reconciliations), ("historical_cohort_summary.csv", cohort_rows)):
        write_csv(output / name, rows)
    report = {"events": len(summaries), "standings_entries": sum(s["observed_n"] for s in summaries),
              "friday_standings_implied_tickets": sum(s["observed_standings_implied_tickets"] for s in summaries if s["event_format"] == "friday"),
              "sunday_standings_implied_tickets": sum(s["observed_standings_implied_tickets"] for s in summaries if s["event_format"] == "sunday"),
              "saturday_conditional_pool": sum(s["conditional_schedule_pool"] for s in summaries if s["event_format"] == "saturday"),
              "draw_summary": next(r for r in rates if r["group_type"] == "overall"),
              "draw_summary_by_event_format": [r for r in rates if r["group_type"] == "event_format"],
              "counterfactual_status": "proved_relaxed_upper_bounds_and_separate_validated_swiss_constructions_no_exact_maximum_claim",
              "actual_physical_issuance_verified": False,
              "input_sha256": {str(p.relative_to(root)): _hash(p) for p in sorted(input_paths)},
              "code_sha256": {str(p.relative_to(root)): _hash(p) for p in sorted((root / "src").rglob("*.py"))}}
    _write_json(output / "historical_phase2_report.json", report)
    return report


def audit_phase2(root: Path) -> dict:
    """Check primary totals, distinct match denominators, witnesses, and inputs."""
    root = Path(root).resolve()
    protected = json.loads((root / "data/phase2_legacy_fingerprints.json").read_text())["files"]
    changed = [name for name, digest in protected.items() if not (root / name).exists() or _hash(root / name) != digest]
    if changed:
        raise ValueError(f"Phase 2 changed protected archival/legacy artifacts: {changed}")
    tables = root / "outputs/tables"
    report = json.loads((tables / "historical_phase2_report.json").read_text())
    for name, digest in {**report["input_sha256"], **report["code_sha256"]}.items():
        if _hash(root / name) != digest:
            raise ValueError(f"Phase 2 inputs/code changed; rerun phase2: {name}")
    summary = _read_csv(tables / "historical_ticket_economy.csv")
    people = _read_csv(tables / "historical_individual_awards.csv")
    distribution = _read_csv(tables / "historical_award_distribution.csv")
    match_rows = _read_csv(tables / "historical_unique_matches.csv")
    rates = _read_csv(tables / "historical_draw_rates.csv")
    if len(summary) != 24 or len({s["event_key"] for s in summary}) != 24:
        raise ValueError("Phase 2 must cover 24 distinct events")
    keys = [(m["event_key"], m["round_id"], m["match_id"]) for m in match_rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate matches in Phase 2 denominator")
    people_keys = [(r["event_key"], r["registration_id"]) for r in people]
    if len(people_keys) != len(set(people_keys)):
        raise ValueError("Duplicate standings entries")
    store = EvidenceStore(root)
    captures = [json.loads(line) for line in store.ledger.read_text().splitlines()]
    for s in summary:
        key = s["event_key"]
        rows = [p for p in people if p["event_key"] == key]
        if len(rows) != int(s["observed_n"]):
            raise ValueError(f"Phase 2 field count mismatch: {key}")
        if s["event_format"] == "saturday":
            if int(s["conditional_schedule_pool"]) != 4992 or s["observed_standings_implied_tickets"]:
                raise ValueError("Saturday must retain the conditional-pool distinction")
        else:
            total = sum(int(r["observed_standings_implied_tickets"]) for r in rows if r["observed_standings_implied_tickets"])
            if total != int(s["observed_standings_implied_tickets"]):
                raise ValueError(f"Primary total mismatch: {key}")
            certificate = json.loads(gzip.decompress((root / s["counterfactual_witness_path"]).read_bytes()))
            source = next(r for r in reversed(captures) if r["url"] == s["payout_source_url"] and r["http_status"] == 200)
            rule = schedule_rule(store.read(source).decode(), s["event_format"])
            table = {int(w): p for w, p in rule["win_tickets"].items()}
            from .models.historical_bounds import validate_construction
            if certificate["construction"]["n"] != int(s["observed_n"]) or certificate["construction"]["rounds"] != rule["rounds"]:
                raise ValueError(f"Construction field/round assumptions mismatch: {key}")
            if {int(w): p for w, p in certificate["win_tickets"].items()} != table or certificate["payout_source_id"] != source["source_id"]:
                raise ValueError(f"Construction payout source mismatch: {key}")
            validate_construction(certificate["construction"], table)
            expected_bound = no_draw_upper_bound(int(s["observed_n"]), rule["rounds"], table)
            if certificate["bound"] != expected_bound or int(s["theoretical_upper_bound_tickets"]) != expected_bound["upper_bound_tickets"]:
                raise ValueError(f"Bound proof mismatch: {key}")
            if int(s["no_draw_swiss_constructed_tickets"]) != certificate["construction"]["constructed_tickets"]:
                raise ValueError(f"Constructed total mismatch: {key}")
        base = s["individual_distribution_basis"]
        bins = [d for d in distribution if d["event_key"] == key and d["basis"] == base]
        if sum(int(d["entries"]) for d in bins) != len(rows):
            raise ValueError(f"Individual distribution count mismatch: {key}")
        if sum(int(d["tickets_total"]) for d in bins if d["tickets_total"]) != int(s["primary_comparison_tickets"]):
            raise ValueError(f"Individual distribution ticket mismatch: {key}")
    decoded = []
    for row in match_rows:
        decoded.append({**row, "included_in_draw_denominator": row["included_in_draw_denominator"] == "True",
                        "explicit_draw": row["explicit_draw"] == "True" if row["explicit_draw"] else None,
                        "duplicate_occurrences": int(row["duplicate_occurrences"])})
    swiss = [r for r in decoded if r["phase_type"] == "SWISS"]
    for group in rates:
        selected = swiss
        if group["event_key"]:
            selected = [m for m in selected if m["event_key"] == group["event_key"]]
        if group["event_format"] != "all":
            selected = [m for m in selected if m["event_format"] == group["event_format"]]
        if group["round_number"]:
            selected = [m for m in selected if m["round_number"] == group["round_number"]]
        expected = summarize_matches(selected)
        for field, value in expected.items():
            actual = group[field]
            if isinstance(value, (int, float)):
                if not actual or abs(float(actual) - value) > 1e-12:
                    raise ValueError(f"Draw grouping mismatch: {group['group_type']} {field}")
            elif actual != ("" if value is None else value):
                raise ValueError(f"Draw grouping mismatch: {group['group_type']} {field}")
    result = {"passed": True, "events": len(summary), "standings_entries": len(people),
              "unique_match_records_all_phases": len(match_rows), "swiss": summarize_matches(swiss),
              "raw_and_legacy_artifacts_unchanged": True, "protected_artifacts_checked": len(protected),
              "no_exact_maximum_claim": all(not s["theoretical_exact_maximum_tickets"] for s in summary),
              "physically_issued_tickets_verified": False}
    _write_json(tables / "historical_phase2_validation.json", result)
    return result
