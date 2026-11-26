import json
import unittest
from fractions import Fraction as F
from pathlib import Path
from riftbound_tickets.phase3a import read_csv
from riftbound_tickets.phase5 import baseline_weekends,preservation

ROOT=Path(__file__).resolve().parents[1]


class Phase5Outputs(unittest.TestCase):
    def test_prior_research_is_preserved(self):
        self.assertTrue(preservation(ROOT)['passed'])

    def test_team_pmfs_normalize_and_match_means(self):
        groups={}
        for r in read_csv(ROOT/'outputs/tables/phase5_team_distributions.csv'):
            key=tuple(r[k] for k in ('event_id','team_decisive_win_probability_exact','draw_rate_exact'))
            groups.setdefault(key,{})[int(r['team_tickets'])]=F(r['probability_exact'])
        for pmf in groups.values():self.assertEqual(sum(pmf.values()),1)
        for r in read_csv(ROOT/'outputs/tables/phase5_team_economics.csv'):
            key=tuple(r[k] for k in ('event_id','team_decisive_win_probability_exact','draw_rate_exact'))
            self.assertEqual(sum(t*p for t,p in groups[key].items()),F(r['expected_tickets_exact']))

    def test_group_conservation_and_single_member_baselines(self):
        for r in read_csv(ROOT/'outputs/tables/phase5_weekend_groups.csv'):
            self.assertEqual(F(r['expected_total_tickets_exact']),40*F(r['expected_units_full_pool_exact'])+F(r['expected_residual_full_pool_exact']))
            self.assertEqual(F(r['group_entry_expenditure_usd_exact']),int(r['group_size'])*F(r['per_participant_entry_expenditure_usd_exact']))
            self.assertEqual(F(r['participant_hours_exact']),int(r['group_size'])*F(r['per_participant_occupied_hours_exact']))
            if r['group_size']=='1':
                _,old=baseline_weekends(ROOT)[r['strategy']]
                self.assertEqual(F(r['p_aggregate_40_exact']),F(old['p_at_least_40_exact']))

    def test_pooling_success_and_capacity_are_not_synonyms(self):
        r=next(r for r in read_csv(ROOT/'outputs/tables/phase5_saturday_comparison.csv') if r['group_size']=='8' and r['vegas_draw_rate_exact']=='0' and r['historical_allocation']=='historical_official')
        self.assertGreater(F(r['new_minus_old_increment_pp_exact']),0)
        self.assertLess(F(r['new_minus_old_pooled_success_pp_exact']),0)
        self.assertLess(F(r['new_minus_old_incremental_units_per_participant_exact']),0)

    def test_historical_offers_and_policy_unknowns_retained(self):
        rows=read_csv(ROOT/'outputs/tables/phase5_historical_ode_offers.csv')
        self.assertEqual(len(rows),8)
        self.assertTrue(all(r['concurrent_casual_duration_minutes']=='135' for r in rows))
        self.assertEqual(next(r for r in rows if r['city']=='Vancouver')['fee_currency'],'CAD')
        policy=read_csv(ROOT/'outputs/tables/phase5_policy_evidence.csv')
        self.assertEqual(next(r for r in policy if r['topic']=='combining_attendees_tickets')['evidence_status'],'unavailable_event_specific_permission')

    def test_stopped_ode_reference_bounds(self):
        rows=read_csv(ROOT/'outputs/tables/phase5_ode_comparison.csv')
        for r in rows:
            if r['version']=='vegas_constructed': self.assertEqual(F(r['p_at_least_40_exact']),0)
        r=next(r for r in rows if r['version']=='historical_competitive' and r['throughput_basis']=='published_durations' and r['decisive_win_probability_exact']=='1/2')
        self.assertEqual(r['maximum_pods'],'5')
        self.assertEqual(F(r['p_at_least_40_exact']),F(9,8192))

    def test_manifest_row_counts(self):
        m=json.loads((ROOT/'outputs/tables/phase5_report.json').read_text())
        for file,count in m['table_rows'].items():self.assertEqual(len(read_csv(ROOT/'outputs/tables'/file)),count)
