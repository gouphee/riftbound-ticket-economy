"""Synthetic edge cases: records, drop eligibility, and unresolved Top 8 seeds."""

import copy
import unittest

from riftbound_tickets.pipeline import normalize


def fixture(event_type="friday"):
    status={"id":1,"best_identifier":"Synthetic test player","matches_won":4,"matches_lost":2,"matches_drawn":0,"registration_status":"COMPLETE"}
    row={"id":7,"rank":1,"round_number":6,"match_record":"4-2-0","match_points":12,"user_event_status":status,"player":{"id":7}}
    registration={**status,"user":{"id":7},"final_place_in_standings":1}
    def wrapped(r): return {"row":r,"source_id":"synthetic-test","source_url":"https://example.test","raw_path":"test-only","retrieved_at":"test-only","page":1,"row_index":0}
    rounds=[{"id":i,"round_number":i,"status":"COMPLETE"} for i in range(1,7)]
    return {"event_key":"test-only","spec":{"event_key":"test-only","city":"Test","event_type":event_type,"official_event_id":0},
            "metadata":{"name":"Synthetic test event","start_datetime":"2026-01-01T00:00:00Z","settings":{"event_lifecycle_status":"EVENT_FINISHED"},"starting_player_count":1,
                        "tournament_phases":[{"id":1,"order_in_phases":1,"round_type":"SWISS","status":"COMPLETE","rounds":rounds}]},
            "selected_round_id":6,"selected_round_number":6,"standings":{"rows":[wrapped(row)],"expected_count":1,"complete":True,"issues":[]},
            "roster":{"rows":[wrapped(registration)],"expected_count":1,"complete":True,"issues":[]},"match_sets":[]}


SOURCE={"source_id":"synthetic-test","url":"https://example.test"}
RULE={"rounds":6,"win_tickets":{6:48,5:36,4:24}}


class NormalizationTests(unittest.TestCase):
    def test_unknown_byes_stay_unknown(self):
        rows,*_=normalize(fixture(),RULE,SOURCE)
        self.assertIsNone(rows[0]['byes'])
        self.assertIsNone(rows[0]['verified_tickets_issued'])

    def test_drop_does_not_invent_eligibility_or_delete_record(self):
        c=fixture()
        for group in ['standings','roster']:
            r=c[group]['rows'][0]['row']
            (r['user_event_status'] if group=='standings' else r)['registration_status']='DROPPED'
        rows,*_=normalize(c,RULE,SOURCE)
        self.assertEqual(rows[0]['published_ticket_entitlement'],24)
        self.assertIsNone(rows[0]['supported_eligible_tickets'])
        self.assertEqual(rows[0]['eligibility_status'],'unknown_drop_or_short_record')

    def test_missing_record_is_not_zero(self):
        c=fixture();c['standings']['rows'][0]['row']['match_record']=None
        rows,*_=normalize(c,RULE,SOURCE)
        self.assertIsNone(rows[0]['match_wins'])
        self.assertIsNone(rows[0]['published_ticket_entitlement'])

    def test_conflicting_record_is_flagged_and_payout_suppressed(self):
        c=fixture();c['roster']['rows'][0]['row']['matches_won']=5
        rows,*_=normalize(c,RULE,SOURCE)
        self.assertIn('standing_record_disagrees_with_roster',rows[0]['flags'])
        self.assertIsNone(rows[0]['published_ticket_entitlement'])

    def test_unresolved_top8_seed_does_not_receive_champion_payout(self):
        c=fixture('saturday')
        c['metadata']['tournament_phases'].append({"id":2,"order_in_phases":2,"round_type":"RANKED_SINGLE_ELIMINATION","status":"UPCOMING","rounds":[{"id":7,"round_number":7,"status":"UPCOMING"}]})
        rows,*_=normalize(c,{"rounds":7},SOURCE)
        self.assertIsNone(rows[0]['final_placement'])
        self.assertIsNone(rows[0]['published_ticket_entitlement'])
        self.assertEqual(rows[0]['top8_equal_split_scenario_tickets'],216)
        self.assertFalse(rows[0]['split_observed_for_this_event'])

    def test_six_win_record_is_not_capped_to_five_win_payout(self):
        c=fixture();r=c['standings']['rows'][0]['row'];r['match_record']='6-0-0';r['match_points']=18
        r['user_event_status'].update(matches_won=6,matches_lost=0)
        c['roster']['rows'][0]['row'].update(matches_won=6,matches_lost=0)
        rows,*_=normalize(c,{"rounds":5,"win_tickets":{5:50,4:30,3:15}},SOURCE)
        self.assertIsNone(rows[0]['published_ticket_entitlement'])
