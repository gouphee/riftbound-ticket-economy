import itertools
import unittest
from collections import Counter,defaultdict
from fractions import Fraction as F
from math import comb
from pathlib import Path

from riftbound_tickets.models.aggregation import (
    allocate_team,allocate_two,group_metrics,independent_joint,partial_metrics,without_replacement)
from riftbound_tickets.models.saturday_analytical import historical_ticket_distribution
from riftbound_tickets.phase5 import expected_max_clock,team_pmf,team_weekend
from riftbound_tickets.collectors.phase5_sources import evidence

ROOT=Path(__file__).resolve().parents[1]


class AggregationTests(unittest.TestCase):
    def test_independent_convolution_against_enumeration(self):
        pmf={0:F(1,2),24:F(1,4),80:F(1,4)}
        oracle=defaultdict(F)
        for values in itertools.product(pmf,repeat=3):
            prob=F(1)
            for t in values:prob*=pmf[t]
            oracle[(sum(values),sum(t//40 for t in values),sum(t>=40 for t in values))]+=prob
        self.assertEqual(independent_joint(pmf,3),dict(oracle))

    def test_without_replacement_against_individual_subsets(self):
        population=[0,0,18,24,40,80]
        oracle=defaultdict(F)
        for sample in itertools.combinations(population,3):
            oracle[(sum(sample),sum(t//40 for t in sample),sum(t>=40 for t in sample))]+=F(1,comb(6,3))
        self.assertEqual(without_replacement(dict(Counter(population)),3),dict(oracle))

    def test_full_population_and_singleton(self):
        counts={0:3,18:2,80:1}
        self.assertEqual(without_replacement(counts,6),{(116,2,1):F(1)})
        pmf={t:F(c,6) for t,c in counts.items()}
        self.assertEqual(without_replacement(counts,1),independent_joint(pmf,1))

    def test_historical_pool_and_split_conserve(self):
        for split in (False,True):
            pmf=historical_ticket_distribution(512,split_top8=split)
            m=group_metrics(without_replacement({t:int(p*512) for t,p in pmf.items()},8),8)
            self.assertEqual(m['expected_total_tickets'],78)
            self.assertEqual(m['expected_total_tickets'],40*m['expected_units_full_pool']+m['expected_residual_full_pool'])

    def test_thresholds_and_person_limit_distinct_from_units(self):
        a=group_metrics(independent_joint({20:F(1)},2),2)
        self.assertEqual(a['p_any_individual_40'],0)
        self.assertEqual(a['p_aggregate_40'],1)
        self.assertEqual(a['expected_units_full_pool'],1)
        self.assertEqual(a['p_full_pool_capacity_for_everyone'],0)
        b=group_metrics(independent_joint({80:F(1)},1),1)
        self.assertEqual(b['expected_units_no_pool'],2)
        self.assertEqual(b['expected_qualifying_individuals'],1)
        self.assertEqual(b['expected_units_full_pool_if_one_per_person'],1)

    def test_single_member_agreement(self):
        pmf={0:F(1,2),24:F(1,4),80:F(1,4)}
        m=group_metrics(independent_joint(pmf,1),1)
        self.assertEqual(m['p_any_individual_40'],F(1,4))
        self.assertEqual(m['p_aggregate_40'],F(1,4))
        self.assertEqual(m['expected_units_full_pool'],m['expected_units_no_pool'])
        self.assertEqual(m['incremental_success_probability'],0)

    def test_invalid_distribution_and_sample(self):
        for pmf,n in [({F(1,2):F(1)},2),({0:F(1,2)},2),({0:F(1)},0)]:
            with self.assertRaises(ValueError):independent_joint(pmf,n)
        with self.assertRaises(ValueError):without_replacement({0:1},2)

    def test_partial_prioritizes_own_units_and_retains_other_prizes(self):
        a=partial_metrics({20:F(1)},2,'own_first_surplus')
        self.assertEqual(a['p_prioritized_recipient_40'],0)
        self.assertEqual(a['expected_unspent_retained_and_residual_tickets'],40)
        b=partial_metrics({20:F(1)},4,'keep10_remainders')
        self.assertEqual(b['expected_potential_units'],1)
        self.assertEqual(b['expected_unspent_retained_and_residual_tickets'],40)
        self.assertEqual(b['p_capacity_for_everyone_under_protocol'],0)

    def test_partial_single_member_preserves_baseline(self):
        pmf={0:F(1,2),45:F(1,4),85:F(1,4)}
        for policy in ('own_first_surplus','keep10_remainders'):
            m=partial_metrics(pmf,1,policy)
            self.assertEqual(m['p_prioritized_recipient_40'],F(1,2))
            self.assertEqual(m['expected_potential_units'],F(3,4))
            self.assertEqual(m['expected_unspent_retained_and_residual_tickets'],F(5,2))

    def test_partial_own_first_can_top_up_prioritized_member(self):
        # Ordered draws (20,60) top up the recipient. (60,20) reserves their own.
        m=partial_metrics({20:F(1,2),60:F(1,2)},2,'own_first_surplus')
        self.assertEqual(m['p_prioritized_recipient_40'],F(3,4))
        self.assertEqual(m['expected_potential_units'],F(3,2))
        self.assertEqual(m['expected_unspent_retained_and_residual_tickets'],20)

    def test_integer_team_allocation_conserves_odd_awards(self):
        for size in (2,3):
            for t in range(81):
                for kind in ('integer_equal','prioritize_A'):
                    allocation=allocate_team(t,size,kind)
                    self.assertEqual(sum(allocation),t)
                    self.assertTrue(all(type(x) is int and x>=0 for x in allocation))
        self.assertEqual(allocate_two(5,'integer_equal'),(2,3))

    def test_clock_max_not_participant_hour_sum(self):
        self.assertEqual(expected_max_clock({F(1):F(1,2),F(3):F(1,2)},2),F(5,2))


class TeamModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.events=evidence(ROOT)
        cls.friday=next(e for e in cls.events if e['event_id']=='friday-radiance-2v2-team-challenge')

    def test_friday_wdl_multinomial_oracle(self):
        p,d=F(3,5),F(1,20)
        prob={'W':(1-d)*p,'D':d,'L':(1-d)*(1-p)}
        oracle={t:F(0) for t in (0,5,10,25,40,60,80)}
        for path in itertools.product('WDL',repeat=5):
            mass=F(1)
            for outcome in path:mass*=prob[outcome]
            s=3*path.count('W')+path.count('D')
            award=0 if s<7 else 5 if s<9 else 10 if s==9 else 25 if s<12 else 40 if s==12 else 60 if s<15 else 80
            oracle[award]+=mass
        self.assertEqual(team_pmf(self.friday,p,d),oracle)
        self.assertEqual(sum(t*q for t,q in team_pmf(self.friday,F(1,2),F(0)).items()),F(95,8))

    def test_team_weekend_shared_outcome_and_stopping(self):
        joint,pmfs,resources,clock=team_weekend(self.friday,self.events,p_team=F(1))
        self.assertEqual(joint,{(80,2,2):F(1)})
        self.assertEqual(pmfs,[{40:F(1)},{40:F(1)}])
        self.assertEqual(resources[0]['cost'],50)
        self.assertEqual(resources[0]['hours'],F(31,4))
        self.assertEqual(clock,{F(15,2):F(1)})

    def test_joint_pair_not_two_independent_team_prizes(self):
        joint,pmfs,resources,clock=team_weekend(self.friday,self.events)
        m=group_metrics(joint,2)
        self.assertEqual(m['expected_total_tickets'],sum(t*p for pmf in pmfs for t,p in pmf.items()))
        self.assertNotEqual(m['p_any_individual_40'],group_metrics(independent_joint(pmfs[0],2),2)['p_any_individual_40'])
        self.assertEqual(resources[0]['hours'],F(3007,128))
