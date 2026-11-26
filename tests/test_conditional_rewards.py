import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from riftbound_tickets.models.conditional_rewards import (record_distribution, gated_checkpoint,
    strong_record_metrics, bracket_distribution, expected, last_round_rewards, PERFORMANCE, DRAWS)
from riftbound_tickets.conditional_rewards import (historical_rows, cohort_tables, preservation,
    feasible_cut_assignments, cohort_published_bounds)
from riftbound_tickets.phase3a import rules_from_archive

ROOT=Path(__file__).resolve().parents[1]


class ConditionalRewardsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rules=rules_from_archive(ROOT)[1]

    def test_known_equal_skill_probabilities(self):
        m=strong_record_metrics(F(1,2),F(0),self.rules)
        for key,value in {'historical_exact_5_1':F(6,64),'vegas_exact_8_2':F(45,1024),
            'historical_at_least_5_wins':F(7,64),'vegas_at_least_8_wins':F(56,1024),
            'historical_exact_6_0':F(1,64),'vegas_exact_10_0':F(1,1024)}.items():self.assertEqual(m[key],value)

    def test_gate_normalization_and_strong_targets_unchanged(self):
        for p in (*PERFORMANCE,F(0),F(1)):
            for d in (*DRAWS,F(1)):
                reached,stopped=gated_checkpoint(self.rules,p,d)
                self.assertEqual(sum(reached.values())+stopped,1)
                self.assertEqual(1-stopped,sum(v for (w,l,x),v in record_distribution(6,p,d).items() if 3*w+x>=12))
                ungated=record_distribution(10,p,d)
                for record,mass in ungated.items():
                    if 3*record[0]+record[2]>=24:self.assertEqual(reached.get(record,F(0)),mass)

    def test_exact_multinomial_and_tail_draw_definitions(self):
        p,d=F(3,5),F(1,20)
        r=record_distribution(6,p,d)
        self.assertEqual(sum(r.values()),1)
        self.assertEqual(r[5,1,0],6*((1-d)*p)**5*((1-d)*(1-p)))
        m=strong_record_metrics(p,d,self.rules)
        self.assertGreater(m['vegas_at_least_24_points'],m['vegas_at_least_8_wins'])
        self.assertEqual(m['historical_at_least_15_points'],m['historical_at_least_5_wins'])

    def test_skill_reverses_cumulative_but_not_exact(self):
        for p in PERFORMANCE:
            m=strong_record_metrics(p,F(0),self.rules)
            self.assertGreater(m['historical_exact_5_1'],m['vegas_exact_8_2'])
            self.assertGreater(m['historical_exact_6_0'],m['vegas_exact_10_0'])
        m=strong_record_metrics(F(4,5),F(0),self.rules)
        self.assertLess(m['historical_at_least_5_wins'],m['vegas_at_least_8_wins'])

    def test_split_ticket_conservation_and_expectations(self):
        self.assertEqual(8*216,432+288+2*216+4*144)
        self.assertEqual(4*288,432+288+2*216)
        self.assertEqual(2*360,432+288)
        for name in ('published','top8_equal','top4_equal','top2_equal'):
            self.assertEqual(expected(bracket_distribution(F(1,2),name)),216)
            for q in PERFORMANCE:self.assertEqual(sum(bracket_distribution(q,name).values()),1)
        q=F(4,5)
        self.assertGreater(expected(bracket_distribution(q)),expected(bracket_distribution(q,'top8_equal')))

    def test_final_round_all_outcomes_and_draw_invariance_at_half(self):
        for w,l,awards,ev in ((8,2,(40,35,30),35),(9,1,(60,50,40),50),(10,0,(80,70,60),70)):
            for d in (*DRAWS,F(1)):
                r=last_round_rewards(w,l,F(1,2),d,self.rules)
                self.assertEqual(tuple(r[k+'_tickets'] for k in ('win','draw','loss')),awards)
                self.assertEqual(r['expected_tickets'],ev)
                self.assertEqual(r['guaranteed_tickets_if_completed_eligible'],awards[2])

    def test_historical_cohorts_replay_without_seed_as_finish(self):
        rows=historical_rows(ROOT);cohorts,hybrid,_=cohort_tables(rows)
        self.assertEqual(len(rows),3165)
        self.assertEqual(sum(r['Swiss_seed_vs_bracket_disagreement'] for r in rows),2)
        for record,n,cut in (('5-1-0',216,16),('6-0-0',37,36)):
            c=next(r for r in cohorts if r['event_key']=='all_eight_events' and r['checkpoint_round']==6 and r['record']==record)
            self.assertEqual((c['cohort_entries'],c['cut_eligible_entries']),(n,cut))
            self.assertIsNone(c['full_cohort_published_mean_tickets'])
            self.assertGreater(c['unresolved_payout_entries'],0)
        for r in rows:
            self.assertTrue(r['round6_source_id'] and r['round7_source_id'] and r['payout_source_id'])
            self.assertIsNone(r['physically_issued_tickets'])
            if r['published_resolved_tickets'] is None:
                self.assertGreaterEqual(r['published_tickets_lower'],144)
                self.assertEqual(r['published_tickets_upper'],432)
        for r in hybrid:
            if r['future_bracket_win_probability_q']==F(1,2) and r['arrangement']=='published':
                other=next(x for x in hybrid if x['event_key']==r['event_key'] and x['record']==r['record']
                    and x['future_bracket_win_probability_q']==F(1,2) and x['arrangement']=='top8_equal')
                self.assertEqual(r['conditional_expected_tickets'],other['conditional_expected_tickets'])

    def test_cohort_bounds_conserve_joint_pool(self):
        rows=historical_rows(ROOT);support=feasible_cut_assignments(rows)
        for event,(rs,assignments) in support.items():
            self.assertTrue(all(sum(a)==1728 for a in assignments))
            self.assertEqual(cohort_published_bounds(rs,support),(F(216),F(216)))
        unknown=next(r for r in rows if r['event_key']=='singapore-saturday' and r['published_resolved_tickets'] is None)
        self.assertEqual(unknown['published_tickets_lower'],216)

    def test_owner_observation_does_not_identify_event(self):
        owner=json.loads((ROOT/'data/conditional_rewards/observations.json').read_text())['owner_top8_split']
        self.assertEqual(owner['received_tickets'],216)
        self.assertIsNone(owner['event_id'])
        self.assertIsNone(owner['final_swiss_record'])

    def test_input_validation(self):
        with self.assertRaises(ValueError):record_distribution(6,.5)
        with self.assertRaises(ValueError):record_distribution(-1,F(1,2))
        with self.assertRaises(ValueError):bracket_distribution(F(1,2),'top16')
        with self.assertRaises(ValueError):last_round_rewards(5,1,F(1,2),F(0),self.rules)

    def test_prior_artifacts_unchanged(self):self.assertTrue(preservation(ROOT)['passed'])


if __name__=='__main__':unittest.main()
