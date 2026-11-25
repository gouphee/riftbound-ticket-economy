import unittest

from riftbound_tickets.payouts.historical import recorded_award, saturday_pool


def record(text, status):
    return {'match_record':text, 'user_event_status':{'registration_status':status}}


class PrimaryHistoricalPayoutTests(unittest.TestCase):
    def test_dropped_is_included_with_original_status(self):
        result = recorded_award(record('5-1-0','DROPPED'), rounds=6, table={4:30,5:40,6:40})
        self.assertEqual(result['primary_ticket_award'],40)
        self.assertEqual(result['registration_status_original'],'DROPPED')
        self.assertFalse(result['explicit_disqualification'])

    def test_eliminated_and_ambiguous_status_not_inferred_dq(self):
        for status in ['ELIMINATED', 'UNKNOWN_STATUS', None]:
            result=recorded_award(record('5-0-0',status),rounds=5,table={3:15,4:30,5:50})
            self.assertEqual(result['primary_ticket_award'],50)
            self.assertFalse(result['explicit_disqualification'])

    def test_explicit_dq_requires_policy_review_before_exclusion(self):
        result=recorded_award(record('5-0-0','DISQUALIFIED'),rounds=5,table={5:50})
        self.assertEqual(result['primary_ticket_award'],50)
        self.assertIn('unresolved',result['disqualification_status'])
        review={'record_source_id':'synthetic-record','policy_source_id':'synthetic-policy',
                'policy_interpretation':'Test-only documented forfeiture','action':'exclude'}
        result=recorded_award(record('5-0-0','DISQUALIFIED'),rounds=5,table={5:50},dq_review=review)
        self.assertEqual(result['primary_ticket_award'],0)
        self.assertEqual(result['record_rule_tickets'],50)
        with self.assertRaises(ValueError):
            recorded_award(record('5-0-0','DROPPED'),rounds=5,table={5:50},dq_review=review)

    def test_historical_tier_boundaries_and_draws(self):
        for table, rounds in [({4:24,5:36,6:48},6),({3:15,4:30,5:45},5),({3:15,4:30,5:50},5),({4:30,5:40,6:40},6)]:
            for wins in range(rounds+1):
                award=recorded_award(record(f'{wins}-{rounds-wins}-0','DROPPED'),rounds=rounds,table=table)
                self.assertEqual(award['primary_ticket_award'],table.get(wins,0))
        self.assertEqual(recorded_award(record('3-1-2','COMPLETE'),rounds=6,table={4:24,5:36,6:48})['primary_ticket_award'],0)

    def test_missing_record_not_inferred_from_roster_or_status(self):
        self.assertIsNone(recorded_award(record(None,'COMPLETE'),rounds=5,table={5:50})['primary_ticket_award'])
        self.assertIsNone(recorded_award(record('6-0-0','COMPLETE'),rounds=5,table={5:50})['primary_ticket_award'])

    def test_saturday_pool_is_independent_of_missing_bracket(self):
        for n in [128,132,264,505,518]:
            self.assertEqual(saturday_pool(n),4992)
        self.assertIsNone(saturday_pool(127))
        self.assertIsNone(saturday_pool(500,all_placements_awarded=False))
