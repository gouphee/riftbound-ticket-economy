import csv
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from riftbound_tickets.phase2 import audit_phase2, build_phase2

ROOT = Path(__file__).resolve().parents[1]


def read_csv(name):
    with (ROOT / 'outputs/tables' / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


class Phase2ArchivedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('riftbound_tickets.collectors.evidence.urlopen', side_effect=AssertionError('Phase 2 must be offline')):
            cls.report = build_phase2(ROOT)
        cls.summaries = {s['event_key']:s for s in read_csv('historical_ticket_economy.csv')}

    def test_primary_totals_include_all_dropped_qualifying_records(self):
        self.assertEqual(self.report['friday_standings_implied_tickets'],119587)
        self.assertEqual(self.report['sunday_standings_implied_tickets'],60556)
        u = self.summaries['utrecht-sunday']
        self.assertEqual(u['observed_standings_implied_tickets'],'10920')
        self.assertEqual(u['legacy_supported_eligible_tickets_known_sensitivity'],'2080')
        self.assertEqual(u['dropped_qualifying_entries'],'268')

    def test_all_eight_saturday_pools_fixed_despite_unfinished_cuts(self):
        self.assertEqual(self.report['saturday_conditional_pool'],39936)
        sat = [s for s in self.summaries.values() if s['event_format']=='saturday']
        self.assertEqual(len(sat),8)
        self.assertTrue(all(s['conditional_schedule_pool']=='4992' for s in sat))

    def test_real_draw_denominators_and_source_flags(self):
        d = self.report['draw_summary']
        self.assertEqual((d['drawn_matches'],d['completed_played_matches']),(1150,50262))
        self.assertEqual((d['excluded_bye'],d['excluded_non_game']),(130,234))
        self.assertAlmostEqual(d['draw_rate'],1150/50262)
        weighted = sum(r['drawn_matches'] for r in self.report['draw_summary_by_event_format']) / sum(r['completed_played_matches'] for r in self.report['draw_summary_by_event_format'])
        self.assertEqual(weighted,d['draw_rate'])

    def test_missing_standings_and_missing_match_are_not_imputed(self):
        atl = self.summaries['atlanta-friday']
        self.assertEqual((atl['observed_n'],atl['roster_entries']),('1019','1020'))
        self.assertEqual(atl['observed_standings_implied_tickets'],'9432')
        people = read_csv('historical_individual_awards.csv')
        self.assertNotIn(('atlanta-friday','3084340'),{(p['event_key'],p['registration_id']) for p in people})
        hartford = next(p for p in people if p['event_key']=='hartford-friday' and p['registration_id']=='3913085')
        self.assertEqual(hartford['match_record_original'],'0-3-0')
        self.assertEqual(hartford['observed_standings_implied_tickets'],'0')
        self.assertEqual(hartford['legacy_strict_published_entitlement'],'')

    def test_empty_round_and_unresolved_cut_draw_credits_stay_visible(self):
        rates = read_csv('historical_draw_rates.csv')
        empty = next(r for r in rates if r['event_key']=='singapore-friday' and r['group_type']=='event_round' and r['round_number']=='6')
        self.assertEqual((empty['completed_played_matches'],empty['draw_rate']),('0',''))
        rec = next(r for r in read_csv('historical_draw_reconciliation.csv') if r['event_key']=='utrecht-saturday')
        self.assertEqual(rec['unreconciled_draw_credits'],'6')

    def test_additive_exports_and_all_witnesses_audit(self):
        result = audit_phase2(ROOT)
        self.assertTrue(result['passed'])
        self.assertTrue(result['raw_and_legacy_artifacts_unchanged'])
        self.assertEqual(result['standings_entries'],20651)
        self.assertEqual(result['unique_match_records_all_phases'],50662)
