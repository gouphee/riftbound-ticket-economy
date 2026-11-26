"""Exact individual award and finite-menu acquisition models (no pooling).

Probabilities are rational throughout. Active playing time is an explicit
time-limit fraction, not measured play. Awards settle at event end, including
events that may distribute tickets earlier. No decisions use future outcomes.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import sqrt

from .saturday_analytical import VegasRules, binomial_probabilities, vegas_point_award
from .saturday_draws import OutcomeProbabilities, match_point_distribution

PERFORMANCE = tuple(F(n, 10) for n in range(4, 9))
DRAWS = (F(0), F(1, 100), F(1, 50), F(1, 20))


def outcomes(p: F, d: F) -> OutcomeProbabilities:
    if type(p) not in (int, F) or type(d) not in (int, F) or not 0 <= p <= 1 or not 0 <= d <= 1:
        raise ValueError('Use exact probabilities in [0,1]')
    return OutcomeProbabilities((1-d)*p, d, (1-d)*(1-p))


def win_awards(rounds: int, table: dict[int, int], p: F, d: F = F(0)) -> dict[int, F]:
    probabilities = outcomes(p, d)
    if any(type(w) is not int or not 0 <= w <= rounds or type(a) is not int or a < 0 for w, a in table.items()):
        raise ValueError('Invalid win-award table')
    result = {a: F(0) for a in sorted({0, *table.values()})}
    for wins, mass in binomial_probabilities(rounds, probabilities.win).items():
        result[table.get(wins, 0)] += mass
    return result


def metrics(pmf: dict[int, F]) -> dict:
    if sum(pmf.values()) != 1 or any(t < 0 or p < 0 for t, p in pmf.items()):
        raise ValueError('Invalid ticket PMF')
    mean = sum(t*p for t, p in pmf.items())
    variance = sum(t*t*p for t, p in pmf.items())-mean*mean
    def quantile(q):
        mass = F(0)
        for t, p in sorted(pmf.items()):
            mass += p
            if mass >= q:
                return t
    result = {'expected_tickets':mean, 'variance':variance, 'standard_deviation':sqrt(variance),
              'p_zero':pmf.get(0, F(0)), 'q10':quantile(F(1,10)), 'median':quantile(F(1,2)),
              'q90':quantile(F(9,10)), 'q95':quantile(F(95,100))}
    result.update({f'p_at_least_{k}':sum((p for t,p in pmf.items() if t >= k), F(0)) for k in (10,20,30,40)})
    return result


def convolution(a, b):
    result = defaultdict(F)
    for x, p in a.items():
        for y, q in b.items():
            result[x+y] += p*q
    return dict(result)


def saturday_stages(rules: VegasRules, p: F, first_draw: F, second_draw: F):
    """Small stage-dependent draw sensitivity; rates are imposed, not strategic."""
    first = match_point_distribution(6, outcomes(p, first_draw))
    second = match_point_distribution(5, outcomes(p, second_draw))
    result = defaultdict(F)
    for points, mass in first.items():
        if not mass:
            continue
        if points < rules.day2_minimum_match_points:
            result[(False, 0)] += mass
        else:
            for extra, conditional in second.items():
                if conditional:
                    result[(True, vegas_point_award(points+extra, rules))] += mass*conditional
    assert sum(result.values()) == 1
    return dict(result)


def solo_distribution(event: dict, p: F, competitive_draw=F(0), bo1_draw=F(0), rules=None):
    name = event['event_name']
    if event['award_unit'] == 'team':
        return None
    if name == 'Standard Rebound Day 1':
        result = defaultdict(F)
        for (_, tickets), mass in saturday_stages(rules, p, competitive_draw, competitive_draw).items():
            result[tickets] += mass
        return dict(result)
    if name == 'Radiance Standard Challenge':
        return win_awards(5, {3:16,4:28,5:40}, p, competitive_draw)
    if name in ('Standard Constructed', 'Radiance Draft'):
        return win_awards(3, {w:w for w in range(4)}, p, bo1_draw)
    if name == 'Super Nexus Night' or name == 'Radiance Full Box Sealed':
        return win_awards(4, {w:2*w for w in range(5)}, p, bo1_draw)
    if name == 'Radiance Sealed Deck':
        return win_awards(3, {w:2+2*w for w in range(4)}, p, bo1_draw)
    if name in ('Champion Deck Trial', 'Draft Challenge'):
        return win_awards(3, {w:1+w for w in range(4)}, p,
                          competitive_draw if name == 'Draft Challenge' else bo1_draw)
    if name == 'TFT Normal':
        # Exchangeable eight-player finish ranks. Riftbound p has no effect.
        return {0:F(1,2),1:F(1,8),2:F(1,4),3:F(1,8)}
    if name.startswith('Top Cut #'):
        # Full advertised 64-player field, uniform final rank slots.
        return {0:F(32,64),3:F(16,64),6:F(8,64),12:F(4,64),22:F(2,64),35:F(1,64),50:F(1,64)}
    if name == 'Riftbound Learn to Play':
        return {0:F(1)}  # Explicitly no advertised prize; never used as a ticket path.
    return None  # FFA honor selection / continuation / other unknowns are not zero.


DAY = {'friday':0, 'saturday':1, 'sunday':2}
OPEN, CLOSE = 660, (1290,1290,1110)


@dataclass(frozen=True)
class Visit:
    event_id: str
    day: int
    start: int
    end: int
    cost: int
    active: F
    occupied: int
    pmf: tuple[tuple[int,F], ...]


def visit(event, day, start=None, *, queue=15, ode_duration=None, active_fraction=F(3,4), p=F(1,2), d=F(0), bo1=F(0), rules=None):
    is_ode = event['day'] == 'ode'
    begin = start if is_ode else event['start_minute']
    duration = (ode_duration if ode_duration is not None else event['published_duration_minutes']) if is_ode else event['published_duration_minutes']
    overhead = queue if is_ode else 15
    end = begin+overhead+duration if is_ode else begin+duration
    pmf = solo_distribution(event, p, d, bo1, rules)
    if pmf is None:
        raise ValueError('No supported individual PMF: '+event['event_id'])
    rounds, limit = event['rounds'], event['round_limit_minutes']
    if event['event_name'] in ('Standard Constructed','Radiance Draft'):
        rounds, limit = 3,30
    active = F(rounds*limit)*active_fraction if rounds and limit else F(0)
    if event['game'] == 'TFT':
        # Whole published duration proxy; no measured active game duration.
        active = F(duration)*active_fraction
    return Visit(event['event_id'],day,begin if is_ode else begin-overhead,end,event['entry_fee_usd'],
                 active,duration+overhead,tuple(sorted(pmf.items())))


def validate_schedule(visits, *, daily_limit=600, break_minutes=15):
    if [(v.day,v.start) for v in visits] != sorted((v.day,v.start) for v in visits):
        raise ValueError('Visits must be in chronological order')
    days = defaultdict(list)
    for v in visits:
        if v.day not in range(3) or v.end > CLOSE[v.day] or v.end <= v.start or v.start < (OPEN if v.event_id.startswith('ode-') else OPEN-15):
            raise ValueError('Visit outside event window')
        days[v.day].append(v)
    for rows in days.values():
        if sum(v.occupied for v in rows) > daily_limit:
            raise ValueError('Daily occupied-hour limit exceeded')
        for previous, current in zip(rows, rows[1:]):
            if current.start < previous.end+break_minutes:
                raise ValueError('Overlapping events or insufficient break')
    fixed_ids = [v.event_id for v in visits if not v.event_id.startswith('ode-')]
    if len(fixed_ids) != len(set(fixed_ids)):
        raise ValueError('Repeated fixed event')


def ode_visits(event, *, queue=15, duration=None, daily_limit=600, **kwargs):
    result = []
    for day in range(3):
        start, used = OPEN, 0
        while True:
            v = visit(event,day,start,queue=queue,ode_duration=duration,**kwargs)
            if v.end > CLOSE[day] or used+v.occupied > daily_limit:
                break
            result.append(v)
            used += v.occupied
            # One 30-minute meal break per day, 15-minute other breaks.
            start = v.end+(30 if len([x for x in result if x.day==day]) == 2 else 15)
    validate_schedule(result,daily_limit=daily_limit)
    return result


# Terminal tuple: final tickets, entry expenditure, occupied minutes, active
# minutes, calendar finish offset from Friday 11:00. Success paths stop at the
# event boundary; failures remain in the distribution and expenditure averages.
Terminal = tuple[int,int,int,F,int]


def fixed_policy(visits, *, starting=0, budget=1000, occupied_limit=2000, stop=True):
    if starting < 0 or budget < 0 or occupied_limit < 0:
        raise ValueError('Invalid starting resources')
    validate_schedule(visits)
    states = {(starting,0,0,F(0),0):F(1)}
    for v in visits:
        next_states = defaultdict(F)
        for (t,c,m,a,finish), mass in states.items():
            if (stop and t >= 40) or c+v.cost > budget or m+v.occupied > occupied_limit:
                next_states[(t,c,m,a,finish)] += mass
                continue
            for award, probability in v.pmf:
                if probability:
                    next_states[(t+award,c+v.cost,m+v.occupied,a+v.active,v.day*1440+v.end-OPEN)] += mass*probability
        states = dict(next_states)
    if sum(states.values()) != 1:
        raise ValueError('Weekend probability mass not conserved')
    return states


def terminal_metrics(states):
    pmf = defaultdict(F)
    for (t,_,_,_,_), mass in states.items():
        pmf[t] += mass
    result = metrics(dict(pmf))
    success = result['p_at_least_40']
    for index,name,scale in ((1,'entry_fee_usd',1),(2,'occupied_hours',60),(3,'active_hours',60),(4,'calendar_span_hours',60)):
        total = sum(state[index]*mass for state,mass in states.items())/scale
        result['expected_'+name] = total
        result['success_conditional_'+name] = sum(state[index]*mass for state,mass in states.items() if state[0]>=40)/success/scale if success else None
    result['maximum_spent_usd'] = max(s[1] for s,p in states.items() if p)
    result['p_below_40'] = 1-success
    result['expected_unused_tickets_given_success'] = sum((s[0]-40)*p for s,p in states.items() if s[0]>=40)/success if success else None
    result['expected_unused_tickets_unconditional'] = sum(max(0,s[0]-40)*p for s,p in states.items())
    result['success_cost_contribution_usd'] = sum((s[1]*p for s,p in states.items() if s[0]>=40),F(0))
    result['failure_cost_contribution_usd'] = sum((s[1]*p for s,p in states.items() if s[0]<40),F(0))
    result['entry_dollars_per_expected_ticket'] = result['expected_entry_fee_usd']/result['expected_tickets'] if result['expected_tickets'] else None
    result['occupied_hours_per_expected_ticket'] = result['expected_occupied_hours']/result['expected_tickets'] if result['expected_tickets'] else None
    return result


def rebound_policy(rules, p, d, prefix, nonqualifying_sunday, *, starting=0, budget=1000, occupied_limit=2000):
    """Enter Saturday only if still short; Sunday alternatives only if eliminated.

    Saturday's Day 1 is fully reserved through 20:00. No unverified early-drop
    eligibility/release time is invented. Qualifiers reserve Sunday until 17:00.
    """
    validate_schedule(prefix)
    validate_schedule(nonqualifying_sunday)
    if any(v.day != 0 for v in prefix) or any(v.day != 2 for v in nonqualifying_sunday):
        raise ValueError('Rebound prefix must be Friday; elimination alternatives must be Sunday')
    before = fixed_policy(prefix,starting=starting,budget=budget,occupied_limit=occupied_limit)
    result = defaultdict(F)
    branches = saturday_stages(rules,p,d,d)
    for state,mass in before.items():
        t,c,m,a,f = state
        if t >= 40 or c+50 > budget or m+555 > occupied_limit:
            result[state] += mass
            continue
        for (qualifies,award),prob in branches.items():
            if not prob:
                continue
            extra = 375 if qualifies else 0  # 6h + 15m check-in on Sunday.
            if m+555+extra > occupied_limit:
                # Committing to Rebound requires capacity to honor qualification.
                raise ValueError('Time budget cannot honor conditional Rebound continuation')
            base = (t+award,c+50,m+555+extra,a+F(270)+(F(225) if qualifies else 0),
                    2*1440+1020-OPEN if qualifies else 1440+1200-OPEN)
            if qualifies:
                result[base] += mass*prob
            else:
                follow = fixed_policy(nonqualifying_sunday,starting=t,budget=budget-c-50,occupied_limit=occupied_limit-m-555)
                for (tt,cc,mm,aa,ff),q in follow.items():
                    end = ff if mm else base[4]
                    result[(tt,c+50+cc,m+555+mm,a+F(270)+aa,end)] += mass*prob*q
    return dict(result)


def adaptive_policy(groups, *, starting=0, budget=200, occupied_limit=1800, daily_limit=600):
    """Maximize P(40+) within a declared finite action menu and hard resources.

    Ties prefer smaller expected expenditure, then occupied minutes. Those
    tie-breakers do not trade off success. This is not a global weekend optimum.
    State includes only information already observed. Groups must be in time
    order; later event durations may skip conflicting groups.
    """
    for group in groups:
        for v in group:
            if v.end > CLOSE[v.day] or v.occupied > daily_limit:
                raise ValueError('Invalid adaptive action')
    choices = {}
    @lru_cache(None)
    def value(i,t,b,minutes,day_used,last_day,last_end):
        if i == len(groups) or t >= 40:
            return (F(t>=40),F(0),F(0))
        key = (i,t,b,minutes,day_used,last_day,last_end)
        best = value(i+1,t,b,minutes,day_used,last_day,last_end)
        choices[key] = None
        for v in groups[i]:
            used = day_used if v.day==last_day else 0
            if (v.cost > b or v.occupied > minutes or used+v.occupied > daily_limit
                    or v.day < last_day
                    or (v.day==last_day and v.start < last_end+15)):
                continue
            success, cost, duration = F(0),F(v.cost),F(v.occupied)
            for award,q in v.pmf:
                if q:
                    child = value(i+1,min(40,t+award),b-v.cost,minutes-v.occupied,used+v.occupied,v.day,v.end)
                    success += q*child[0]
                    cost += q*child[1]
                    duration += q*child[2]
            candidate = (success,cost,duration)
            if (candidate[0],-candidate[1],-candidate[2]) > (best[0],-best[1],-best[2]):
                best = candidate
                choices[key] = v
        return best
    objective = value(0,min(starting,40),budget,occupied_limit,0,-1,-100)
    states = {(starting,0,0,F(0),0,0,-1,-100):F(1)}
    trace = []
    for i in range(len(groups)):
        nxt = defaultdict(F)
        for (t,c,m,a,finish,used,day,end),mass in states.items():
            key = (i,min(40,t),budget-c,occupied_limit-m,used,day,end)
            v = choices.get(key)
            trace.append({'decision_group':i,'tickets_observed':t,'entry_budget_remaining':budget-c,
                          'occupied_minutes_remaining':occupied_limit-m,'day_minutes_used':used,
                          'previous_day':day,'previous_end_minute':end,
                          'action':v.event_id if v is not None and t<40 else 'stop' if t>=40 else 'skip',
                          'state_probability':mass})
            if t>=40 or v is None:
                nxt[(t,c,m,a,finish,used,day,end)] += mass
            else:
                for award,q in v.pmf:
                    if q:
                        nxt[(t+award,c+v.cost,m+v.occupied,a+v.active,v.day*1440+v.end-OPEN,
                             (used if v.day==day else 0)+v.occupied,v.day,v.end)] += mass*q
        states = dict(nxt)
    terminal = defaultdict(F)
    for (t,c,m,a,f,_,_,_),mass in states.items():
        terminal[(t,c,m,a,f)] += mass
    if sum(terminal.values()) != 1 or terminal_metrics(terminal)['p_at_least_40'] != objective[0]:
        raise ValueError('Adaptive policy replay differs from Bellman objective')
    return dict(terminal), objective, trace


def pareto(rows, time_field='expected_occupied_hours'):
    """Scenario-specific nondominated rows; zero-success paths are retained."""
    def dominates(a,b):
        aa=(a['p_at_least_40'],-a['expected_entry_fee_usd'],-a[time_field])
        bb=(b['p_at_least_40'],-b['expected_entry_fee_usd'],-b[time_field])
        return all(x>=y for x,y in zip(aa,bb)) and any(x>y for x,y in zip(aa,bb))
    return [r for r in rows if not any(dominates(other,r) for other in rows)]
