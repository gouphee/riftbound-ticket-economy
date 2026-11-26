"""Exact individual checkpoint probabilities; not a Swiss pairing simulator."""
from collections import defaultdict
from fractions import Fraction as F
from math import comb

from .saturday_analytical import _probability, vegas_point_award

PERFORMANCE = tuple(F(n, 10) for n in range(4, 9))
DRAWS = (F(0), F(1, 100), F(1, 50), F(1, 20))


def record_distribution(rounds, p, d=F(0)):
    """p is P(win | decisive), d is an independent per-match draw probability."""
    p, d = _probability(p), _probability(d)
    if type(rounds) is not int or rounds < 0:
        raise ValueError('Invalid round count')
    w, loss = (1-d)*p, (1-d)*(1-p)
    return {(wins, rounds-wins-draws, draws):
            comb(rounds, wins)*comb(rounds-wins, draws)*w**wins*loss**(rounds-wins-draws)*d**draws
            for wins in range(rounds+1) for draws in range(rounds-wins+1)}


def gated_checkpoint(rules, p, d=F(0)):
    """Unconditional entry mass at R10, plus mass stopped after R6. No renormalizing."""
    first = record_distribution(rules.day1_rounds, p, d)
    rest = record_distribution(rules.day2_rounds-1, p, d)
    reached, stopped = defaultdict(F), F(0)
    for (w, l, draw), mass in first.items():
        if 3*w+draw < rules.day2_minimum_match_points:
            stopped += mass
            continue
        for (ew, el, ed), extra in rest.items():
            reached[w+ew, l+el, draw+ed] += mass*extra
    if sum(reached.values())+stopped != 1:
        raise ValueError('Gate probability does not normalize')
    return dict(reached), stopped


def strong_record_metrics(p, d, rules):
    old = record_distribution(6, p, d)
    new, stopped = gated_checkpoint(rules, p, d)
    return {'historical_exact_5_1': old[5, 1, 0],
            'vegas_exact_8_2': new.get((8, 2, 0), F(0)),
            'historical_at_least_5_wins': sum(v for (w,l,x),v in old.items() if w>=5),
            'vegas_at_least_8_wins': sum(v for (w,l,x),v in new.items() if w>=8),
            'historical_at_least_15_points': sum(v for (w,l,x),v in old.items() if 3*w+x>=15),
            'vegas_at_least_24_points': sum(v for (w,l,x),v in new.items() if 3*w+x>=24),
            'historical_exact_6_0': old[6, 0, 0],
            'vegas_exact_10_0': new.get((10, 0, 0), F(0)),
            'vegas_reach_R10': 1-stopped, 'vegas_stopped_at_R6': stopped}


def bracket_distribution(q, arrangement='published'):
    """Conditional on a secured Top8 slot; decisive bracket win chance q each round.

    Stage splits pool only the remaining placement prizes. Previously eliminated
    players retain their published prizes. These are scenarios, not practice rates.
    """
    q = _probability(q)
    if arrangement == 'top8_equal':
        return {216: F(1)}
    if arrangement == 'top4_equal':
        return {144: 1-q, 288: q}
    if arrangement == 'top2_equal':
        return {144: 1-q, 216: q*(1-q), 360: q*q}
    if arrangement != 'published':
        raise ValueError('Unknown arrangement')
    return {144: 1-q, 216: q*(1-q), 288: q*q*(1-q), 432: q**3}


def expected(distribution):
    return sum(F(t)*v for t,v in distribution.items())


def last_round_rewards(wins, losses, p, d, rules):
    if (wins, losses) not in ((8,2), (9,1), (10,0)):
        raise ValueError('Expected no-draw R10 checkpoint')
    p, d = _probability(p), _probability(d)
    awards = {outcome: vegas_point_award(3*wins+extra, rules)
              for outcome,extra in (('win',3), ('draw',1), ('loss',0))}
    ev = (1-d)*p*awards['win']+d*awards['draw']+(1-d)*(1-p)*awards['loss']
    return {**{k+'_tickets': v for k,v in awards.items()}, 'expected_tickets': ev,
            'guaranteed_tickets_if_completed_eligible': min(awards.values()),
            'maximum_possible_tickets': max(awards.values())}
