"""Exact marginal W/D/L sensitivity and local outcome identities, not Swiss.

No draws are sampled. A points-generating polynomial is multiplied by dynamic
programming; the first-stage gate is applied before continuing any path.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .saturday_analytical import VegasRules, qualifies_for_day2, ticket_metrics, vegas_point_award

DRAW_RATES = (Fraction(0), Fraction(1,100), Fraction(1,50), Fraction(1,20))
OUTCOME_INCREMENTS = {"draw": (1,1), "a_win": (3,0), "b_win": (0,3)}


def _exact_probability(value) -> Fraction:
    if type(value) not in (int, Fraction) or not 0 <= value <= 1:
        raise ValueError("Use an exact Fraction probability between zero and one")
    return Fraction(value)


@dataclass(frozen=True)
class OutcomeProbabilities:
    win: Fraction
    draw: Fraction
    loss: Fraction

    def __post_init__(self):
        for name in ("win", "draw", "loss"):
            object.__setattr__(self, name, _exact_probability(getattr(self, name)))
        if self.win + self.draw + self.loss != 1:
            raise ValueError("W/D/L probabilities must sum to exactly one")


def equal_skill_outcomes(draw_rate: Fraction) -> OutcomeProbabilities:
    draw = _exact_probability(draw_rate)
    return OutcomeProbabilities((1-draw)/2, draw, (1-draw)/2)


def match_point_distribution(rounds: int, probabilities: OutcomeProbabilities) -> dict[int, Fraction]:
    """Coefficients of (p_loss + p_draw*z + p_win*z**3)**rounds."""
    if type(rounds) is not int or rounds < 0:
        raise ValueError("Round count must be a nonnegative integer")
    distribution = {0: Fraction(1)}
    for _ in range(rounds):
        next_distribution = {}
        for score, mass in distribution.items():
            for increment, probability in ((0, probabilities.loss), (1, probabilities.draw), (3, probabilities.win)):
                if probability:
                    point = score + increment
                    next_distribution[point] = next_distribution.get(point, Fraction(0)) + mass*probability
        distribution = next_distribution
    return {point: distribution.get(point,Fraction(0)) for point in range(3*rounds+1)}


@dataclass(frozen=True)
class DrawPointPath:
    day1_points: int
    qualifies: bool
    day2_points: int | None
    final_points: int
    tickets: int
    rounds_played: int
    probability: Fraction


def vegas_draw_paths(rules: VegasRules, probabilities: OutcomeProbabilities) -> tuple[DrawPointPath, ...]:
    first = match_point_distribution(rules.day1_rounds, probabilities)
    second = match_point_distribution(rules.day2_rounds, probabilities)
    paths = []
    for points, mass in first.items():
        if not mass:
            continue
        if not qualifies_for_day2(points,rules):
            paths.append(DrawPointPath(points,False,None,points,vegas_point_award(points,rules),rules.day1_rounds,mass))
        else:
            for extra_points, conditional_mass in second.items():
                if conditional_mass:
                    final = points + extra_points
                    paths.append(DrawPointPath(points,True,extra_points,final,vegas_point_award(final,rules),rules.total_rounds,mass*conditional_mass))
    if sum(p.probability for p in paths) != 1:
        raise ValueError("Gated path probabilities do not normalize")
    return tuple(paths)


def vegas_draw_final_points(rules: VegasRules, probabilities: OutcomeProbabilities) -> dict[int, Fraction]:
    result = {p: Fraction(0) for p in range(rules.maximum_match_points+1)}
    for path in vegas_draw_paths(rules, probabilities):
        result[path.final_points] += path.probability
    return result


def vegas_draw_ticket_distribution(rules: VegasRules, probabilities: OutcomeProbabilities) -> dict[int, Fraction]:
    result = {t: Fraction(0) for t in sorted({0, *(t for _, _, t in rules.point_tiers)})}
    for path in vegas_draw_paths(rules, probabilities):
        result[path.tickets] += path.probability
    return result


def vegas_draw_metrics(entrants: int, rules: VegasRules, probabilities: OutcomeProbabilities) -> dict:
    paths = vegas_draw_paths(rules, probabilities)
    qualification = sum((p.probability for p in paths if p.qualifies),Fraction(0))
    rounds = Fraction(rules.day1_rounds) + rules.day2_rounds*qualification
    result = ticket_metrics(vegas_draw_ticket_distribution(rules,probabilities),entrants,rounds)
    result.update({"qualification_probability":qualification, "expected_day2_entrants":entrants*qualification,
                   "expected_rounds_played_per_entrant":rounds,
                   "at_least_40_given_qualified":result["at_least_40_probability"]/qualification if qualification else Fraction(0)})
    return result


def expected_sunday_award(post_day1_points: int, rules: VegasRules, probabilities: OutcomeProbabilities) -> Fraction:
    """At the end of Round 6: zero if eliminated, conditional future EV if in.

    Qualification is not itself a prize. The award is settled after five more
    rounds for qualifiers, under the specified independent future W/D/L model.
    """
    if not qualifies_for_day2(post_day1_points,rules):
        return Fraction(0)
    return sum((mass*vegas_point_award(post_day1_points+extra,rules)
                for extra,mass in match_point_distribution(rules.day2_rounds,probabilities).items()),Fraction(0))


def feasible_no_prior_draw_scores(round_number: int, rules: VegasRules) -> tuple[int, ...]:
    """Individually feasible scores; no assertion that two such players pair.

    Round 11 paths must have passed the Round 6 gate. Multiples of three alone
    are insufficient: e.g. 9 points after ten rounds could not be in Day 2.
    """
    if round_number == rules.day1_rounds:
        return tuple(3*w for w in range(round_number))
    if round_number == rules.total_rounds:
        minimum_wins = (rules.day2_minimum_match_points+2)//3
        return tuple(3*w for w in range(minimum_wins,round_number))
    raise ValueError("Outcome matrices are scoped to Round 6 or Round 11")


def outcome_matrix(round_number: int, a_points: int, b_points: int, rules: VegasRules,
                   future_probabilities: OutcomeProbabilities | None = None) -> tuple[dict, ...]:
    feasible = feasible_no_prior_draw_scores(round_number,rules)
    if type(a_points) is not int or type(b_points) is not int or a_points not in feasible or b_points not in feasible:
        raise ValueError("Starting scores must be individually feasible without prior draws and satisfy the prior Day 2 gate")
    if round_number == rules.day1_rounds and future_probabilities is None:
        raise ValueError("Round 6 future expected awards require an explicit Sunday outcome model")
    if round_number == rules.total_rounds and future_probabilities is not None:
        raise ValueError("Round 11 settles awards; there are no future rounds")
    rows = []
    for outcome,(a_increment,b_increment) in OUTCOME_INCREMENTS.items():
        a_post,b_post = a_points+a_increment,b_points+b_increment
        row = {"round":round_number,"a_start_points":a_points,"b_start_points":b_points,"equal_start_points":a_points==b_points,
               "outcome":outcome,"a_points_added":a_increment,"b_points_added":b_increment,
               "a_post_points":a_post,"b_post_points":b_post,
               "feasibility_scope":"individual_no_prior_draw_path_feasible_joint_swiss_pairing_not_verified"}
        if round_number == rules.total_rounds:
            a_award,b_award = vegas_point_award(a_post,rules),vegas_point_award(b_post,rules)
            row.update({"a_tickets":a_award,"b_tickets":b_award,"combined_tickets":a_award+b_award})
            row.update({"earning_players":int(a_award>0)+int(b_award>0),
                        "players_at_least_40":int(a_award>=40)+int(b_award>=40),
                        "players_at_least_80":int(a_award>=80)+int(b_award>=80)})
        else:
            a_qual,b_qual = qualifies_for_day2(a_post,rules),qualifies_for_day2(b_post,rules)
            a_ev,b_ev = expected_sunday_award(a_post,rules,future_probabilities),expected_sunday_award(b_post,rules,future_probabilities)
            row.update({"a_qualifies_day2":a_qual,"b_qualifies_day2":b_qual,"qualified_players":int(a_qual)+int(b_qual),
                        "a_future_expected_tickets":a_ev,"b_future_expected_tickets":b_ev,"future_combined_expected_tickets":a_ev+b_ev})
        rows.append(row)
    metrics = ("combined_tickets",) if round_number==rules.total_rounds else ("qualified_players","future_combined_expected_tickets")
    for metric in metrics:
        draw,a_win,b_win = [row[metric] for row in rows]
        deltas = {"draw_minus_a_win_"+metric:draw-a_win, "draw_minus_b_win_"+metric:draw-b_win,
                  "a_win_minus_b_win_"+metric:a_win-b_win,
                  "all_outcomes_equal_"+metric:draw==a_win==b_win}
        for row in rows:
            row.update(deltas)
    return tuple(rows)
