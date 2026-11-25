"""Exact equal-skill Saturday benchmarks; no Swiss simulation or Monte Carlo.

Historical placement slots are exchangeable. Vegas is a two-stage marginal
binomial model with qualification applied before Sunday outcomes. Expected field
totals use linearity, not an assumption of independent players in a tournament.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from ..payouts.rules import SATURDAY_TIERS, saturday_placement, saturday_top8_split


@dataclass(frozen=True)
class VegasRules:
    day1_rounds: int
    day2_rounds: int
    day2_minimum_match_points: int
    point_tiers: tuple[tuple[int, int, int], ...]
    points_per_win: int = 3
    points_per_draw: int = 1

    def __post_init__(self):
        if self.day1_rounds != 6 or self.day2_rounds != 5:
            raise ValueError("This verified Vegas benchmark requires six plus five rounds, totaling eleven")
        if self.day2_minimum_match_points != 12 or self.points_per_win != 3 or self.points_per_draw != 1:
            raise ValueError("Unexpected Vegas qualification/scoring rules; review official sources")
        covered = []
        for low, high, tickets in self.point_tiers:
            if any(type(v) is not int for v in (low, high, tickets)) or not 0 <= low <= high <= self.maximum_match_points or tickets < 0:
                raise ValueError("Invalid point payout tier")
            covered.extend(range(low, high + 1))
        if sorted(covered) != list(range(19, 34)):
            raise ValueError("Vegas table must preserve every published point band, including no-draw-inaccessible bands")

    @property
    def total_rounds(self) -> int:
        return self.day1_rounds + self.day2_rounds

    @property
    def maximum_match_points(self) -> int:
        return self.total_rounds * self.points_per_win


@dataclass(frozen=True)
class VegasPath:
    day1_wins: int
    day1_points: int
    qualifies: bool
    day2_wins: int | None
    final_points: int
    tickets: int
    scheduled_rounds: int
    probability: Fraction


def _probability(p: Fraction) -> Fraction:
    if not isinstance(p, (int, Fraction)) or isinstance(p, bool):
        raise ValueError("Use exact Fraction probabilities, not floating-point approximations")
    p = Fraction(p)
    if not 0 <= p <= 1:
        raise ValueError("Win probability must be between zero and one")
    return p


def binomial_probabilities(rounds: int, win_probability: Fraction = Fraction(1, 2)) -> dict[int, Fraction]:
    if type(rounds) is not int or rounds < 0:
        raise ValueError("Round count must be a nonnegative integer")
    p = _probability(win_probability)
    return {wins: comb(rounds, wins) * p**wins * (1-p)**(rounds-wins) for wins in range(rounds+1)}


def qualifies_for_day2(day1_points: int, rules: VegasRules) -> bool:
    """Point-based gate, usable by a later explicitly specified draw model."""
    if type(day1_points) is not int or not 0 <= day1_points <= rules.day1_rounds * rules.points_per_win:
        raise ValueError("Invalid first-stage points")
    return day1_points >= rules.day2_minimum_match_points


def vegas_point_award(final_points: int, rules: VegasRules) -> int:
    """Full published point table, independent of baseline point reachability."""
    if type(final_points) is not int or not 0 <= final_points <= rules.maximum_match_points:
        raise ValueError("Invalid final match points")
    return next((tickets for low, high, tickets in rules.point_tiers if low <= final_points <= high), 0)


def vegas_paths(rules: VegasRules, win_probability: Fraction = Fraction(1, 2)) -> tuple[VegasPath, ...]:
    first = binomial_probabilities(rules.day1_rounds, win_probability)
    second = binomial_probabilities(rules.day2_rounds, win_probability)
    paths = []
    for wins, probability in first.items():
        first_points = rules.points_per_win * wins
        if not qualifies_for_day2(first_points, rules):
            # No fictitious Sunday rounds or wins for nonqualifiers.
            paths.append(VegasPath(wins, first_points, False, None, first_points,
                                   vegas_point_award(first_points, rules), rules.day1_rounds, probability))
            continue
        for extra_wins, conditional_probability in second.items():
            final_points = first_points + rules.points_per_win * extra_wins
            paths.append(VegasPath(wins, first_points, True, extra_wins, final_points,
                                   vegas_point_award(final_points, rules), rules.total_rounds,
                                   probability * conditional_probability))
    if sum(path.probability for path in paths) != 1:
        raise ValueError("Two-stage path probabilities do not normalize")
    return tuple(paths)


def vegas_ticket_distribution(rules: VegasRules, win_probability: Fraction = Fraction(1, 2)) -> dict[int, Fraction]:
    distribution = {award: Fraction(0) for award in sorted({0, *(p for _, _, p in rules.point_tiers)})}
    for path in vegas_paths(rules, win_probability):
        distribution[path.tickets] += path.probability
    return distribution


def vegas_final_point_distribution(rules: VegasRules, win_probability: Fraction = Fraction(1, 2)) -> dict[int, Fraction]:
    distribution = {point: Fraction(0) for point in range(rules.maximum_match_points + 1)}
    for path in vegas_paths(rules, win_probability):
        distribution[path.final_points] += path.probability
    return distribution


def historical_ticket_distribution(entrants: int, *, split_top8: bool = False) -> dict[int, Fraction]:
    """Uniform rank-slot model, conditional on all 128 advertised awards funded."""
    if type(entrants) is not int or entrants < 128:
        raise ValueError("The full Top 128 model requires at least 128 entrants")
    possible = {0, *(p for _, _, p in SATURDAY_TIERS)}
    distribution = {ticket: Fraction(0) for ticket in sorted(possible)}
    payout = saturday_top8_split if split_top8 else saturday_placement
    for rank in range(1, entrants+1):
        distribution[payout(rank)] += Fraction(1, entrants)
    if sum(distribution.values()) != 1:
        raise ValueError("Historical probabilities do not normalize")
    if sum(ticket * probability for ticket, probability in distribution.items()) * entrants != 4992:
        raise ValueError("Historical rank-slot pool was not conserved")
    return distribution


def upper_tail_ticket_share(distribution: dict[int, Fraction], population_share: Fraction) -> Fraction:
    """Marginal upper-tail share, allowing fractional mass within tied awards."""
    fraction = _probability(population_share)
    mean = sum(ticket * p for ticket, p in distribution.items())
    if mean == 0:
        return Fraction(0)
    remaining, tickets = fraction, Fraction(0)
    for award in sorted(distribution, reverse=True):
        take = min(remaining, distribution[award])
        tickets += take * award
        remaining -= take
        if remaining == 0:
            break
    return tickets / mean


def ticket_metrics(distribution: dict[int, Fraction], entrants: int, expected_rounds: Fraction) -> dict[str, Fraction | int]:
    if type(entrants) is not int or entrants < 1 or sum(distribution.values()) != 1 or any(p < 0 for p in distribution.values()):
        raise ValueError("Invalid entrant count or probability distribution")
    mean = sum(ticket * p for ticket, p in distribution.items())
    p40 = sum((p for ticket, p in distribution.items() if ticket >= 40), Fraction(0))
    p80 = sum((p for ticket, p in distribution.items() if ticket >= 80), Fraction(0))
    gini = sum((p * q * abs(a-b) for a, p in distribution.items() for b, q in distribution.items()), Fraction(0)) / (2 * mean) if mean else Fraction(0)
    return {"expected_tickets_per_entrant": mean, "expected_total_tickets": mean * entrants,
            "zero_ticket_probability": distribution.get(0, Fraction(0)),
            "any_ticket_probability": 1 - distribution.get(0, Fraction(0)),
            "at_least_40_probability": p40, "at_least_80_probability": p80,
            "maximum_individual_payout": max(t for t, p in distribution.items() if p > 0),
            "expected_scheduled_rounds_per_entrant": expected_rounds,
            "expected_earning_entries": entrants * (1-distribution.get(0, Fraction(0))),
            "expected_entries_at_least_40": entrants * p40,
            "marginal_ticket_gini": gini,
            "top_1pct_marginal_ticket_share": upper_tail_ticket_share(distribution, Fraction(1,100)),
            "top_5pct_marginal_ticket_share": upper_tail_ticket_share(distribution, Fraction(5,100)),
            "top_10pct_marginal_ticket_share": upper_tail_ticket_share(distribution, Fraction(1,10)),
            "ticket_share_in_40plus_outcomes": sum((t*p for t,p in distribution.items() if t>=40),Fraction(0))/mean if mean else Fraction(0),
            "ticket_variance": sum(t*t*p for t,p in distribution.items()) - mean*mean}


def historical_metrics(entrants: int, *, split_top8: bool = False) -> dict:
    # Seven Swiss rounds for everyone; 8 QF + 4 SF + 2 final entrant-rounds.
    return ticket_metrics(historical_ticket_distribution(entrants, split_top8=split_top8), entrants, Fraction(7) + Fraction(14, entrants))


def vegas_metrics(entrants: int, rules: VegasRules, win_probability: Fraction = Fraction(1,2)) -> dict:
    paths = vegas_paths(rules, win_probability)
    qualification = sum((p.probability for p in paths if p.qualifies), Fraction(0))
    result = ticket_metrics(vegas_ticket_distribution(rules, win_probability), entrants,
                            Fraction(rules.day1_rounds) + rules.day2_rounds * qualification)
    result["qualification_probability"] = qualification
    result["expected_day2_entrants"] = entrants * qualification
    result["at_least_40_given_qualified"] = result["at_least_40_probability"] / qualification if qualification else Fraction(0)
    return result
