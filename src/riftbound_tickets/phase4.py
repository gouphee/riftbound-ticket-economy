"""Phase 4 individual acquisition research: collect, build, audit, figures."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.phase4_sources import Phase4SourceStore, collect, sources_and_inventory
from .collectors.schedules import TableRows, schedule_rule
from .models.individual import (
    PERFORMANCE, DRAWS, DAY, adaptive_policy, fixed_policy, metrics, ode_visits,
    pareto, rebound_policy, saturday_stages, solo_distribution, terminal_metrics,
    validate_schedule, visit, win_awards,
)
from .models.saturday_analytical import binomial_probabilities
from .phase3a import read_csv, rules_from_archive, sha256, write_csv, write_json

NEW_CODE = ('src/riftbound_tickets/collectors/phase4_sources.py',
            'src/riftbound_tickets/models/individual.py','src/riftbound_tickets/phase4.py',
            'src/riftbound_tickets/charts/individual.py','scripts/validate_phase4.py',
            'tests/test_individual.py','tests/test_phase4_outputs.py')


def summary_markdown(rows):
    labels={'sunday_only':'Sunday Challenge only','competitive_first':'Competitive first',
            'saturday_first':'Saturday first','mixed':'Mixed Riftbound','casual_focused':'Casual focused',
            'ode_constructed':'Constructed ODE focused','ode_tft_normal':'TFT Normal ODE focused',
            'mixed_with_tft':'Mixed with TFT','ticket_aware_adaptive':'Adaptive Riftbound menu'}
    lines=['| Strategy | P(40+) | Expected tickets | Expected entry USD | Maximum paid USD | Occupied hours | Active hours proxy |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for key,label in labels.items():
        r=next(r for r in rows if r['strategy']==key and float(r['conditional_decisive_win_probability'])==.5 and float(r['competitive_draw_rate'])==0)
        lines.append(f"| {label} | {float(r['p_at_least_40']):.4%} | {float(r['expected_tickets']):.3f} | {float(r['expected_entry_fee_usd']):.2f} | {r['maximum_spent_usd']} | {float(r['expected_occupied_hours']):.2f} | {float(r['expected_active_hours']):.2f} |")
    return '\n'.join(lines)


SUMMARY_START='<!-- phase4-summary-start -->'
SUMMARY_END='<!-- phase4-summary-end -->'


def serial(row):
    result = {}
    for key,value in row.items():
        if isinstance(value,F):
            result[key] = float(value)
            result[key+'_exact'] = str(value)
        elif value is None:
            result[key] = ''
        elif isinstance(value,(list,dict,tuple)):
            result[key] = json.dumps(value,ensure_ascii=False,separators=(',',':'))
        else:
            result[key] = value
    return result


def economics(pmf,fee,elapsed,active):
    result = metrics(pmf)
    mean = result['expected_tickets']
    result.update(entry_fee_usd=fee,elapsed_hours=elapsed,active_playing_hours=active,
                  tickets_per_entry_dollar=mean/fee if fee else None,
                  tickets_per_elapsed_hour=mean/elapsed if elapsed else None,
                  tickets_per_active_hour=mean/active if active else None,
                  expenditure_per_expected_ticket=F(fee)/mean if mean else None,
                  elapsed_hours_per_expected_ticket=elapsed/mean if mean else None)
    return result


def validate_published_awards(events,rules):
    """Independently parse the source cells before using named event models."""
    for event in events:
        if event['award_unit']=='team' or event['ticket_status']!='confirmed':
            continue
        cell=event['payout_text']
        pairs=re.findall(r'(\d+) Wins?\s*:\s*(\d+) Tickets?',cell)
        per_win=re.search(r'(\d+) Tickets per win',cell)
        if pairs or per_win:
            table={int(w):int(a) for w,a in pairs}
            if per_win: table={w:int(per_win[1])*w for w in range(event['rounds']+1)}
            expected=defaultdict(F)
            p,d=F(1,3),F(1,20)
            for w,mass in binomial_probabilities(event['rounds'],(1-d)*p).items(): expected[table.get(w,0)]+=mass
            actual=solo_distribution(event,p,d,d,rules)
            if {t:q for t,q in actual.items() if q}!={t:q for t,q in expected.items() if q}:
                raise ValueError('Model disagrees with captured payout cell: '+event['event_id'])
        if event['event_name']=='TFT Normal' or event['event_name'].startswith('Top Cut #'):
            parsed=[int(a) for a in re.findall(r':\s*(\d+) Tickets?',cell)]
            expected=[3,2,2,1] if event['event_name']=='TFT Normal' else [50,35,22,12,6,3]
            if parsed!=expected: raise ValueError('TFT placement source changed: '+event['event_id'])


def enriched_inventory(rows):
    output=[]
    for row in rows:
        name = row['event_name']
        products={'Radiance Draft':{'draft_boosters':3},'Draft Challenge':{'draft_boosters':3},
                  'Radiance Sealed Deck':{'sealed_boosters':6},'Radiance Full Box Sealed':{'sealed_boosters':24},
                  'Champion Deck Trial':{'champion_deck_kit':1},'Super Nexus Night':{'nexus_pack':1},
                  'Standard Rebound Day 1':{'participation_promo_if_seated_round1':1},
                  'Team Trios Sealed':{'sealed_boosters_per_team':15},
                  'TFT Normal':{'Space_Gods_Portal_if_rank_5_to_8':1}}
        notes=[]
        if row['award_unit']=='team':
            notes.append('No verified individual division of team tickets; no solo PMF or implicit equal split')
        if name=='Free for All':
            notes.append('Winner probability and discretionary honor recipient not observed; separate exchangeable sensitivity only')
        if name=='Team Trios Sealed':
            notes.append('315m advertised duration conflicts with 90m construction plus five 60m round limits; no solo schedule modeled')
        if 'Rebound' in name:
            notes.append('Stale Round 10 prize prose; explicit six plus five rounds governs; continuation must be reserved')
        output.append({**row,'date_local':{'friday':'2026-12-11','saturday':'2026-12-12','sunday':'2026-12-13'}.get(row['day'],'2026-12-11/13'),
                       'time_zone':'America/Los_Angeles','products_separate_from_tickets':products.get(name,{}),
                       'product_valuation':'not_valued_entry_fees_only',
                       'products_evidence':'documented_quantities_or_conditional_awards' if name in products else 'not_listed_not_confirmed_zero',
                       'seat_availability':'unknown_not_assumed_observed_capacity',
                       'registration_cutoff':'unknown; advance purchase required for fixed starts',
                       'notes':'; '.join(notes)})
    return output


def make_plans(events,p,d,queue=15,duration=None,bo1=F(0)):
    E={e['event_id']:e for e in events}
    def fixed(key):
        e=E[key]
        return visit(e,DAY[e['day']],p=p,d=d,bo1=bo1)
    def ode(day,start=660,key='ode-standard-constructed'):
        return visit(E[key],day,start,queue=queue,ode_duration=duration,p=p,d=d,bo1=bo1)
    fri=[fixed('friday-super-nexus-night')]
    sun=[fixed('sunday-radiance-standard-challenge')]
    supplement=[ode(2),fixed('sunday-radiance-sealed-deck')]
    casual=[fixed('friday-radiance-sealed-deck'),*fri,ode(1),fixed('saturday-champion-deck-trial'),
            fixed('saturday-super-nexus-night'),*supplement]
    mixed=[*fri,ode(1),fixed('saturday-champion-deck-trial'),fixed('saturday-super-nexus-night'),*sun]
    plans={'sunday_only':sun,'casual_focused':casual,'mixed':mixed,
           'ode_constructed':ode_visits(E['ode-standard-constructed'],p=p,d=d,bo1=bo1,queue=queue,duration=duration),
           'ode_tft_normal':ode_visits(E['ode-tft-normal'],p=p,d=d,bo1=bo1,queue=queue)}
    plans['mixed_with_tft']=[*fri,ode(1),fixed('saturday-top-cut-1'),fixed('sunday-top-cut-3'),ode(2,900)]
    for plan in plans.values():
        validate_schedule(plan)
    return plans,fri,sun,supplement


def adaptive_groups(events,p,d,queue=15,bo1=F(0)):
    E={e['event_id']:e for e in events}
    def f(key):
        e=E[key]
        return visit(e,DAY[e['day']],p=p,d=d,bo1=bo1)
    def o(day,start):
        return visit(E['ode-standard-constructed'],day,start,p=p,d=d,bo1=bo1,queue=queue)
    return [
        [f('friday-radiance-sealed-deck'),o(0,660)],
        [f('friday-champion-deck-trial'),f('friday-draft-challenge'),o(0,840)],
        [f('friday-super-nexus-night')],
        [o(1,660)],
        [f('saturday-champion-deck-trial'),f('saturday-radiance-sealed-deck'),f('saturday-draft-challenge')],
        [f('saturday-super-nexus-night')],
        [f('sunday-radiance-standard-challenge'),o(2,660)],
        [f('sunday-radiance-sealed-deck'),o(2,840)],
    ]


def historical_tables(root,vegas_event):
    store=EvidenceStore(root)
    ledger=[json.loads(s) for s in store.ledger.read_text().splitlines()]
    records=read_csv(root/'outputs/tables/historical_ticket_economy.csv')
    comparisons,side_inventory=[],[]
    seen=set()
    for row in records:
        if row['event_format'] not in ('friday','sunday'):
            continue
        source=next(r for r in ledger if r['source_id']==row['payout_source_id'] and r['url']==row['payout_source_url'])
        html=store.read(source).decode()
        rule=schedule_rule(html,row['event_format'])
        schedule=rule['schedule_row']
        fee=int(re.search(r'\d+',schedule[5])[0])
        duration=re.fullmatch(r'(\d+)hr:(\d+)m',schedule[3])
        hours=F(int(duration[1])*60+int(duration[2]),60) if duration else None
        for d in (F(0),F(1,50)):
            old=win_awards(rule['rounds'],rule['win_tickets'],F(1,2),d)
            new=solo_distribution(vegas_event,F(1,2),d)
            comparisons.append({'historical_event_id':row['event_key'],'historical_event_format':row['event_format'],
                'comparison_event':'sunday-radiance-standard-challenge','conditional_decisive_win_probability':F(1,2),
                'draw_rate':d,'historical_rounds':rule['rounds'],'vegas_rounds':5,
                'comparison_equivalence':'same_1v1_BO3_win_based_family_exact_structure' if rule['rounds']==5 else 'related_family_extra_historical_round_not_identical',
                'historical_win_tickets':rule['win_tickets'],'vegas_win_tickets':{3:16,4:28,5:40},
                'historical_published_fee_amount':fee,'historical_published_fee_text':schedule[5],
                'historical_currency_explicit_in_fee_cell':'CAD' if 'CA$' in schedule[5] else 'EUR' if '€' in schedule[5] else None,
                'historical_currency_status':'explicit_currency_symbol' if 'CA$' in schedule[5] or '€' in schedule[5] else 'dollar_currency_not_specified_in_cell_no_FX_conversion',
                'vegas_entry_usd':50,'historical_published_hours':hours,'vegas_published_hours':F(15,2),
                'historical_model_mean':metrics(old)['expected_tickets'],'vegas_model_mean':metrics(new)['expected_tickets'],
                'historical_model_p40':metrics(old)['p_at_least_40'],'vegas_model_p40':metrics(new)['p_at_least_40'],
                'observed_standings_implied_tickets':int(row['observed_standings_implied_tickets']),
                'observed_standings_entries':int(row['observed_n']),'observed_p40':F(row['entries_at_least_40'])/int(row['observed_n']),
                'observed_basis':row['primary_result_status'],'physical_issuance':None,
                'source_id':source['source_id'],'url':source['url'],'retrieved_at':source['retrieved_at'],
                'raw_path':source['raw_path'],'source_schedule_cells':schedule})
        if source['url'] in seen:
            continue
        seen.add(source['url'])
        parser=TableRows();parser.feed(html)
        for index,cells in enumerate(parser.rows):
            if len(cells) < 8 or not any(word in cells[1] for word in ('On Demand','Nexus','Draft','Sealed')):
                continue
            side_inventory.append({'city':row['city'],'source_row_index':index,'schedule_cells':cells,
                'event_name':cells[1],'time_or_ode':cells[0],'format':cells[2],
                'published_duration':cells[3],'payout':cells[4],'fee':cells[5],
                'source_id':source['source_id'],'url':source['url'],'retrieved_at':source['retrieved_at'],'raw_path':source['raw_path'],
                'status':'published_historical_offer_not_observed_throughput_or_weekend_participant_history'})
    return comparisons,side_inventory


def analytical_tables(root):
    sources,inventory,revisions=sources_and_inventory(root)
    inventory=enriched_inventory(inventory)
    _,rules=rules_from_archive(root)
    current=revisions['current_saturday_rules']
    if (current['point_tiers'] != [list(t) for t in rules.point_tiers]
            or (current['day1_rounds'],current['day2_rounds'],current['day2_minimum_match_points'])!=(6,5,12)):
        raise ValueError('Current Saturday payout differs; explicit rule review needed')
    validate_published_awards(inventory,rules)
    economics_rows,distributions,stage_rows=[],[],[]
    for event in inventory:
        for p in PERFORMANCE:
            for d in DRAWS:
                # Different scenarios: competitive draws do not silently transfer to BO1.
                pmf=solo_distribution(event,p,d,F(0),rules)
                if pmf is None:
                    continue
                name=event['event_name']
                if name=='Standard Rebound Day 1':
                    branches=saturday_stages(rules,p,d,d)
                    qual=sum(prob for (q,_),prob in branches.items() if q)
                    elapsed=F(9)+6*qual
                    active=F(9,2)+F(15,4)*qual
                else:
                    elapsed=F(event['published_duration_minutes'],60)
                    rounds,limit=event['rounds'],event['round_limit_minutes']
                    if name in ('Standard Constructed','Radiance Draft'):
                        rounds,limit=3,30
                    active=F(rounds*limit,80) if rounds and limit else None
                    qual=None
                base={'event_id':event['event_id'],'conditional_decisive_win_probability':p,'competitive_draw_rate':d,
                      'bo1_draw_rate':F(0),'basis':'exact_marginal_published_award_not_forecast_or_issuance',
                      'source_id':event['source_id'],'source_row_index':event['source_row_index'],
                      'tft_performance_basis':'exchangeable_full_field_not_Riftbound_skill' if event['game']=='TFT' else '',
                      'active_time_basis':'75pct_of_round_time_limits_no_measured_play' if active else 'unknown',
                      'qualification_probability':qual}
                economics_rows.append({**base,**economics(pmf,event['entry_fee_usd'],elapsed,active)})
                for tickets,prob in pmf.items():
                    distributions.append({**base,'tickets':tickets,'probability':prob})
        if event['game']=='Riftbound' and event['award_unit']=='individual' and 'Best of One' in event['format']:
            for bo1 in (F(1,50),F(1,20)):
                pmf=solo_distribution(event,F(1,2),F(0),bo1,rules)
                if pmf is not None:
                    economics_rows.append({'event_id':event['event_id'],'conditional_decisive_win_probability':F(1,2),
                        'competitive_draw_rate':F(0),'bo1_draw_rate':bo1,'basis':'separate_BO1_draw_sensitivity_not_calibrated',
                        **economics(pmf,event['entry_fee_usd'],F(event['published_duration_minutes'],60),None)})
                    for tickets,prob in pmf.items():
                        distributions.append({'event_id':event['event_id'],'conditional_decisive_win_probability':F(1,2),
                            'competitive_draw_rate':F(0),'bo1_draw_rate':bo1,'tickets':tickets,'probability':prob,
                            'basis':'separate_BO1_draw_sensitivity_not_calibrated','source_id':event['source_id'],
                            'source_row_index':event['source_row_index']})
    for p in PERFORMANCE:
        for first,second in ((F(1,100),F(1,20)),(F(1,50),F(1,50)),(F(1,20),F(1,100))):
            branches=saturday_stages(rules,p,first,second)
            pmf=defaultdict(F)
            for (_,t),mass in branches.items(): pmf[t]+=mass
            stage_rows.append({'conditional_decisive_win_probability':p,'day1_draw_rate':first,'day2_draw_rate':second,
                'basis':'imposed_stage_sensitivity_no_strategic_policy_or_record_frequency',**metrics(dict(pmf))})
    # Honor is chosen by the winner. Sweep an explicit recipient-probability range;
    # the symmetric 1/4 case is a sensitivity, never the default solo distribution.
    honor=[]
    for h in (F(0),F(1,4),F(3,4)):
        honor.append({'event_id':'ode-free-for-all','winner_probability':F(1,4),'honor_probability':h,
                      'basis':'winner_exchangeability_plus_unverified_honor_selection_sensitivity',
                      **economics({0:F(3,4)-h,1:h,2:F(1,4)},10,F(2),None)})
    plans0,_,_,_=make_plans(inventory,F(1,2),F(0))
    definitions=[]
    for name,plan in plans0.items():
        for v in plan:
            definitions.append({'strategy':name,'branch':'unconditional','event_id':v.event_id,'day':v.day,
                'start_including_queue_or_checkin_minute':v.start,'end_minute':v.end,'occupied_minutes':v.occupied,
                'entry_fee_usd':v.cost,'active_minutes_assumed':v.active,'basis':'conditional_seats_pods_and_admission_not_observed_operations'})
    _,prefix,sunday,supplement=make_plans(inventory,F(1,2),F(0))
    for name,follow in (('competitive_first',sunday),('saturday_first',supplement)):
        for branch,plan in (('Friday_prefix',prefix),('only_if_not_qualified',follow)):
            for v in plan:
                definitions.append({'strategy':name,'branch':branch,'event_id':v.event_id,'day':v.day,
                    'start_including_queue_or_checkin_minute':v.start,'end_minute':v.end,'occupied_minutes':v.occupied,
                    'entry_fee_usd':v.cost,'active_minutes_assumed':v.active})
        for day,end,duration,cost in ((1,1200,555,50),(2,1020,375,0)):
            definitions.append({'strategy':name,'branch':'Rebound_all_entrants' if day==1 else 'only_if_qualified',
                'event_id':'saturday-standard-rebound-day-1' if day==1 else 'sunday-standard-rebound-day-2','day':day,
                'start_including_queue_or_checkin_minute':645,'end_minute':end,'occupied_minutes':duration,'entry_fee_usd':cost,
                'active_minutes_assumed':270 if day==1 else 225})
    results,constrained,final_pmfs,policy_rows=[],[],[],[]
    scenario_results={}
    for p in PERFORMANCE:
        for d in DRAWS:
            plans,prefix,sunday,supplement=make_plans(inventory,p,d)
            states_by={name:fixed_policy(plan) for name,plan in plans.items()}
            states_by['competitive_first']=rebound_policy(rules,p,d,prefix,sunday)
            states_by['saturday_first']=rebound_policy(rules,p,d,prefix,supplement)
            # A fixed $200, 30 occupied-hour finite-menu policy; no Rebound or teams.
            adaptive,obj,choices=adaptive_policy(adaptive_groups(inventory,p,d),budget=200,occupied_limit=1800)
            states_by['ticket_aware_adaptive']=adaptive
            if p==F(1,2) and d==0:
                policy_rows.extend(choices)
            for name,states in states_by.items():
                base={'strategy':name,'conditional_decisive_win_probability':p,'competitive_draw_rate':d,'bo1_draw_rate':F(0),
                      'queue_minutes':15,'duration_basis':'published','stopping_policy':'stop_after_settled_event_award_reaches_40',
                      'performance_scope':'same_hypothetical_p_per_Riftbound_format_TFT_exchangeable',
                      'fee_basis':'conditional_pay_as_entered_no_refunds_assumed; advance_purchase_and_seat_availability_required',
                      'scope':'finite_Riftbound_menu' if name=='ticket_aware_adaptive' else 'representative_conditional_schedule'}
                row={**base,**terminal_metrics(states)}
                row['full_reservation_fee_exposure_usd']=sum(v.cost for v in plans[name]) if name in plans else 200 if name=='ticket_aware_adaptive' else 75+sum(v.cost for v in (sunday if name=='competitive_first' else supplement))
                results.append(row)
                if p==F(1,2) and d==0:
                    pmf=defaultdict(F)
                    for state,mass in states.items(): pmf[state[0]]+=mass
                    final_pmfs.extend({**base,'tickets':t,'probability':mass} for t,mass in sorted(pmf.items()))
            scenario_results[p,d]=[r for r in results if r['conditional_decisive_win_probability']==p and r['competitive_draw_rate']==d]
    # Separate competitive ability from limited/BO1 ability; no cross-game skill inference.
    for p in (F(7,10),F(4,5)):
        for d in (F(0),F(1,50)):
            _,prefix,_,_=make_plans(inventory,F(1,2),d)
            _,_,sunday,_=make_plans(inventory,p,d)
            state=rebound_policy(rules,p,d,prefix,sunday)
            results.append({'strategy':'competitive_first','conditional_decisive_win_probability':p,
                'competitive_draw_rate':d,'bo1_draw_rate':F(0),'queue_minutes':15,'duration_basis':'published',
                'performance_scope':'strong_competitive_only_BO1_fixed_50pct',
                'stopping_policy':'stop_after_settled_event_award_reaches_40',**terminal_metrics(state)})
    # Hard constraints change the chosen schedule, rather than conditioning away
    # failures after the fact. Rebound not included where continuation cannot fit.
    for budget in (50,100,150,200,250):
        for hours in (10,20,30):
            states,_,_=adaptive_policy(adaptive_groups(inventory,F(1,2),F(0)),budget=budget,occupied_limit=hours*60)
            constrained.append({'strategy':'ticket_aware_adaptive','conditional_decisive_win_probability':F(1,2),
                'competitive_draw_rate':F(0),'entry_budget_usd':budget,'occupied_hour_budget':hours,
                'constraint_basis':'hard_resources_policy_reoptimized_before_play',**terminal_metrics(states)})
    starting=[]
    for existing in (0,10,20,25,30,35):
        # Best immediate event is not necessarily the best sequence. Report both.
        candidates=[]
        for event in inventory:
            pmf=solo_distribution(event,F(1,2),F(0),F(0),rules)
            if pmf is None or event['event_name'] in ('Standard Rebound Day 2','Riftbound Learn to Play'):
                continue
            if event['award_unit']=='team': continue
            shifted={t+existing:mass for t,mass in pmf.items()}
            candidates.append({'starting_tickets':existing,'event_id':event['event_id'],'entry_fee_usd':event['entry_fee_usd'],
                'basis':'standalone_options_before_event_starts_no_shared_resource_optimization',**metrics(shifted)})
        starting.extend(candidates)
        remaining=[g for g in adaptive_groups(inventory,F(1,2),F(0))][-2:]
        for budget in (25,50,75):
            states,_,_=adaptive_policy(remaining,starting=existing,budget=budget,occupied_limit=465)
            starting.append({'starting_tickets':existing,'event_id':'adaptive_sunday_remaining','entry_fee_usd':budget,
                'basis':'Sunday_11am_finite_menu_maximize_success_hard_7_75_occupied_hours_including_checkin',**terminal_metrics(states)})
    queue_rows=[]
    E={r['event_id']:r for r in inventory}
    for key in ('ode-standard-constructed','ode-radiance-draft','ode-tft-normal'):
        for duration in sorted({90,E[key]['published_duration_minutes']} if key!='ode-tft-normal' else {60}):
            for queue in (0,15,45):
                for available in ('all_days','Saturday_unavailable'):
                    visits=ode_visits(E[key],queue=queue,duration=duration)
                    if available=='Saturday_unavailable': visits=[v for v in visits if v.day!=1]
                    states=fixed_policy(visits)
                    queue_rows.append({'event_id':key,'duration_minutes':duration,'queue_minutes':queue,
                        'availability_scenario':available,'maximum_events':len(visits),'maximum_tickets':len(visits)*3,
                        'duration_status':'published' if duration==E[key]['published_duration_minutes'] else 'unverified_faster_completion_sensitivity',
                        'meal_break_minutes':30,'other_break_minutes':15,'daily_occupied_limit_minutes':600,
                        **terminal_metrics(states)})
    historical,old_side=historical_tables(root,E['sunday-radiance-standard-challenge'])
    frontier=[]
    for (p,d),rows in scenario_results.items():
        for time_field in ('expected_occupied_hours','expected_calendar_span_hours'):
            for row in pareto(rows,time_field):
                frontier.append({**row,'frontier_time_objective':time_field,
                                 'frontier_scope':'nondominated_evaluated_schedules_only_conditional_on_capacity_not_global_optimum'})
    assumptions=[
        ('A01','performance','p=40/50/60/70/80% conditional decisive match wins; hypothetical per-format parameters, not population shares or fitted skill'),
        ('A02','draws','Competitive 0/1/2/5%; BO1 zero primary plus separate 2/5% sensitivities; TFT exchangeable ranks, no WDL assumption'),
        ('A03','time','Published durations; 15m fixed-event check-in; ODE queue 0/15/45m; full event award settlement; no verified early-drop payout/release'),
        ('A04','operations','ODE starts when pod fills; finite repeated slots; 15m breaks, 30m meal after second consecutive ODE; daily occupied cap 10h; event internal meal breaks unverified'),
        ('A05','cost','Entry fees only. Required festival pass, fees/taxes, deck acquisition, travel, lodging, food excluded; badge price not verified from blocked Tixr capture'),
        ('A06','availability','Every modeled seat and ODE pod is conditional; Saturday-unavailable stress scenario, no estimated fill probability; Tixr purchase possible during festival but exact cutoffs unknown'),
        ('A07','teams','All team tickets excluded from individual distributions; no transfer permission, equal division or pooling assumed'),
        ('A08','active_time','75% of per-round time limit; construction and waiting excluded; unknown for TFT. This proxy is not measured play; event-level 50/100% sensitivity supplied'),
        ('A09','optimization','Adaptive finite menu excludes Rebound, TFT, FFA, teams; maximizes success under hard budgets; ties minimize expected entry spend then occupied time; frontier limited to evaluated strategies'),
        ('A10','history','Historical side offers archived in eight official schedules; no linked attendee weekend histories, queue measurements or comparable operational model, so no historical whole-weekend forecast'),
        ('A11','redemption','40 tickets is accumulation only. Inventory, claim ledger, one-per-badge/eligibility restrictions and current ticket transfer policy unresolved; no metal ownership probability'),
        ('A12','independence','Exact marginal independent outcomes; no finite-field Swiss, byes, opponent-strength evolution or tiebreaks; constant high p likely overstates late-Swiss performance'),
    ]
    time_sensitivity=[]
    for row in economics_rows:
        if row.get('active_playing_hours'):
            for factor in (F(2,3),F(4,3)):
                hours=row['active_playing_hours']*factor
                time_sensitivity.append({'event_id':row['event_id'],'conditional_decisive_win_probability':row['conditional_decisive_win_probability'],
                    'competitive_draw_rate':row['competitive_draw_rate'],'bo1_draw_rate':row['bo1_draw_rate'],
                    'fraction_of_round_time_limit':F(3,4)*factor,'active_hours_assumed':hours,
                    'expected_tickets_per_active_hour':row['expected_tickets']/hours})
    tables={'event_inventory':inventory,'event_distributions':distributions,'event_economics':economics_rows,
            'stage_draw_sensitivity':stage_rows,'ffa_honor_sensitivity':honor,'strategy_definitions':definitions,
            'strategy_results':results,'strategy_distributions':final_pmfs,'starting_tickets':starting,
            'budget_time_constraints':constrained,'queue_duration_sensitivity':queue_rows,'pareto':frontier,
            'historical_comparisons':historical,'historical_side_inventory':old_side,'active_time_sensitivity':time_sensitivity,
            'adaptive_policy':policy_rows,
            'adaptive_menu':[{'decision_group':i,'event_id':v.event_id,'day':v.day,'start_minute':v.start,
                              'end_minute':v.end,'cost_usd':v.cost,'occupied_minutes':v.occupied}
                             for i,g in enumerate(adaptive_groups(inventory,F(1,2),F(0))) for v in g],
            'other_official_opportunities':[
                {'event':'Riftbound NA Regional Championship','source_id':sources[3]['source_id'],'url':sources[3]['url'],
                 'retrieved_at':sources[3]['retrieved_at'],'raw_path':sources[3]['raw_path'],
                 'entry_eligibility':'invitation_required','advertised_prizes':'cash_50000_USD_and_exclusive_cards_playmats',
                 'prize_wall_tickets':'not_advertised_not_verified_zero','model_status':'excluded_no_supported_ticket_award_table'},
                {'event':'TFT Vegas Open main event','source_id':sources[5]['source_id'],'url':sources[5]['url'],
                 'retrieved_at':sources[5]['retrieved_at'],'raw_path':sources[5]['raw_path'],
                 'entry_eligibility':'competitor_registration','advertised_prizes':'cash_311300_USD_and_digital_cosmetics',
                 'prize_wall_tickets':'not_advertised_not_verified_zero','model_status':'excluded_no_supported_ticket_award_table'}],
            'assumptions':[{'id':k,'topic':t,'assumption_or_gap':v} for k,t,v in assumptions]}
    return {f'phase4_{name}.csv':[serial(r) for r in rows] for name,rows in tables.items()},revisions,sources


def preservation(root):
    manifest=json.loads((root/'data/phase4/preserved_artifacts.json').read_text())
    changed=[p for p,d in manifest['files'].items() if not (root/p).is_file() or sha256(root/p)!=d]
    return {'passed':not changed,'checked_files':len(manifest['files']),'changed_files':changed}


def build(root):
    root=Path(root).resolve()
    tables,revisions,sources=analytical_tables(root)
    for name,rows in tables.items(): write_csv(root/'outputs/tables'/name,rows)
    document=root/'docs/PHASE4_INDIVIDUAL_ACQUISITION.md'
    if document.exists():
        body=document.read_text()
        if SUMMARY_START in body and SUMMARY_END in body:
            head,tail=body.split(SUMMARY_START,1)
            _,tail=tail.split(SUMMARY_END,1)
            document.write_text(head+SUMMARY_START+'\n'+summary_markdown(tables['phase4_strategy_results.csv'])+'\n'+SUMMARY_END+tail)
    write_json(root/'data/phase4/source_review.json',revisions)
    write_csv(root/'data/phase4/sources.csv',[serial(r) for r in sources])
    inputs=['data/raw/phase4/retrievals.jsonl','data/phase4/source_review.json','data/phase4/preserved_artifacts.json',
            'data/phase4/sources.csv','outputs/tables/historical_ticket_economy.csv','data/phase3a/vegas_rules.json']
    report={'model':'exact_fraction_individual_awards_convolution_and_finite_menu_Bellman_no_Monte_Carlo',
            'table_rows':{k:len(v) for k,v in tables.items()},'source_revisions':len(revisions['revisions']),
            'input_sha256':{p:sha256(root/p) for p in inputs},'code_sha256':{p:sha256(root/p) for p in NEW_CODE if (root/p).exists()},
            'output_sha256':{'outputs/tables/'+p:sha256(root/'outputs/tables'/p) for p in tables}}
    write_json(root/'outputs/tables/phase4_report.json',report)
    return report


def audit(root,write=True):
    root=Path(root).resolve()
    report=json.loads((root/'outputs/tables/phase4_report.json').read_text())
    hashes={**report['input_sha256'],**report['code_sha256'],**report['output_sha256']}
    mismatches=[p for p,d in hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    tables,review,sources=analytical_tables(root)
    differences=[]
    for name,rows in tables.items():
        fields=list(dict.fromkeys(k for r in rows for k in r))
        expected=[{k:str(r.get(k,'')) for k in fields} for r in rows]
        if read_csv(root/'outputs/tables'/name)!=expected: differences.append(name)
    if json.loads((root/'data/phase4/source_review.json').read_text())!=review: differences.append('source_review')
    document=root/'docs/PHASE4_INDIVIDUAL_ACQUISITION.md'
    if document.exists():
        body=document.read_text()
        if SUMMARY_START not in body or SUMMARY_END not in body or body.split(SUMMARY_START,1)[1].split(SUMMARY_END,1)[0].strip()!=summary_markdown(tables['phase4_strategy_results.csv']):
            differences.append('research_report_numerical_summary')
    else: differences.append('missing_research_report')
    store=Phase4SourceStore(root)
    for row in [json.loads(s) for s in store.ledger.read_text().splitlines()]: store.read(row)
    protected=preservation(root)
    figure_mismatches=[]
    path=root/'outputs/figures/phase4_manifest.json'
    if path.exists():
        manifest=json.loads(path.read_text())
        for p,d in {**manifest['input_sha256'],**manifest['figure_sha256'],**manifest['renderer_sha256']}.items():
            if not (root/p).is_file() or sha256(root/p)!=d: figure_mismatches.append(p)
    else: figure_mismatches.append('missing_figure_manifest')
    result={'passed':not mismatches and not differences and protected['passed'] and not figure_mismatches,
            'hash_mismatches':mismatches,'table_differences':differences,'preservation':protected,
            'figure_hash_mismatches':figure_mismatches,'recalculation':True}
    if write: write_json(root/'outputs/tables/phase4_validation.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('collect','build','audit','figures'))
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--refresh',action='store_true',help='Preserve fresh retrievals (collect only)')
    args=parser.parse_args()
    if args.command=='collect': collect(args.root,refresh=args.refresh)
    elif args.command=='build': print(json.dumps(build(args.root)['table_rows'],indent=2))
    elif args.command=='figures':
        from .charts.individual import render_figures
        print('\n'.join(render_figures(args.root)))
    else:
        result=audit(args.root)
        print(json.dumps(result,indent=2))
        if not result['passed']: raise SystemExit(1)


if __name__=='__main__': main()
