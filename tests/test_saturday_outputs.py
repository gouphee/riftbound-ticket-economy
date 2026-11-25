import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

from riftbound_tickets.phase3a import (
    TABLE_NAMES, audit, build, historical_inputs,
    preserved_artifacts_check, read_csv, sha256,
)

ROOT = Path(__file__).resolve().parents[1]


class SaturdayOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('riftbound_tickets.collectors.evidence.urlopen',side_effect=AssertionError('Analytical build must be offline')):
            cls.report = build(ROOT)
        cls.rows = read_csv(ROOT/'outputs/tables/saturday_analytical_comparison.csv')

    def test_all_scenarios_and_observed_fields(self):
        self.assertEqual(len(self.rows),24)
        old,_ = historical_inputs(ROOT)
        observed = {r['observed_historical_event_key']:int(r['historical_n']) for r in self.rows if r['observed_historical_event_key']}
        self.assertEqual(observed,{r['event_key']:int(r['observed_n']) for r in old})
        self.assertEqual(observed['utrecht-saturday'],505)

    def test_capacity_scenarios_are_labeled(self):
        rows = {r['scenario_id']:r for r in self.rows if r['historical_allocation']=='official_placement'}
        self.assertEqual(rows['equal-1024']['historical_attendance_status'],'hypothetical_beyond_published_cap')
        self.assertEqual(rows['observed-barcelona-saturday']['historical_attendance_status'],'observed_over_advertised_cap_exception')
        full = rows['published-full-caps']
        self.assertEqual((full['historical_n'],full['vegas_n']),('512','1024'))
        self.assertIn('not_attendance_forecast',full['scenario_kind'])

    def test_all_exported_pmfs_normalize_and_reproduce_totals(self):
        rows = read_csv(ROOT/'outputs/tables/saturday_ticket_distributions.csv')
        groups = {}
        for row in rows:
            groups.setdefault((row['scenario_id'],row['allocation']),[]).append(row)
        self.assertEqual(len(groups),36)
        for (_,allocation), group in groups.items():
            self.assertEqual(sum(F(r['probability_exact']) for r in group),1)
            total = sum(F(r['expected_total_ticket_contribution_exact']) for r in group)
            n = int(group[0]['entrants'])
            self.assertEqual(total, n*F(5795,1024) if allocation=='official_match_points' else 4992)

    def test_offline_rebuild_is_identical(self):
        paths = [ROOT/'outputs/tables'/p for p in TABLE_NAMES]
        before = [sha256(p) for p in paths]
        with patch('riftbound_tickets.collectors.evidence.urlopen',side_effect=AssertionError('Offline rebuild used network')):
            build(ROOT)
        self.assertEqual(before,[sha256(p) for p in paths])

    def test_archival_and_phase2_preservation(self):
        check = preserved_artifacts_check(ROOT)
        self.assertEqual(check['checked_files'],615)
        self.assertTrue(check['passed'],check['changed_files'])

    def test_independent_recalculation_and_sources_audit(self):
        result = audit(ROOT,write=False)
        self.assertTrue(result['passed'],result)
        self.assertEqual(result['source_objects_verified'],2)
        self.assertEqual(result['figure_hash_mismatches'],[])


if __name__ == '__main__':
    unittest.main()
