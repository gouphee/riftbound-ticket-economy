import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

from riftbound_tickets.phase3a import read_csv, sha256
from riftbound_tickets.phase3b import TABLE_NAMES, audit, build, preservation_check

ROOT = Path(__file__).resolve().parents[1]


class Phase3BOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('riftbound_tickets.collectors.evidence.urlopen',side_effect=AssertionError('Phase 3B must be offline')):
            cls.report = build(ROOT)

    def test_required_scenarios_and_fractional_expected_counts(self):
        rows = read_csv(ROOT/'outputs/tables/saturday_draw_sensitivity.csv')
        self.assertEqual(len(rows),8)
        self.assertEqual({r['draw_rate_exact'] for r in rows},{'0','1/100','1/50','1/20'})
        self.assertEqual({r['entrants'] for r in rows},{'512','1024'})
        for row in rows:
            if row['draw_rate_exact']=='1/50':
                self.assertNotEqual(F(row['expected_day2_entrants_exact']).denominator,1)
                self.assertNotEqual(F(row['expected_entries_at_least_40_exact']).denominator,1)

    def test_exported_pmfs_normalize_and_complete_point_range(self):
        tickets = read_csv(ROOT/'outputs/tables/saturday_draw_ticket_distributions.csv')
        points = read_csv(ROOT/'outputs/tables/saturday_draw_final_points.csv')
        for scenario in {r['draw_scenario'] for r in tickets}:
            award_rows = [r for r in tickets if r['draw_scenario']==scenario]
            point_rows = [r for r in points if r['draw_scenario']==scenario]
            self.assertEqual(sum(F(r['probability_exact']) for r in award_rows),1)
            self.assertEqual(sum(F(r['probability_exact']) for r in point_rows),1)
            self.assertEqual({int(r['final_match_points']) for r in point_rows},set(range(34)))

    def test_historical_comparisons_reuse_all_original_scenarios(self):
        rows = read_csv(ROOT/'outputs/tables/saturday_draw_historical_comparison.csv')
        self.assertEqual(len(rows),96)
        self.assertEqual(len({r['observed_historical_event_key'] for r in rows if r['observed_historical_event_key']}),8)
        for row in rows:
            self.assertEqual(F(row['historical_expected_total_tickets_exact']),4992)
            if row['scenario_id']=='equal-1024':
                self.assertEqual(row['historical_attendance_status'],'hypothetical_beyond_published_cap')
            if row['scenario_id']=='observed-barcelona-saturday':
                self.assertEqual(row['historical_attendance_status'],'observed_over_advertised_cap_exception')

    def test_complete_outcome_grid_and_separate_ev_columns(self):
        rows = read_csv(ROOT/'outputs/tables/saturday_final_round_outcomes.csv')
        terminal = [r for r in rows if r['round']=='11']
        gate = [r for r in rows if r['round']=='6']
        self.assertEqual(len(terminal),7*7*3)
        self.assertEqual(len(gate),6*6*3*4)
        self.assertTrue(all(r['future_combined_expected_tickets_exact']=='' for r in terminal))
        self.assertTrue(all(r['combined_tickets']=='' for r in gate))

    def test_rebuild_is_offline_and_byte_identical(self):
        paths = [ROOT/'outputs/tables'/name for name in TABLE_NAMES]
        before = [sha256(p) for p in paths]
        with patch('riftbound_tickets.collectors.evidence.urlopen',side_effect=AssertionError('Offline build used network')):
            build(ROOT)
        self.assertEqual(before,[sha256(p) for p in paths])

    def test_all_previous_artifacts_preserved(self):
        check = preservation_check(ROOT)
        self.assertEqual(check['checked_files'],750)
        self.assertTrue(check['passed'],check['changed_files'])

    def test_new_hash_recalculation_and_figure_audit(self):
        result = audit(ROOT,write=False)
        self.assertTrue(result['passed'],result)
        self.assertTrue(result['zero_draw_reproduces_phase3a'])


if __name__=='__main__':
    unittest.main()
