"""Independent small-case checks for Phase 4 payout and acquisition semantics."""
import itertools
import unittest
from fractions import Fraction as F
from pathlib import Path

from riftbound_tickets.models.individual import (
    Visit, adaptive_policy, convolution, fixed_policy, metrics, outcomes, pareto,
    rebound_policy, saturday_stages, solo_distribution, terminal_metrics,
    validate_schedule, win_awards,
)
from riftbound_tickets.models.saturday_analytical import vegas_ticket_distribution
from riftbound_tickets.models.saturday_draws import vegas_draw_ticket_distribution
from riftbound_tickets.phase3a import rules_from_archive

ROOT=Path(__file__).resolve().parents[1]


def v(name,day,start,end,cost,pmf):
    return Visit(name,day,start,end,cost,F(end-start,2),end-start,tuple(pmf.items()))


class IndividualAwards(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rules=rules_from_archive(ROOT)[1]

    def test_wdl_conditional_parameter(self):
        self.assertEqual(outcomes(F(7,10),F(1,20)).win,F(133,200))
        self.assertEqual(outcomes(F(7,10),F(1,20)).loss,F(57,200))
        for p in (F(-1),F(11,10),.5):
            with self.assertRaises(ValueError): outcomes(p,F(0))

    def test_enumerated_win_distribution_with_draws(self):
        p,d=F(3,5),F(1,20)
        o=outcomes(p,d)
        oracle={0:F(0),2:F(0),5:F(0),9:F(0)}
        table={0:0,1:2,2:5,3:9}
        for path in itertools.product(('win','draw','loss'),repeat=3):
            mass=F(1)
            for result in path: mass*=getattr(o,result)
            oracle[table[path.count('win')]]+=mass
        self.assertEqual(win_awards(3,table,p,d),oracle)

    def test_draws_not_wins_and_participation_awards(self):
        self.assertEqual(win_awards(3,{w:2+2*w for w in range(4)},F(1),F(1))[2],1)
        self.assertEqual(win_awards(5,{3:16,4:28,5:40},F(1),F(1))[0],1)
        with self.assertRaises(ValueError): win_awards(3,{4:5},F(1,2))

    def test_stage_model_matches_preserved_phases(self):
        for d in (F(0),F(1,100),F(1,50),F(1,20)):
            pmf={}
            for (_,t),mass in saturday_stages(self.rules,F(1,2),d,d).items(): pmf[t]=pmf.get(t,F(0))+mass
            expected=vegas_draw_ticket_distribution(self.rules,outcomes(F(1,2),d))
            self.assertEqual({t:p for t,p in pmf.items() if p},{t:p for t,p in expected.items() if p})
        self.assertEqual(sum(t*p for t,p in vegas_ticket_distribution(self.rules).items()),F(5795,1024))

    def test_stage_gate_and_extremes(self):
        self.assertEqual(saturday_stages(self.rules,F(0),F(0),F(0)),{(False,0):F(1)})
        self.assertEqual(saturday_stages(self.rules,F(1),F(0),F(0)),{(True,80):F(1)})
        self.assertEqual(saturday_stages(self.rules,F(1,2),F(1),F(0)),{(False,0):F(1)})
        for first,second in ((F(1,100),F(1,20)),(F(1,20),F(1,100))):
            self.assertEqual(sum(saturday_stages(self.rules,F(7,10),first,second).values()),1)

    def test_metrics_and_quantiles(self):
        m=metrics({0:F(1,2),40:F(1,2)})
        self.assertEqual(m['expected_tickets'],20)
        self.assertEqual(m['variance'],400)
        self.assertEqual(m['standard_deviation'],20)
        self.assertEqual(m['median'],0)
        self.assertEqual(m['q90'],40)
        self.assertEqual(m['p_at_least_40'],F(1,2))
        with self.assertRaises(ValueError): metrics({0:F(1,3)})

    def test_convolution(self):
        self.assertEqual(convolution({0:F(1,2),2:F(1,2)},{0:F(1,2),2:F(1,2)}),{0:F(1,4),2:F(1,2),4:F(1,4)})

    def test_unknown_team_and_honor_are_not_zero(self):
        for name,unit in [('2v2','team'),('Free for All','individual')]:
            self.assertIsNone(solo_distribution({'event_name':name,'award_unit':unit},F(1,2)))


class WeekendPolicies(unittest.TestCase):
    def test_overlap_break_duplicate_and_daily_cap(self):
        a=v('fixed',0,660,780,10,{1:F(1)})
        for b in (v('other',0,770,800,10,{1:F(1)}),v('other',0,780,810,10,{1:F(1)}),
                  v('fixed',0,800,900,10,{1:F(1)})):
            with self.assertRaises(ValueError): validate_schedule([a,b])
        with self.assertRaises(ValueError): validate_schedule([v('long',0,645,1280,1,{1:F(1)})])
        with self.assertRaises(ValueError): validate_schedule([v('late',2,1050,1150,1,{1:F(1)})])

    def test_repeated_ode_allowed_but_time_still_finite(self):
        validate_schedule([v('ode-pod',0,660,780,10,{1:F(1)}),v('ode-pod',0,800,920,10,{1:F(1)})])

    def test_stop_and_unsuccessful_costs(self):
        visits=[v('a',0,660,720,10,{0:F(1,2),40:F(1,2)}),v('b',0,750,810,10,{0:F(1,2),40:F(1,2)})]
        states=fixed_policy(visits)
        m=terminal_metrics(states)
        self.assertEqual(sum(states.values()),1)
        self.assertEqual(m['p_at_least_40'],F(3,4))
        self.assertEqual(m['expected_entry_fee_usd'],15)
        self.assertEqual(m['success_conditional_entry_fee_usd'],F(40,3))
        self.assertEqual(m['failure_cost_contribution_usd'],5)
        self.assertTrue(all(t<=40 for t,_,_,_,_ in states))
        self.assertEqual(terminal_metrics(fixed_policy(visits,stop=False))['expected_tickets'],40)

    def test_budget_and_time_hard_limits(self):
        visits=[v('a',0,660,720,10,{20:F(1)}),v('b',0,750,810,10,{20:F(1)})]
        for kw in ({'budget':10},{'occupied_limit':60}):
            states=fixed_policy(visits,**kw)
            self.assertEqual(terminal_metrics(states)['p_at_least_40'],0)
            self.assertTrue(all(s[1]<=10 and s[2]<=60 for s in states))
        self.assertEqual(terminal_metrics(fixed_policy(visits))['expected_tickets'],40)

    def test_starting_tickets_and_overshoot(self):
        states=fixed_policy([v('a',0,660,720,10,{8:F(1)})],starting=35)
        m=terminal_metrics(states)
        self.assertEqual(m['p_at_least_40'],1)
        self.assertEqual(m['expected_unused_tickets_given_success'],3)
        self.assertIsNone(terminal_metrics({(0,0,0,F(0),0):F(1)})['success_conditional_entry_fee_usd'])

    def test_adaptive_uses_current_tickets_and_not_future(self):
        a=v('guaranteed',0,660,720,10,{10:F(1)})
        b=v('risky',0,660,720,10,{0:F(3,4),40:F(1,4)})
        high,objective,trace=adaptive_policy([[a,b]],starting=30,budget=10,occupied_limit=60)
        self.assertEqual(objective[0],1)
        self.assertEqual(trace[0]['action'],'guaranteed')
        low,objective,trace=adaptive_policy([[a,b]],budget=10,occupied_limit=60)
        self.assertEqual(objective[0],F(1,4))
        self.assertEqual(trace[0]['action'],'risky')
        self.assertEqual(terminal_metrics(low)['p_below_40'],F(3,4))
        # No clairvoyant selection of risky only when it would win.
        self.assertEqual(terminal_metrics(low)['expected_entry_fee_usd'],10)

    def test_adaptive_cannot_reuse_time_or_money(self):
        groups=[[v('a',0,660,780,10,{20:F(1)})],[v('b',0,750,870,10,{20:F(1)})]]
        states,obj,_=adaptive_policy(groups,budget=20,occupied_limit=300)
        self.assertEqual(obj[0],0)
        for budget,time in ((10,300),(20,120)):
            states,_,_=adaptive_policy([[groups[0][0]],[v('b',0,810,930,10,{20:F(1)})]],budget=budget,occupied_limit=time)
            self.assertTrue(all(s[1]<=budget and s[2]<=time for s in states))

    def test_rebound_continuation_and_no_sunday_for_nonqualified(self):
        rules=rules_from_archive(ROOT)[1]
        follow=[v('sunday',2,645,1000,50,{40:F(1)})]
        lose=rebound_policy(rules,F(0),F(0),[],follow)
        self.assertEqual(terminal_metrics(lose)['p_at_least_40'],1)
        self.assertEqual(terminal_metrics(lose)['expected_entry_fee_usd'],100)
        win=rebound_policy(rules,F(1),F(0),[],follow)
        self.assertEqual(terminal_metrics(win)['expected_entry_fee_usd'],50)
        self.assertEqual(terminal_metrics(win)['expected_tickets'],80)
        self.assertEqual(terminal_metrics(win)['expected_occupied_hours'],F(930,60))
        with self.assertRaises(ValueError): rebound_policy(rules,F(1),F(0),[],[],occupied_limit=600)

    def test_pareto_does_not_blend_objectives(self):
        rows=[{'p_at_least_40':F(1,2),'expected_entry_fee_usd':10,'expected_occupied_hours':2},
              {'p_at_least_40':F(3,4),'expected_entry_fee_usd':20,'expected_occupied_hours':3},
              {'p_at_least_40':F(1,2),'expected_entry_fee_usd':15,'expected_occupied_hours':3}]
        self.assertEqual(pareto(rows),rows[:2])


if __name__=='__main__': unittest.main()
