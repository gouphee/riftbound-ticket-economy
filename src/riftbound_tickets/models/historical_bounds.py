"""Proved ceilings and explicit feasible Swiss examples; no Monte Carlo.

The ceiling relaxes Swiss pairing/opponent constraints, and therefore bounds
every Swiss tournament in the stated full-participation, no-draw reference.
The separate construction enforces score-group pairing, unique opponents, and
at most one lowest-eligible bye per round. Neither is called the exact maximum.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from functools import reduce
from math import gcd


def _validate(n: int, rounds: int, table: dict[int, int]):
    if type(n) is not int or n < 2 or type(rounds) is not int or rounds < 1:
        raise ValueError("Need at least two players and a positive integer round count")
    if rounds > (n if n % 2 else n - 1):
        raise ValueError("Not enough unique opponents/one-time byes for full participation")
    if not table or any(type(w) is not int or w < 0 or w > rounds or type(p) is not int or p < 0 for w, p in table.items()):
        raise ValueError("Invalid payout table")


def no_draw_upper_bound(n: int, rounds: int, table: dict[int, int]) -> dict:
    """LP relaxation over final win counts, rounded down to a ticket lattice.

    Every round creates floor(N/2) played-match wins plus N%2 bye wins.
    Thus W=R*ceil(N/2). For any feasible tournament n_w counts satisfy
    sum(n_w)=N, sum(w*n_w)=W, n_w>=0. Relax integrality and all opponent/
    Swiss constraints. A vertex of this two-equality LP uses at most two win
    levels; enumerate them using exact rational arithmetic. Rounding DOWN to
    the payout GCD remains a proved ceiling on any integer tournament payout.
    Fractional level counts are a proof certificate, not feasible standings.
    """
    _validate(n, rounds, table)
    wins_budget = rounds * ((n + 1) // 2)
    payout = [table.get(w, 0) for w in range(rounds + 1)]
    best, certificate = None, None
    for low in range(rounds + 1):
        if low * n == wins_budget:
            value = Fraction(n * payout[low])
            if best is None or value > best:
                best, certificate = value, {low: Fraction(n)}
        for high in range(low + 1, rounds + 1):
            high_count = Fraction(wins_budget - low * n, high - low)
            low_count = n - high_count
            if min(low_count, high_count) < 0:
                continue
            value = low_count * payout[low] + high_count * payout[high]
            if best is None or value > best:
                best, certificate = value, {low: low_count, high: high_count}
    ticket_gcd = reduce(gcd, payout) or 1
    bound = (best.numerator // (best.denominator * ticket_gcd)) * ticket_gcd
    return {
        "n": n, "rounds": rounds, "no_draw_win_budget": wins_budget,
        "upper_bound_tickets": bound, "result_status": "proved_upper_bound_swiss_constraints_relaxed",
        "exact_swiss_maximum": None, "lp_ceiling_fraction": str(best), "payout_gcd": ticket_gcd,
        "fractional_win_counts_certificate": {str(k): str(v) for k, v in certificate.items()},
        "assumptions": "fixed_field_full_participation_no_draws_no_repeat_opponents_one_lowest_eligible_bye_if_odd",
        "constraints_relaxed_for_upper_bound": "integer_record_counts_opponent_graph_and_swiss_score_group_pairing",
    }


def _pair_group(players: list[int], opponents: list[set[int]]) -> list[tuple[int, int]] | None:
    """Find a perfect matching within one score group, excluding rematches."""
    if not players:
        return []
    # First round and most large groups have an immediate valid matching.
    adjacent = list(zip(players[::2], players[1::2]))
    if all(b not in opponents[a] for a, b in adjacent):
        return adjacent
    a = players[0]
    for index, b in enumerate(players[1:], 1):
        if b in opponents[a]:
            continue
        rest = _pair_group(players[1:index] + players[index + 1:], opponents)
        if rest is not None:
            return [(a, b), *rest]
    return None


def _swiss_pairs(groups: list[list[int]], opponents: list[set[int]],
                 index: int = 0, carry: int | None = None) -> list[tuple[int, int]] | None:
    """Process descending scores; float one player when a group is odd.

    A player can float past more than one score group if opponent restrictions
    prevent a pairing. This is an explicit reference policy, not a claim about
    the UVS implementation, tiebreakers, colors, or player skill.
    """
    if index == len(groups):
        return [] if carry is None else None
    players = sorted(groups[index] + ([] if carry is None else [carry]))
    floaters = list(reversed(players)) if len(players) % 2 else [None]
    for floater in floaters:
        remaining = [p for p in players if p != floater]
        pairs = _pair_group(remaining, opponents)
        if pairs is None:
            continue
        later = _swiss_pairs(groups, opponents, index + 1, floater)
        if later is not None:
            return pairs + later
    return None


def construct_no_draw_swiss(n: int, rounds: int, table: dict[int, int]) -> dict:
    """Construct one actual feasible reference tournament, not an expectation.

    Synthetic integer IDs, deterministic lower-ID winner, no random draws or
    skill model. All pairings and bye choices are retained for independent replay.
    A construction failure is explicit; it is never promoted to a maximum.
    """
    _validate(n, rounds, table)
    wins = [0] * n
    opponents = [set() for _ in range(n)]
    had_bye = set()
    witness = []
    for round_number in range(1, rounds + 1):
        bye = None
        if n % 2:
            eligible = [p for p in range(n) if p not in had_bye]
            bye = min(eligible, key=lambda p: (wins[p], -p))
        brackets = defaultdict(list)
        for player in range(n):
            if player != bye:
                brackets[wins[player]].append(player)
        scores = sorted(brackets, reverse=True)
        groups = [brackets[score] for score in scores]
        pairs = _swiss_pairs(groups, opponents)
        if pairs is None:
            raise ValueError(f"No reference-policy pairing found for N={n}, round={round_number}")
        pre_wins = wins.copy()
        for a, b in pairs:
            opponents[a].add(b)
            opponents[b].add(a)
            wins[min(a, b)] += 1
        if bye is not None:
            had_bye.add(bye)
            wins[bye] += 1
        witness.append({"round_number": round_number, "bye": bye,
                        "pairings": [{"players": [a, b], "pre_match_wins": [pre_wins[a], pre_wins[b]],
                                      "winner": min(a, b)} for a, b in pairs]})
    result = {"n": n, "rounds": rounds, "evidence_class": "deterministic_no_draw_counterfactual_witness",
              "result_status": "constructively_attained_not_optimized",
              "pairing_policy": "descending_score_groups_single_downfloats_no_repeat_opponents_lowest_eligible_bye",
              "final_win_counts": dict(sorted(Counter(wins).items())),
              "constructed_tickets": sum(table.get(w, 0) for w in wins), "rounds_witness": witness}
    validate_construction(result, table)
    return result


def validate_construction(result: dict, table: dict[int, int]) -> None:
    """Replay identity coverage, no repeats, score-first float policy, and wins."""
    n, rounds = result["n"], result["rounds"]
    _validate(n, rounds, table)
    wins, opponents, had_bye = [0] * n, [set() for _ in range(n)], set()
    if len(result["rounds_witness"]) != rounds:
        raise ValueError("Construction round coverage mismatch")
    for number, round_ in enumerate(result["rounds_witness"], 1):
        bye, seen = round_["bye"], set()
        if round_["round_number"] != number or len(round_["pairings"]) != n // 2:
            raise ValueError("Construction round/pair count mismatch")
        if (bye is not None) != bool(n % 2):
            raise ValueError("Invalid bye count")
        if bye is not None:
            if bye in had_bye or not 0 <= bye < n:
                raise ValueError("Repeated or invalid bye")
            if wins[bye] != min(wins[p] for p in range(n) if p not in had_bye):
                raise ValueError("Bye was not awarded at lowest eligible score")
            seen.add(bye)
        brackets = defaultdict(list)
        for player in range(n):
            if player != bye:
                brackets[wins[player]].append(player)
        # Require this exact deterministic score-first construction policy.
        expected_pairs = _swiss_pairs([brackets[s] for s in sorted(brackets, reverse=True)], opponents)
        actual_pairs = [tuple(p["players"]) for p in round_["pairings"]]
        if expected_pairs != actual_pairs:
            raise ValueError("Construction violates the stated Swiss pairing policy")
        for pair in round_["pairings"]:
            a, b = pair["players"]
            if a == b or not (0 <= a < n and 0 <= b < n) or a in seen or b in seen or b in opponents[a]:
                raise ValueError("Self pairing, repeat opponent, or duplicate player")
            if pair["pre_match_wins"] != [wins[a], wins[b]] or pair["winner"] != min(a, b):
                raise ValueError("Invalid pre-record or winner")
            seen.update((a, b))
        if seen != set(range(n)):
            raise ValueError("Construction does not cover the whole field")
        for pair in round_["pairings"]:
            a, b = pair["players"]
            opponents[a].add(b)
            opponents[b].add(a)
            wins[pair["winner"]] += 1
        if bye is not None:
            had_bye.add(bye)
            wins[bye] += 1
    if dict(Counter(wins)) != {int(k): v for k, v in result["final_win_counts"].items()}:
        raise ValueError("Final win distribution mismatch")
    if sum(table.get(w, 0) for w in wins) != result["constructed_tickets"]:
        raise ValueError("Constructed ticket total mismatch")
    if sum(wins) != rounds * ((n + 1) // 2):
        raise ValueError("Construction violates match-win conservation")
