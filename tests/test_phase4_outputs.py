import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from riftbound_tickets.collectors.phase4_sources import sources_and_inventory
from riftbound_tickets.models.individual import solo_distribution,validate_schedule
from riftbound_tickets.phase3a import read_csv,rules_from_archive
from riftbound_tickets.phase4 import economics,make_plans,preservation,validate_published_awards

ROOT=Path(__file__).resolve().parents[1]


class Phase4EvidenceAndOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources,cls.inventory,cls.revisions=sources_and_inventory(ROOT)
        cls.rules=rules_from_archive(ROOT)[1]

    def test_inventory_and_live_revision_review(self):
        self.assertEqual(len(self.inventory),33)
        self.assertEqual(self.revisions['revisions'],[])
        self.assertTrue(all(r['raw_cells'] and r['source_id'] and r['retrieved_at'] for r in self.inventory))
        self.assertTrue(all(r['earliest_realistic_completion'] is None for r in self.inventory))
        self.assertEqual(self.sources[2]['http_status'],403)

    def test_event_award_boundaries(self):
        validate_published_awards(self.inventory,self.rules)
        E={r['event_name']:r for r in self.inventory}
        cases={'Radiance Standard Challenge':(0,40),'Standard Constructed':(0,3),
               'Radiance Sealed Deck':(2,8),'Draft Challenge':(1,4),'Champion Deck Trial':(1,4),
               'Super Nexus Night':(0,8),'Radiance Full Box Sealed':(0,8)}
        for name,(low,high) in cases.items():
            self.assertEqual(solo_distribution(E[name],F(0),rules=self.rules).get(low),1)
            self.assertEqual(solo_distribution(E[name],F(1),rules=self.rules).get(high),1)

    def test_source_rule_change_fails_closed(self):
        event=next(r for r in self.inventory if r['event_id']=='sunday-radiance-standard-challenge')
        changed={**event,'payout_text':event['payout_text'].replace('28 Tickets','29 Tickets')}
        with self.assertRaises(ValueError): validate_published_awards([changed],self.rules)

    def test_primary_schedules_and_pod_bound(self):
        plans,_,_,_=make_plans(self.inventory,F(1,2),F(0))
        for plan in plans.values(): validate_schedule(plan)
        self.assertEqual(len(plans['ode_constructed']),8)
        self.assertEqual(sum(max(t for t,p in v.pmf) for v in plans['ode_constructed']),24)
        no_queue,_,_,_=make_plans(self.inventory,F(1,2),F(0),queue=0)
        self.assertEqual(len(no_queue['ode_constructed']),11)

    def test_unknown_and_zero_cost_ratios(self):
        m=economics({0:F(1)},0,F(1),None)
        self.assertIsNone(m['expenditure_per_expected_ticket'])
        self.assertIsNone(m['elapsed_hours_per_expected_ticket'])
        self.assertIsNone(m['tickets_per_active_hour'])
        self.assertEqual(m['expected_tickets'],0)

    def test_table_pmfs_and_expectations(self):
        groups={}
        for r in read_csv(ROOT/'outputs/tables/phase4_event_distributions.csv'):
            key=tuple(r[k] for k in ('event_id','conditional_decisive_win_probability','competitive_draw_rate','bo1_draw_rate'))
            groups.setdefault(key,{})[int(r['tickets'])]=F(r['probability_exact'])
        for pmf in groups.values(): self.assertEqual(sum(pmf.values()),1)
        for r in read_csv(ROOT/'outputs/tables/phase4_event_economics.csv'):
            key=tuple(r[k] for k in ('event_id','conditional_decisive_win_probability','competitive_draw_rate','bo1_draw_rate'))
            if key in groups:
                self.assertEqual(sum(t*p for t,p in groups[key].items()),F(r['expected_tickets_exact']))
        for r in read_csv(ROOT/'outputs/tables/phase4_strategy_results.csv'):
            self.assertEqual(F(r['p_at_least_40_exact'])+F(r['p_below_40_exact']),1)
            self.assertEqual(F(r['success_cost_contribution_usd_exact'])+F(r['failure_cost_contribution_usd_exact']),F(r['expected_entry_fee_usd_exact']))

    def test_all_prior_research_preserved(self):
        self.assertTrue(preservation(ROOT)['passed'])

    def test_historical_currencies_not_relabeled_usd(self):
        rows=read_csv(ROOT/'outputs/tables/phase4_historical_comparisons.csv')
        self.assertNotIn('historical_entry_usd',rows[0])
        self.assertEqual(next(r for r in rows if r['historical_event_id']=='vancouver-friday')['historical_currency_explicit_in_fee_cell'],'CAD')
        self.assertEqual(next(r for r in rows if r['historical_event_id']=='utrecht-friday')['historical_currency_explicit_in_fee_cell'],'EUR')
        self.assertEqual(next(r for r in rows if r['historical_event_id']=='sydney-friday')['historical_currency_explicit_in_fee_cell'],'')

    def test_output_manifest_counts(self):
        report=json.loads((ROOT/'outputs/tables/phase4_report.json').read_text())
        for name,count in report['table_rows'].items(): self.assertEqual(len(read_csv(ROOT/'outputs/tables'/name)),count)
