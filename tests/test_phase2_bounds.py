"""Small exhaustive outcome search is independent of the analytic relaxation."""

import copy
import itertools
import unittest

from riftbound_tickets.models.historical_bounds import (
    construct_no_draw_swiss, no_draw_upper_bound, validate_construction,
)


def perfect_pairings(players):
    if not players:
        yield []
    else:
        a = players[0]
        for i, b in enumerate(players[1:], 1):
            for rest in perfect_pairings(players[1:i] + players[i+1:]):
                yield [(a, b), *rest]


def exhaustive_no_repeat_max(n, rounds, table):
    """All pairings/winners, at most one nonrepeated bye; no Swiss relaxation code."""
    best = 0

    def visit(number, wins, past, bye_history):
        nonlocal best
        if number == rounds:
            best = max(best, sum(table.get(w, 0) for w in wins))
            return
        byes = [p for p in range(n) if p not in bye_history] if n % 2 else [None]
        for bye in byes:
            for pairs in perfect_pairings([p for p in range(n) if p != bye]):
                edges = {tuple(sorted(pair)) for pair in pairs}
                if edges & past:
                    continue
                for winners in itertools.product(*pairs):
                    updated = list(wins)
                    for winner in winners:
                        updated[winner] += 1
                    if bye is not None:
                        updated[bye] += 1
                    visit(number + 1, updated, past | edges, bye_history | ({bye} if bye is not None else set()))
    visit(0, [0]*n, set(), set())
    return best


class TheoreticalBoundTests(unittest.TestCase):
    def test_bound_exceeds_small_brute_force_feasible_maxima(self):
        for n, rounds, table in [(4, 3, {2: 7, 3: 10}), (5, 2, {1: 3, 2: 8}), (6, 2, {2: 9})]:
            with self.subTest(n=n, rounds=rounds):
                exhaustive = exhaustive_no_repeat_max(n, rounds, table)
                ceiling = no_draw_upper_bound(n, rounds, table)
                self.assertGreaterEqual(ceiling['upper_bound_tickets'], exhaustive)
                self.assertIsNone(ceiling['exact_swiss_maximum'])
                self.assertIn('relaxed', ceiling['result_status'])

    def test_no_all_players_receive_maximum_personal_award(self):
        bound = no_draw_upper_bound(100, 6, {4:24, 5:36, 6:48})
        self.assertEqual(bound['upper_bound_tickets'], 2400)
        self.assertLess(bound['upper_bound_tickets'], 100*48)

    def test_odd_field_bye_budget_and_ticket_gcd(self):
        bound = no_draw_upper_bound(255, 6, {4:30, 5:40, 6:40})
        self.assertEqual(bound['no_draw_win_budget'], 6*128)
        self.assertEqual(bound['upper_bound_tickets'], 6140)
        self.assertEqual(bound['upper_bound_tickets'] % 10, 0)

    def test_swiss_construction_has_distinct_opponents_and_replays(self):
        for n, rounds in [(4,3), (5,3), (8,3), (255,6), (1019,6)]:
            table = {rounds: 45, rounds-1: 30, rounds-2: 15}
            witness = construct_no_draw_swiss(n, rounds, table)
            validate_construction(witness, table)
            self.assertLessEqual(witness['constructed_tickets'], no_draw_upper_bound(n, rounds, table)['upper_bound_tickets'])
            self.assertEqual(sum(witness['final_win_counts'].values()), n)

    def test_constructed_pairing_tamper_is_detected(self):
        witness = construct_no_draw_swiss(8, 3, {2:15, 3:45})
        bad = copy.deepcopy(witness)
        bad['rounds_witness'][1]['pairings'] = copy.deepcopy(bad['rounds_witness'][0]['pairings'])
        with self.assertRaises(ValueError):
            validate_construction(bad, {2:15, 3:45})

    def test_impossible_unique_opponent_reference_rejected(self):
        with self.assertRaises(ValueError):
            no_draw_upper_bound(4, 4, {4:40})
