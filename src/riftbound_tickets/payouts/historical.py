"""Primary standings-implied entitlements; DROPPED is not a DQ policy."""

from __future__ import annotations

import re

from .rules import SATURDAY_TIERS, win_record_payout


def recorded_award(raw: dict, *, rounds: int, table: dict[int, int],
                   dq_review: dict | None = None) -> dict:
    """Use the final explicit match record without imputing absent standings.

    A documented DQ review must link both its record and the historical policy.
    Status alone never authorizes an exclusion, and DROPPED/ELIMINATED is never
    translated to DISQUALIFIED. A DQ adjustment concerns entitlements, not proof
    of returning or retaining already physically awarded prizes.
    """
    record = raw.get("match_record")
    match = re.fullmatch(r"(\d+)-(\d+)-(\d+)", record or "")
    values = tuple(map(int, match.groups())) if match else (None, None, None)
    award = win_record_payout(*values, rounds=rounds, table=table)
    status = (raw.get("user_event_status") or {}).get("registration_status")
    explicit_dq = status == "DISQUALIFIED" or (raw.get("user_event_status") or {}).get("is_disqualified") is True
    excluded = False
    dq_state = "none_explicitly_recorded"
    if dq_review:
        required = ("record_source_id", "policy_source_id", "policy_interpretation", "action")
        if any(not dq_review.get(k) for k in required) or dq_review["action"] != "exclude":
            raise ValueError("DQ exclusion requires attributable record evidence and a documented policy interpretation")
        # A review can document an explicit DQ outside this standings status.
        if not explicit_dq and dq_review.get("explicit_dq_evidence_reviewed") is not True:
            raise ValueError("A drop or ambiguous status is not explicit DQ evidence")
        excluded, dq_state = True, "excluded_by_documented_dq_review"
    elif explicit_dq:
        dq_state = "explicit_dq_policy_unresolved_included_pending_review"
    return {"record": record, "wins": values[0], "losses": values[1], "draws": values[2],
            "record_rule_tickets": award, "primary_ticket_award": 0 if excluded and award is not None else award,
            "registration_status_original": status, "dropped": status == "DROPPED",
            "explicit_disqualification": explicit_dq, "disqualification_status": dq_state,
            "dq_adjustment_tickets": award if excluded else 0,
            "record_status": "known_record" if award is not None else "unknown_or_outside_published_round_limit"}


def saturday_pool(standings_entries: int, *, all_placements_awarded: bool = True) -> int | None:
    """Conditional funded Top 128 pool, independent of bracket winners/statuses."""
    if type(standings_entries) is not int or standings_entries < 0:
        raise ValueError("Invalid standings count")
    if not all_placements_awarded or standings_entries < 128:
        return None
    return sum((hi - lo + 1) * tickets for lo, hi, tickets in SATURDAY_TIERS)
