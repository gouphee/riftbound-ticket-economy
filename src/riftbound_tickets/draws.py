"""Unique-match empirical draw rates with exclusions and descriptive uncertainty."""

from __future__ import annotations

import json
from collections import Counter
from math import sqrt

SEMANTIC_MATCH_FIELDS = (
    "id", "tournament_round", "status", "match_type", "players", "winning_player",
    "match_is_bye", "is_ghost_match", "match_is_loss", "reports_are_in_conflict",
    "match_is_intentional_draw", "match_is_unintentional_draw",
    "games_won_by_winner", "games_won_by_loser", "games_drawn",
)


def classify_match(match: dict, *, duplicate_conflict: bool = False) -> dict:
    """Only completed two-person played matches with explicit results enter n.

    Missing winner is not sufficient evidence of a draw. One-player automatic
    loss records are non-games, independently of the API's COMPLETE flag.
    """
    reason = None
    intentional = match.get("match_is_intentional_draw") is True
    unintentional = match.get("match_is_unintentional_draw") is True
    players = match.get("players") or []
    winner = match.get("winning_player")
    if duplicate_conflict or match.get("reports_are_in_conflict"):
        reason = "conflicted"
    elif match.get("status") != "COMPLETE":
        reason = "incomplete"
    elif match.get("match_is_bye"):
        reason = "bye"
    elif match.get("is_ghost_match"):
        reason = "ghost"
    elif match.get("match_is_loss") or len(players) != 2 or len(set(players)) != 2:
        reason = "non_game"
    elif match.get("match_type") != "PLAYER_VS_PLAYER":
        reason = "unsupported_match_type"
    elif winner is not None and (intentional or unintentional):
        reason = "conflicted"
    elif winner is not None and winner not in players:
        reason = "conflicted"
    elif winner is None and not (intentional or unintentional):
        reason = "unknown_result"
    if reason:
        return {"included_in_draw_denominator": False, "exclusion_reason": reason,
                "explicit_draw": None, "draw_type": None, "draw_type_conflict": False}
    drawn = intentional or unintentional
    draw_type = "intentional" if intentional and not unintentional else "unintentional" if unintentional and not intentional else "ambiguous_both_flags" if drawn else "decisive"
    return {"included_in_draw_denominator": True, "exclusion_reason": "",
            "explicit_draw": drawn, "draw_type": draw_type,
            "draw_type_conflict": intentional and unintentional}


def unique_matches(collection: dict) -> list[dict]:
    """Deduplicate by event + round ID + match ID, retaining every source pointer."""
    unique = {}
    for group in collection["match_sets"]:
        for wrapped in group["rows"]:
            match = wrapped["row"]
            key = (collection["event_key"], group["round_id"], match["id"])
            signature = json.dumps({k: match.get(k) for k in SEMANTIC_MATCH_FIELDS}, sort_keys=True)
            source = {k: wrapped.get(k) for k in ("source_id", "source_url", "raw_path", "retrieved_at", "page", "row_index")}
            if key not in unique:
                unique[key] = {"event_key": key[0], "round_id": key[1], "match_id": key[2],
                               "round_number": group["round_number"], "phase_type": group["phase_type"],
                               "match": match, "sources": [source], "signature": signature,
                               "duplicate_occurrences": 0, "duplicate_conflict": False,
                               "match_page_coverage_complete": group["complete"]}
            else:
                entry = unique[key]
                entry["duplicate_occurrences"] += 1
                entry["sources"].append(source)
                entry["duplicate_conflict"] |= signature != entry["signature"] or group["phase_type"] != entry["phase_type"]
            if match.get("tournament_round") != group["round_id"]:
                unique[key]["duplicate_conflict"] = True
    return list(unique.values())


def wilson_interval(drawn: int, completed: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    """95% descriptive binomial interval, not uncertainty in census arithmetic.

    Repeated players and tournament rounds are correlated. This interval is a
    working independent-match model, not a design-adjusted population claim.
    """
    if not 0 <= drawn <= completed:
        raise ValueError("Invalid draw count")
    if not completed:
        return None, None
    proportion = drawn / completed
    denominator = 1 + z * z / completed
    middle = (proportion + z * z / (2 * completed)) / denominator
    radius = z * sqrt(proportion * (1 - proportion) / completed + z * z / (4 * completed * completed)) / denominator
    return max(0.0, middle - radius), min(1.0, middle + radius)


def summarize_matches(rows: list[dict]) -> dict:
    counts = Counter()
    for row in rows:
        counts["unique_match_records"] += 1
        counts["duplicate_occurrences_removed"] += row.get("duplicate_occurrences", 0)
        if row["included_in_draw_denominator"]:
            counts["completed_played_matches"] += 1
            counts["drawn_matches"] += row["explicit_draw"]
            counts["decisive_matches"] += not row["explicit_draw"]
            counts["intentional_draws"] += row["draw_type"] == "intentional"
            counts["unintentional_draws"] += row["draw_type"] == "unintentional"
            counts["draw_type_ambiguous"] += row["draw_type"] == "ambiguous_both_flags"
        else:
            counts["excluded_" + row["exclusion_reason"]] += 1
    fields = ["unique_match_records", "duplicate_occurrences_removed", "completed_played_matches", "drawn_matches",
              "decisive_matches", "intentional_draws", "unintentional_draws", "draw_type_ambiguous",
              "excluded_bye", "excluded_ghost", "excluded_non_game", "excluded_incomplete", "excluded_conflicted",
              "excluded_unknown_result", "excluded_unsupported_match_type"]
    result = {field: counts[field] for field in fields}
    n, d = result["completed_played_matches"], result["drawn_matches"]
    result["excluded_total"] = result["unique_match_records"] - n
    uncertain = result["excluded_unknown_result"] + result["excluded_conflicted"]
    lo, hi = wilson_interval(d, n)
    result.update({"draw_rate": d / n if n else None, "draw_rate_wilson95_low": lo, "draw_rate_wilson95_high": hi,
                   "result_classification_coverage": n / (n + uncertain) if n + uncertain else None,
                   "unknown_result_sensitivity_low": d / (n + uncertain) if n + uncertain else None,
                   "unknown_result_sensitivity_high": (d + uncertain) / (n + uncertain) if n + uncertain else None,
                   "uncertain_completed_candidates": uncertain,
                   "interval_interpretation": "descriptive_independent_match_wilson_not_cluster_adjusted"})
    return result
