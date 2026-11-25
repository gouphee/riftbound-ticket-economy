"""Synthetic match fixtures exercise classification, not historical observations."""

import copy
import unittest

from riftbound_tickets.draws import classify_match, summarize_matches, unique_matches, wilson_interval


def match(**changes):
    value = {"id": 1, "tournament_round": 10, "status": "COMPLETE", "players": [1, 2],
             "match_type": "PLAYER_VS_PLAYER", "winning_player": 1, "match_is_bye": False,
             "is_ghost_match": False, "match_is_loss": False, "reports_are_in_conflict": False,
             "match_is_intentional_draw": False, "match_is_unintentional_draw": False}
    return {**value, **changes}


def collection(matches):
    return {"event_key": "synthetic", "match_sets": [{"round_id": 10, "round_number": 1,
             "phase_type": "SWISS", "complete": True, "rows": [{"row": m} for m in matches]}]}


class DrawTests(unittest.TestCase):
    def test_round_is_part_of_match_identity(self):
        c = collection([match()])
        c['match_sets'].append({'round_id':11,'round_number':2,'phase_type':'SWISS','complete':True,
                                'rows':[{'row':match(tournament_round=11)}]})
        self.assertEqual(len(unique_matches(c)),2)

    def test_duplicate_match_does_not_double_count_its_players(self):
        drawn = match(winning_player=None, match_is_intentional_draw=True)
        rows = unique_matches(collection([drawn, copy.deepcopy(drawn)]))
        self.assertEqual(len(rows), 1)
        classified = [{**r, **classify_match(r['match'])} for r in rows]
        result = summarize_matches(classified)
        self.assertEqual((result['drawn_matches'], result['completed_played_matches']), (1, 1))
        self.assertEqual(result['duplicate_occurrences_removed'], 1)

    def test_excludes_byes_non_games_ghosts_incomplete_and_conflicts(self):
        cases = [(dict(match_is_bye=True, players=[1]), 'bye'),
                 (dict(match_is_loss=True, players=[1], winning_player=None), 'non_game'),
                 (dict(is_ghost_match=True), 'ghost'), (dict(status='IN_PROGRESS'), 'incomplete'),
                 (dict(reports_are_in_conflict=True), 'conflicted')]
        for changes, expected in cases:
            with self.subTest(expected=expected):
                result = classify_match(match(**changes))
                self.assertFalse(result['included_in_draw_denominator'])
                self.assertEqual(result['exclusion_reason'], expected)

    def test_missing_winner_is_not_assumed_draw(self):
        result = classify_match(match(winning_player=None))
        self.assertEqual(result['exclusion_reason'], 'unknown_result')
        self.assertIsNone(result['explicit_draw'])

    def test_conflicting_duplicates_are_excluded(self):
        rows = unique_matches(collection([match(), match(winning_player=2)]))
        self.assertTrue(rows[0]['duplicate_conflict'])
        self.assertFalse(classify_match(rows[0]['match'], duplicate_conflict=True)['included_in_draw_denominator'])

    def test_draw_subtypes_and_winner_conflict(self):
        self.assertEqual(classify_match(match(winning_player=None, match_is_intentional_draw=True))['draw_type'], 'intentional')
        self.assertEqual(classify_match(match(winning_player=None, match_is_unintentional_draw=True))['draw_type'], 'unintentional')
        self.assertEqual(classify_match(match(match_is_unintentional_draw=True))['exclusion_reason'], 'conflicted')
        both = classify_match(match(winning_player=None, match_is_intentional_draw=True, match_is_unintentional_draw=True))
        self.assertTrue(both['explicit_draw'])
        self.assertEqual(both['draw_type'], 'ambiguous_both_flags')

    def test_weighted_rate_and_uncertain_result_sensitivity(self):
        rows = [classify_match(match()) for _ in range(8)]
        rows.append(classify_match(match(winning_player=None, match_is_unintentional_draw=True)))
        rows.append(classify_match(match(winning_player=None)))
        result = summarize_matches(rows)
        self.assertAlmostEqual(result['draw_rate'], 1/9)
        self.assertEqual(result['unknown_result_sensitivity_low'], .1)
        self.assertEqual(result['unknown_result_sensitivity_high'], .2)

    def test_empty_round_rate_is_unknown_not_zero(self):
        result = summarize_matches([])
        self.assertIsNone(result['draw_rate'])
        self.assertEqual(wilson_interval(0, 0), (None, None))
        low, high = wilson_interval(10, 100)
        self.assertLess(low, .1)
        self.assertGreater(high, .1)
