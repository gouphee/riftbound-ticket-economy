import unittest
from collections import defaultdict
from fractions import Fraction as F
from math import factorial
from pathlib import Path

from riftbound_tickets.models.saturday_analytical import vegas_final_point_distribution, vegas_metrics, vegas_point_award, vegas_ticket_distribution
from riftbound_tickets.models.saturday_draws import (
    DRAW_RATES, OutcomeProbabilities, equal_skill_outcomes, expected_sunday_award,
    feasible_no_prior_draw_scores, match_point_distribution, outcome_matrix,
    vegas_draw_final_points, vegas_draw_metrics, vegas_draw_paths, vegas_draw_ticket_distribution,
)
from riftbound_tickets.phase3a import rules_from_archive

ROOT = Path(__file__).resolve().parents[1]


def multinomial_records(rounds, probabilities):
    """Independent combinatorial test oracle, not the point DP."""
    for wins in range(rounds+1):
        for draws in range(rounds-wins+1):
            losses = rounds-wins-draws
            count = factorial(rounds)//(factorial(wins)*factorial(draws)*factorial(losses))
            mass = count*probabilities.win**wins*probabilities.draw**draws*probabilities.loss**losses
            yield 3*wins+draws,mass


class DrawModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.rules = rules_from_archive(ROOT)

    def test_probability_inputs_are_exact_and_normalized(self):
        for rate in DRAW_RATES:
            p = equal_skill_outcomes(rate)
            self.assertEqual(p.win,p.loss)
            self.assertEqual(p.win+p.draw+p.loss,1)
        for invalid in (.02,True,F(-1,2),F(3,2)):
            with self.assertRaises(ValueError):
                equal_skill_outcomes(invalid)
        with self.assertRaises(ValueError):
            OutcomeProbabilities(F(1,2),F(1,2),F(1,2))

    def test_generating_function_normalization_and_mean(self):
        for rate in DRAW_RATES:
            p = equal_skill_outcomes(rate)
            for rounds in (0,1,5,6,11):
                pmf = match_point_distribution(rounds,p)
                self.assertEqual(sum(pmf.values()),1)
                self.assertEqual(sum(points*mass for points,mass in pmf.items()),rounds*(3*p.win+p.draw))
                self.assertTrue(all(isinstance(mass,F) for mass in pmf.values()))
        for invalid in (-1,True,6.0):
            with self.assertRaises(ValueError):
                match_point_distribution(invalid,equal_skill_outcomes(F(0)))

    def test_independent_multinomial_oracle_with_gate(self):
        for rate in DRAW_RATES:
            p = equal_skill_outcomes(rate)
            expected = defaultdict(F)
            for first,mass in multinomial_records(6,p):
                if first < 12:
                    expected[first] += mass
                else:
                    for extra,conditional in multinomial_records(5,p):
                        expected[first+extra] += mass*conditional
            self.assertEqual(vegas_draw_final_points(self.rules,p),{s:expected[s] for s in range(34)})

    def test_full_final_and_ticket_pmfs_normalize(self):
        for rate in DRAW_RATES:
            p = equal_skill_outcomes(rate)
            self.assertEqual(sum(vegas_draw_final_points(self.rules,p).values()),1)
            self.assertEqual(sum(vegas_draw_ticket_distribution(self.rules,p).values()),1)
            self.assertEqual(sum(path.probability for path in vegas_draw_paths(self.rules,p)),1)

    def test_zero_draw_extension_equals_all_phase3a_metrics(self):
        p = equal_skill_outcomes(F(0))
        self.assertEqual(vegas_draw_final_points(self.rules,p),vegas_final_point_distribution(self.rules))
        self.assertEqual(vegas_draw_ticket_distribution(self.rules,p),vegas_ticket_distribution(self.rules))
        for n in (512,1024):
            new,old = vegas_draw_metrics(n,self.rules,p),vegas_metrics(n,self.rules)
            for key,value in old.items():
                self.assertEqual(new[key],value)

    def test_reference_zero_draw_metrics(self):
        m = vegas_draw_metrics(1024,self.rules,equal_skill_outcomes(F(0)))
        self.assertEqual(m['qualification_probability'],F(11,32))
        self.assertEqual(m['at_least_40_probability'],F(67,2048))
        self.assertEqual(m['expected_tickets_per_entrant'],F(5795,1024))
        self.assertEqual(m['expected_total_tickets'],5795)

    def test_reference_two_percent_draw_metrics(self):
        m = vegas_draw_metrics(1024,self.rules,equal_skill_outcomes(F(1,50)))
        self.assertAlmostEqual(float(m['expected_day2_entrants']),333.016318208,places=10)
        self.assertAlmostEqual(float(m['at_least_40_probability']),.028166985715897448,places=14)
        self.assertAlmostEqual(float(m['expected_tickets_per_entrant']),5.408622742308486,places=12)
        self.assertAlmostEqual(float(m['expected_total_tickets']),5538.42968812389,places=8)

    def test_gate_is_applied_to_points_not_four_win_shortcut(self):
        # Three wins and three draws is 12 points after six rounds.
        p = equal_skill_outcomes(F(1,50))
        self.assertGreater(20*p.win**3*p.draw**3,0)
        first = match_point_distribution(6,p)
        self.assertEqual(vegas_draw_metrics(1,self.rules,p)['qualification_probability'],sum(first[s] for s in range(12,19)))
        self.assertTrue(all(path.qualifies for path in vegas_draw_paths(self.rules,p) if path.day1_points==12))

    def test_eliminated_paths_never_receive_sunday_points(self):
        for rate in DRAW_RATES:
            for path in vegas_draw_paths(self.rules,equal_skill_outcomes(rate)):
                if path.day1_points < 12:
                    self.assertFalse(path.qualifies)
                    self.assertIsNone(path.day2_points)
                    self.assertEqual(path.final_points,path.day1_points)
                    self.assertEqual((path.rounds_played,path.tickets),(6,0))
                else:
                    self.assertTrue(path.qualifies)
                    self.assertEqual(path.rounds_played,11)

    def test_draw_accessible_payout_bands_and_impossible_32_points(self):
        p = equal_skill_outcomes(F(1,50))
        pmf = vegas_draw_ticket_distribution(self.rules,p)
        for award in (10,25,35,50,70):
            self.assertGreater(pmf[award],0)
        self.assertEqual(vegas_draw_final_points(self.rules,p)[32],0)
        self.assertEqual(match_point_distribution(6,p)[17],0)
        self.assertEqual(match_point_distribution(5,p)[14],0)

    def test_complete_official_thresholds(self):
        expected = {**{s:0 for s in range(19)},19:10,20:10,21:20,22:25,23:25,24:30,25:35,26:35,27:40,28:50,29:50,30:60,31:70,32:70,33:80}
        self.assertEqual({s:vegas_point_award(s,self.rules) for s in range(34)},expected)

    def test_expectations_scale_without_rounding_counts(self):
        p = equal_skill_outcomes(F(1,50))
        small,large = [vegas_draw_metrics(n,self.rules,p) for n in (512,1024)]
        for field in ('expected_total_tickets','expected_day2_entrants','expected_entries_at_least_40'):
            self.assertEqual(large[field],2*small[field])
            self.assertNotEqual(large[field].denominator,1)
        self.assertEqual(large['expected_rounds_played_per_entrant'],6+5*large['qualification_probability'])

    def test_degenerate_all_draw_win_loss_cases(self):
        for probabilities,expected in ((OutcomeProbabilities(0,1,0),(0,0,6)),
                                       (OutcomeProbabilities(1,0,0),(1,80,11)),
                                       (OutcomeProbabilities(0,0,1),(0,0,6))):
            m = vegas_draw_metrics(1,self.rules,probabilities)
            self.assertEqual((m['qualification_probability'],m['expected_tickets_per_entrant'],m['expected_rounds_played_per_entrant']),expected)


class LocalOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.rules = rules_from_archive(ROOT)

    def test_individually_feasible_no_prior_draw_scores(self):
        self.assertEqual(feasible_no_prior_draw_scores(6,self.rules),(0,3,6,9,12,15))
        self.assertEqual(feasible_no_prior_draw_scores(11,self.rules),(12,15,18,21,24,27,30))
        for round_,score in ((11,9),(11,31),(6,18),(6,10),(11,True)):
            with self.assertRaises(ValueError):
                outcome_matrix(round_,score,12,self.rules,equal_skill_outcomes(F(0)) if round_==6 else None)

    def test_rejects_missing_future_model_and_extra_terminal_rounds(self):
        with self.assertRaises(ValueError):
            outcome_matrix(6,9,9,self.rules)
        with self.assertRaises(ValueError):
            outcome_matrix(11,18,18,self.rules,equal_skill_outcomes(F(0)))
        with self.assertRaises(ValueError):
            feasible_no_prior_draw_scores(10,self.rules)

    def test_all_seven_equal_score_terminal_cases_conserve_combined_tickets(self):
        totals = (0,0,20,50,70,100,140)
        for score,total in zip(feasible_no_prior_draw_scores(11,self.rules),totals):
            rows = outcome_matrix(11,score,score,self.rules)
            self.assertEqual([r['combined_tickets'] for r in rows],[total]*3)
            self.assertTrue(all(r['all_outcomes_equal_combined_tickets'] for r in rows))
            self.assertTrue(all('joint_swiss_pairing_not_verified' in r['feasibility_scope'] for r in rows))

    def test_equal_terminal_distribution_changes_without_pool_change(self):
        rows = outcome_matrix(11,18,18,self.rules)
        self.assertEqual([(r['a_tickets'],r['b_tickets']) for r in rows],[(10,10),(20,0),(0,20)])
        rows = outcome_matrix(11,27,27,self.rules)
        self.assertEqual([(r['a_tickets'],r['b_tickets']) for r in rows],[(50,50),(60,40),(40,60)])

    def test_unequal_terminal_scores_can_change_combined_total(self):
        rows = outcome_matrix(11,18,21,self.rules)
        self.assertEqual([r['combined_tickets'] for r in rows],[35,40,30])
        self.assertEqual(rows[0]['draw_minus_a_win_combined_tickets'],-5)
        self.assertEqual(rows[0]['draw_minus_b_win_combined_tickets'],5)
        self.assertFalse(rows[0]['all_outcomes_equal_combined_tickets'])

    def test_some_unequal_terminal_scores_also_conserve_total(self):
        rows = outcome_matrix(11,21,24,self.rules)
        self.assertEqual([r['combined_tickets'] for r in rows],[60,60,60])

    def test_terminal_draw_is_midpoint_of_decisive_totals(self):
        for a in feasible_no_prior_draw_scores(11,self.rules):
            for b in feasible_no_prior_draw_scores(11,self.rules):
                draw,a_win,b_win = outcome_matrix(11,a,b,self.rules)
                self.assertEqual(2*draw['combined_tickets'],a_win['combined_tickets']+b_win['combined_tickets'])

    def test_equal_pool_can_change_number_reaching_40(self):
        draw,a_win,b_win = outcome_matrix(11,24,24,self.rules)
        self.assertEqual([r['combined_tickets'] for r in (draw,a_win,b_win)],[70,70,70])
        self.assertEqual([r['players_at_least_40'] for r in (draw,a_win,b_win)],[0,1,1])

    def test_round6_equal_nine_points_draw_eliminates_both(self):
        rows = outcome_matrix(6,9,9,self.rules,equal_skill_outcomes(F(0)))
        self.assertEqual([r['qualified_players'] for r in rows],[0,1,1])
        self.assertEqual([r['future_combined_expected_tickets'] for r in rows],[F(0),F(195,16),F(195,16)])
        self.assertTrue(all('combined_tickets' not in r for r in rows))

    def test_round6_unequal_scores_qualification_and_ev_are_separate(self):
        rows = outcome_matrix(6,9,12,self.rules,equal_skill_outcomes(F(0)))
        self.assertEqual([r['qualified_players'] for r in rows],[1,2,1])
        self.assertNotEqual(rows[0]['future_combined_expected_tickets'],rows[2]['future_combined_expected_tickets'])
        self.assertEqual(expected_sunday_award(11,self.rules,equal_skill_outcomes(F(0))),0)
        self.assertEqual(expected_sunday_award(12,self.rules,equal_skill_outcomes(F(0))),F(195,16))

    def test_round6_equal_twelve_zero_future_draw_identity(self):
        rows = outcome_matrix(6,12,12,self.rules,equal_skill_outcomes(F(0)))
        self.assertEqual([r['qualified_players'] for r in rows],[2,2,2])
        self.assertEqual([r['future_combined_expected_tickets'] for r in rows],[F(575,16)]*3)

    def test_round6_equal_twelve_future_draws_break_ev_identity(self):
        rows = outcome_matrix(6,12,12,self.rules,equal_skill_outcomes(F(1,50)))
        self.assertEqual([r['qualified_players'] for r in rows],[2,2,2])
        self.assertLess(rows[0]['future_combined_expected_tickets'],rows[1]['future_combined_expected_tickets'])
        self.assertFalse(rows[0]['all_outcomes_equal_future_combined_expected_tickets'])

    def test_round11_orientation_symmetry_and_point_awards(self):
        for a in feasible_no_prior_draw_scores(11,self.rules):
            for b in feasible_no_prior_draw_scores(11,self.rules):
                rows,mirror = outcome_matrix(11,a,b,self.rules),outcome_matrix(11,b,a,self.rules)
                self.assertEqual(rows[0]['combined_tickets'],mirror[0]['combined_tickets'])
                self.assertEqual(rows[1]['combined_tickets'],mirror[2]['combined_tickets'])
                for row in rows:
                    self.assertEqual(row['a_post_points'],a+row['a_points_added'])
                    self.assertEqual(row['b_post_points'],b+row['b_points_added'])
                    self.assertEqual(row['combined_tickets'],row['a_tickets']+row['b_tickets'])


if __name__=='__main__':
    unittest.main()
