import unittest
from collections import defaultdict
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from riftbound_tickets.collectors.phase3a_sources import (
    ELEVENTH_ROUND_ANNOUNCEMENT, Phase3ASourceStore, parse_vegas_schedule,
    verify_announcement_content,
)
from riftbound_tickets.models.saturday_analytical import (
    binomial_probabilities, historical_metrics, historical_ticket_distribution,
    qualifies_for_day2, upper_tail_ticket_share, vegas_final_point_distribution,
    vegas_metrics, vegas_paths, vegas_point_award, vegas_ticket_distribution,
)
from riftbound_tickets.phase3a import rules_from_archive

ROOT = Path(__file__).resolve().parents[1]


class ExactSaturdayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archived, cls.rules = rules_from_archive(ROOT)

    def test_binomial_normalizes_exactly(self):
        for rounds in (0, 5, 6, 11):
            for p in (F(0), F(1,2), F(1)):
                values = binomial_probabilities(rounds, p)
                self.assertEqual(sum(values.values()), 1)
                self.assertTrue(all(isinstance(v, F) for v in values.values()))
        self.assertEqual(binomial_probabilities(6)[4], F(15,64))

    def test_rejects_approximate_probabilities_and_bad_rounds(self):
        for p in (.5, True, F(-1,2), F(3,2)):
            with self.assertRaises(ValueError):
                binomial_probabilities(6, p)
        for rounds in (-1, True, 6.0):
            with self.assertRaises(ValueError):
                binomial_probabilities(rounds)

    def test_point_gate_boundary(self):
        self.assertFalse(qualifies_for_day2(11, self.rules))
        self.assertTrue(qualifies_for_day2(12, self.rules))
        self.assertEqual(vegas_metrics(512,self.rules)['qualification_probability'], F(11,32))

    def test_nonqualifiers_never_play_sunday(self):
        paths = vegas_paths(self.rules)
        self.assertEqual(len(paths), 22)
        self.assertEqual(sum(p.probability for p in paths), 1)
        for path in paths:
            if path.day1_wins < 4:
                self.assertFalse(path.qualifies)
                self.assertIsNone(path.day2_wins)
                self.assertEqual(path.scheduled_rounds, 6)
                self.assertEqual(path.final_points, path.day1_points)
                self.assertEqual(path.tickets, 0)
            else:
                self.assertTrue(path.qualifies)
                self.assertEqual(path.scheduled_rounds, 11)
                self.assertEqual(path.final_points, 3*(path.day1_wins+path.day2_wins))

    def test_conditional_day2_is_five_round_binomial(self):
        paths = vegas_paths(self.rules)
        first = binomial_probabilities(6)
        for k in (4,5,6):
            self.assertEqual({p.day2_wins: p.probability/first[k] for p in paths if p.day1_wins==k}, binomial_probabilities(5))

    def test_full_point_table_boundaries_including_inaccessible_bands(self):
        expected = {**{p:0 for p in range(19)},19:10,20:10,21:20,22:25,23:25,24:30,
                    25:35,26:35,27:40,28:50,29:50,30:60,31:70,32:70,33:80}
        for points, award in expected.items():
            self.assertEqual(vegas_point_award(points,self.rules), award)
        for invalid in (-1,34,12.0,True):
            with self.assertRaises(ValueError):
                vegas_point_award(invalid,self.rules)

    def test_zero_ticket_qualification_outcome(self):
        # Even 6-0 then 0-5 earns zero tickets at 18 points.
        path = next(p for p in vegas_paths(self.rules) if p.day1_wins==6 and p.day2_wins==0)
        self.assertTrue(path.qualifies)
        self.assertEqual((path.final_points,path.tickets),(18,0))

    def test_exact_ticket_pmf(self):
        expected = {0:F(1621,2048),10:F(0),20:F(215,2048),25:F(0),30:F(145,2048),35:F(0),
                    40:F(55,2048),50:F(0),60:F(11,2048),70:F(0),80:F(1,2048)}
        self.assertEqual(vegas_ticket_distribution(self.rules),expected)
        self.assertEqual(sum(expected.values()),1)

    def test_no_draw_inaccessible_tiers_retained_as_zero(self):
        pmf = vegas_ticket_distribution(self.rules)
        self.assertTrue(all(pmf[t]==0 for t in (10,25,35,50,70)))
        points = vegas_final_point_distribution(self.rules)
        self.assertTrue(all(p==0 for point,p in points.items() if point%3))
        self.assertEqual(sum(points.values()),1)

    def test_gate_changes_seven_and_eight_win_states(self):
        points = vegas_final_point_distribution(self.rules)
        self.assertEqual(points[21],F(215,2048))
        self.assertEqual(points[24],F(145,2048))
        self.assertNotEqual(points[21],binomial_probabilities(11)[7])
        self.assertNotEqual(points[24],binomial_probabilities(11)[8])

    def test_independent_exhaustive_binary_path_check(self):
        # Test oracle only: enumerate all 2^11 binary strings, gate before
        # consuming the suffix. No joint tournament/pairing simulation.
        pmf = defaultdict(F)
        for outcomes in product((0,1),repeat=11):
            first = sum(outcomes[:6])
            wins = first + (sum(outcomes[6:]) if first>=4 else 0)
            award = {7:20,8:30,9:40,10:60,11:80}.get(wins,0)
            pmf[award] += F(1,2048)
        self.assertEqual(dict(pmf),{t:p for t,p in vegas_ticket_distribution(self.rules).items() if p})

    def test_reference_expected_values_and_rounds(self):
        old,new = historical_metrics(512),vegas_metrics(512,self.rules)
        self.assertEqual(old['at_least_40_probability'],F(1,16))
        self.assertEqual(old['expected_tickets_per_entrant'],F(39,4))
        self.assertEqual(new['at_least_40_probability'],F(67,2048))
        self.assertEqual(new['expected_tickets_per_entrant'],F(5795,1024))
        self.assertEqual(new['zero_ticket_probability'],F(1621,2048))
        self.assertEqual(new['expected_scheduled_rounds_per_entrant'],F(247,32))
        self.assertEqual(old['expected_scheduled_rounds_per_entrant'],7+F(14,512))

    def test_historical_pool_and_attendance_normalization(self):
        for n in (128,132,256,512,1024):
            for split in (False,True):
                old = historical_metrics(n,split_top8=split)
                self.assertEqual(old['expected_total_tickets'],4992)
                self.assertEqual(old['at_least_40_probability'],F(32,n))
                self.assertEqual(old['at_least_80_probability'],F(8,n))
                self.assertEqual(old['zero_ticket_probability'],F(n-128,n))
                self.assertEqual(old['expected_tickets_per_entrant'],F(4992,n))
                self.assertEqual(sum(historical_ticket_distribution(n,split_top8=split).values()),1)

    def test_split_conserves_tickets_and_thresholds(self):
        old,split = historical_metrics(512),historical_metrics(512,split_top8=True)
        for field in ('expected_total_tickets','expected_tickets_per_entrant','at_least_40_probability','at_least_80_probability'):
            self.assertEqual(old[field],split[field])
        self.assertEqual((old['maximum_individual_payout'],split['maximum_individual_payout']),(432,216))
        self.assertLess(split['marginal_ticket_gini'],old['marginal_ticket_gini'])
        pmf = historical_ticket_distribution(512)
        self.assertEqual(upper_tail_ticket_share(pmf,F(8,512)),F(9,26))
        self.assertEqual(upper_tail_ticket_share(pmf,F(32,512)),F(8,13))

    def test_vegas_total_scales_not_individual_probabilities(self):
        for n in (256,512,1024):
            metrics = vegas_metrics(n,self.rules)
            self.assertEqual(metrics['expected_total_tickets'],n*F(5795,1024))
            self.assertEqual(metrics['at_least_40_probability'],F(67,2048))

    def test_eleven_round_structure_and_stale_prose(self):
        self.assertEqual(self.rules.total_rounds,11)
        self.assertEqual(self.rules.maximum_match_points,33)
        self.assertEqual(self.archived['obsolete_award_round_references'],[10,10])
        with self.assertRaises(ValueError):
            replace(self.rules,day2_rounds=4)

    def test_primary_announcement_verified_by_content(self):
        store = Phase3ASourceStore(ROOT)
        html = store.read(store.archived(ELEVENTH_ROUND_ANNOUNCEMENT)).decode()
        self.assertTrue(verify_announcement_content(html)['verified_primary_announcement_content'])
        self.assertFalse(verify_announcement_content('<html>HTTP 200 but no post</html>')['verified_primary_announcement_content'])

    def test_schedule_parser_fails_on_incomplete_payout_table(self):
        store = Phase3ASourceStore(ROOT)
        html = store.read(self.archived['source']).decode()
        self.assertEqual(parse_vegas_schedule(html)['point_tiers'],self.archived['point_tiers'])
        # Test a broken archived payout band rather than substituting a default.
        with self.assertRaises(ValueError):
            parse_vegas_schedule(html.replace('19-20 Match Points','18-20 Match Points'))

    def test_historical_requires_full_funded_field(self):
        for n in (0,127,128.0,True):
            with self.assertRaises(ValueError):
                historical_ticket_distribution(n)


if __name__ == '__main__':
    unittest.main()
