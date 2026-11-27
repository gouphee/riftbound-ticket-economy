import json
import unittest
from pathlib import Path
from fractions import Fraction as F

from riftbound_tickets.field_composition import (valid_uid,standings_uid,roster_uid,unique_index,link_group,analyze)
from riftbound_tickets.recommendations import build_tables,inventory,fraction
from riftbound_tickets.phase6_claims import claim_rows
from riftbound_tickets.phase6 import preservation,operations_table
from riftbound_tickets.phase3a import read_csv

ROOT=Path(__file__).resolve().parents[1]


class Phase6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field=analyze(ROOT);cls.recs=build_tables(ROOT)

    def test_positive_integer_ids_only(self):
        for v in (None,'123',True,-1,0,1.5):self.assertIsNone(valid_uid(v))
        self.assertEqual(valid_uid(123),123)

    def test_conflicting_ids_are_unresolved_not_name_matched(self):
        row={'player':{'id':1,'best_identifier':'same name'},'user_event_status':{'user':{'id':2}}}
        self.assertIsNone(standings_uid(row))
        self.assertEqual(standings_uid({'player':{},'user_event_status':{'user':{'id':2}}}),2)
        self.assertEqual(link_group(None,{1:{}},set(),True),'unresolved_identity')

    def test_duplicate_ids_are_quarantined(self):
        rows=[{'row':{'user':{'id':1}}},{'row':{'user':{'id':1}}},{'row':{'user':{'id':2}}},{'row':{'user':None}}]
        idx,coll,missing=unique_index(rows,roster_uid)
        self.assertEqual(set(idx),{2});self.assertEqual(coll,{1});self.assertEqual(missing,1)
        self.assertEqual(link_group(1,idx,coll,True),'unresolved_identity')

    def test_absence_requires_complete_registry(self):
        self.assertEqual(link_group(2,{1:{}},set(),True),'absent_complete_main_registry')
        self.assertEqual(link_group(2,{1:{}},set(),False),'unresolved_main_coverage')

    def test_composition_count_conservation(self):
        rows=self.field['composition'];self.assertEqual(sum(r['standings_entries'] for r in rows),20651)
        for key in {r['event_key'] for r in rows}:
            self.assertEqual(sum(r['fraction_of_side_standings'] for r in rows if r['event_key']==key),1)
        summary={r['weekday']:r for r in self.field['weekday_summary']}
        self.assertEqual([summary[d]['main_registry_linked'] for d in ('friday','saturday','sunday')],[9172,126,4191])
        self.assertEqual(sum(r['unresolved_identity'] for r in summary.values()),6)
        self.assertEqual(sum(r['entries'] for r in self.field['side_performance_distribution']),20651)

    def test_same_city_participation_pattern_in_all_eight(self):
        rows=self.field['composition']
        for city in {r['event_key'].rsplit('-',1)[0] for r in rows}:
            values={r['weekday']:r['fraction_of_side_standings'] for r in rows if r['event_key'].startswith(city+'-') and r['identity_group']=='main_registry_linked'}
            self.assertLess(values['saturday'],values['friday']);self.assertLess(values['saturday'],values['sunday'])

    def test_sunday_rule_qualification_not_automatically_attendance(self):
        rows=self.field['sunday_qualification']
        self.assertEqual(sum(r['main_linked_entries'] for r in rows),4191)
        self.assertEqual(sum(r['below_R8_gate'] for r in rows),4048)
        self.assertEqual(sum(r['qualified_by_R8_points'] for r in rows),143)
        self.assertEqual(sum(r['Day2_pairing_evidenced'] for r in rows),142)

    def test_cross_match_accounting(self):
        for r in self.field['cross_group_matches']:
            self.assertEqual(r['matches'],r['main_wins']+r['not_listed_wins']+r['draws'])
            if r['main_decisive_win_fraction'] is not None:
                self.assertEqual(r['main_decisive_win_fraction'],F(r['main_wins'],r['main_wins']+r['not_listed_wins']))
        sat=next(r for r in self.field['weekday_summary'] if r['weekday']=='saturday')
        self.assertEqual(sat['cross_group_main_decisive_win_fraction'],F(283,540))

    def test_main_checkpoint_anomalies_are_visible(self):
        a={r['city']:r for r in self.field['main_feasibility']}
        self.assertEqual((a['hartford']['main_roster_entries'],a['hartford']['D1_standings_entries']),(1954,1953))
        self.assertEqual((a['singapore']['main_roster_entries'],a['singapore']['D1_standings_entries']),(2054,2055))
        self.assertEqual(sum(r.get('conflicting_identifier_values',0) for r in self.field['identity_audit']),6)

    def test_aggregate_exports_contain_no_person_identifiers(self):
        forbidden={'uid','player_id','registration_id','player_name','best_identifier','user','player','main_D1_record'}
        for rows in self.field.values():
            for r in rows:self.assertFalse(forbidden & set(r))

    def test_legacy_itinerary_metrics_and_booking_exposure(self):
        r=next(r for r in self.recs['itineraries'] if r['itinerary_id']=='mixed-p50')
        self.assertEqual(r['p40'],F(15631,131072))
        self.assertEqual((r['modeled_entry_spend_usd'],r['occupied_hours']),(135,F(39,2)))
        r=next(r for r in self.recs['itineraries'] if r['itinerary_id']=='competitive_first-p50')
        self.assertGreater(r['full_plan_fee_exposure_usd'],r['modeled_entry_spend_usd'])
        for r in self.recs['itineraries']:
            if r['full_plan_fee_exposure_usd'] is not None:
                self.assertGreaterEqual(r['full_plan_fee_exposure_usd'],r['modeled_entry_spend_usd'])
                self.assertEqual(r['full_plan_fee_exposure_usd'],r['scheduled_booking_exposure_usd']+r['planned_ODE_budget_usd'])

    def test_team_replaces_nexus_and_preserves_fee_alternatives(self):
        rows=[r for r in self.recs['itineraries'] if r['profile']=='Friday_team_consideration']
        self.assertEqual(len(rows),2);self.assertEqual(rows[0]['p40'],rows[1]['p40'])
        self.assertEqual(sorted(r['full_plan_fee_exposure_usd'] for r in rows),[135,160])
        self.assertFalse(any(r['event_id']=='friday-super-nexus-night' and r['itinerary_id'].startswith('friday-team') for r in self.recs['itinerary_events']))

    def test_close_to_40_exact_probabilities_and_ceilings(self):
        def select(balance,event):return next(r for r in self.recs['close_to_40'] if r['starting_tickets']==balance and r['event_id']==event and r['hypothetical_p']==F(1,2))
        self.assertEqual(select(38,'ode-standard-constructed')['p_reach_40'],F(1,2))
        self.assertEqual(select(38,'friday-champion-deck-trial')['p_reach_40'],F(7,8))
        self.assertEqual(select(38,'friday-radiance-sealed-deck')['p_reach_40'],1)
        self.assertFalse(select(35,'ode-standard-constructed')['can_cover_gap'])
        for b,p in ((20,F(3,16)),(25,F(1,2)),(30,F(1,2))):self.assertEqual(select(b,'sunday-radiance-standard-challenge')['p_reach_40'],p)

    def test_performance_thresholds_are_bracketed(self):
        for r in self.recs['performance_thresholds']:
            self.assertLess(r['Rebound_p40_at_lower'],r['Sunday_Challenge_p40'])
            self.assertGreaterEqual(r['Rebound_p40_at_upper'],r['Sunday_Challenge_p40'])
            self.assertEqual(r['Rebound_p_threshold_upper']-r['Rebound_p_threshold_lower'],F(1,10000))

    def test_recommendation_ranking_can_reverse(self):
        rows=self.recs['performance_sensitivities']
        def p(s,k):return next(r['p40'] for r in rows if r['scenario_id']==s and r['strategy']==k)
        self.assertGreater(p('equal_50','mixed'),p('equal_50','competitive_first'))
        self.assertLess(p('Rebound60_other50','mixed'),p('Rebound60_other50','competitive_first'))

    def test_claim_index_coverage_statuses_and_source_cells(self):
        rows=claim_rows(ROOT);self.assertEqual(len(rows),57)
        self.assertEqual(len({r['claim_id'] for r in rows}),57)
        self.assertEqual({r['video_sequence'] for r in rows},{f'S{i:02d}' for i in range(1,14)})
        for r in rows:
            self.assertTrue(r['spoken_qualification'])
            if r['status'] in ('contradicted','unresolved'):self.assertEqual(r['production_instruction'],'DO_NOT_ASSERT')

    def test_no_tft_scenarios_promoted(self):
        self.assertFalse(any('tft' in r.get('event_id','') for r in self.recs['event_objectives']))
        self.assertFalse(any('tft' in r['event_id'] for r in self.recs['itinerary_events']))

    def test_current_operational_unknowns_are_explicit(self):
        rows={r['operational_item']:r for r in operations_table(ROOT)}
        self.assertEqual(rows['registration_stock']['http_status'],403)
        for k in ('badge_limits_transfers','Friday_team_fee_allocation','ODE_desk_last_launch','exact_registration_cutoffs'):
            self.assertEqual(rows[k]['status'],'unresolved')

    def test_existing_draw_sensitivity_changes_tiny_standalone_edge(self):
        rows=read_csv(ROOT/'outputs/tables/phase6_draw_robustness.csv')
        selected={r['event_id']:F(r['p_at_least_40_exact']) for r in rows if r['competitive_draw_rate']=='0.02'}
        self.assertGreater(selected['sunday-radiance-standard-challenge'],selected['saturday-standard-rebound-day-1'])

    def test_preserves_all_previous_research(self):
        result=preservation(ROOT);self.assertTrue(result['passed']);self.assertEqual(result['checked_files'],1045)


if __name__=='__main__':unittest.main()
