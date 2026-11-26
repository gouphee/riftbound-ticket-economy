"""Focused team awards and aggregation, isolated from completed Phase 4."""
from __future__ import annotations
import argparse
import json
import re
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from .collectors.phase5_sources import Phase5SourceStore,URLS,RULES,HUB,collect,evidence
from .collectors.phase3a_sources import verify_announcement_content
from .models.aggregation import (allocate_two,allocate_team,group_metrics,independent_joint,joint_convolve,
    partial_metrics,without_replacement)
from .models.individual import (PERFORMANCE,DRAWS,Visit,convolution,fixed_policy,metrics,
    ode_visits,outcomes,terminal_metrics,win_awards,validate_schedule)
from .models.saturday_analytical import historical_ticket_distribution
from .models.saturday_draws import match_point_distribution,vegas_draw_ticket_distribution
from .phase3a import read_csv,rules_from_archive,sha256,write_csv,write_json
from .phase4 import serial,make_plans

GROUPS=(1,2,4,8)
NEW_CODE=('src/riftbound_tickets/models/aggregation.py','src/riftbound_tickets/phase5.py',
          'src/riftbound_tickets/collectors/phase5_sources.py','src/riftbound_tickets/charts/aggregation.py',
          'scripts/validate_phase5.py','tests/test_aggregation.py','tests/test_phase5_outputs.py')


def report_summary(rows):
    lines=['| People | Historical: no pooling | Historical: full pool | Vegas: no pooling | Vegas: full pool | Pooling increment, historical → Vegas |',
           '|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        if r['historical_allocation']!='historical_official' or r['vegas_draw_rate_exact']!='0' or r['group_size']==1:continue
        fields=('historical_p_any_individual_40','historical_p_aggregate_40','vegas_p_any_individual_40','vegas_p_aggregate_40')
        vals=[f'{float(r[k]):.2%}' for k in fields]
        gain=f"{100*float(r['historical_incremental_success_probability']):.2f} → {100*float(r['vegas_incremental_success_probability']):.2f} pp"
        lines.append('| '+str(r['group_size'])+' | '+' | '.join(vals)+' | '+gain+' |')
    return '\n'.join(lines)


def team_pmf(event,p,d):
    cell=event['payout_text'];rounds=event['rounds']
    if event['event_name']=='Radiance 2v2 Team Challenge':
        tiers=[(int(a),int(b or a),int(t)) for a,b,t in re.findall(r'(\d+)(?:-(\d+))? Match Points\s*:\s*(\d+) Tickets',cell)]
        if tiers!=[(15,15,80),(13,14,60),(12,12,40),(10,11,25),(9,9,10),(7,8,5)]:
            raise ValueError('Review changed Friday team payout')
        result={t:F(0) for t in (0,5,10,25,40,60,80)}
        for points,mass in match_point_distribution(5,outcomes(p,d)).items():
            award=next((t for a,b,t in tiers if a<=points<=b),0)
            result[award]+=mass
        return result
    pairs=re.findall(r'(\d+) Wins?\s*:\s*(\d+) Tickets',cell)
    if event['award_unit']!='team' or not pairs or not rounds: raise ValueError('Unsupported team event')
    return win_awards(rounds,{int(w):int(t) for w,t in pairs},p,d)


def allocate_pmf(pmf,allocation,role,size=2):
    result=defaultdict(F)
    for t,p in pmf.items(): result[allocate_team(t,size,allocation)[role]]+=p
    return dict(result)


def policy_review(root,sources):
    text=' '.join((root/'data/phase5/tournament_rules_extracted.txt').read_text().split())
    if not all(s in text for s in ('October 9, 2026','704.5.b.','Sharing prizes','704.5.a.')):
        raise ValueError('Reviewed current rules extraction changed')
    store=Phase5SourceStore(root)
    if sha256(root/'data/phase5/tournament_rules.pdf')!=sources[6]['sha256']:
        raise ValueError('Readable PDF differs from source capture')
    if sources[6]['http_status']!=200 or RULES not in store.read(sources[5]).decode():
        raise ValueError('Current rules not linked by captured official hub')
    schedule=sources[0];pdf=sources[6];signup=sources[1]
    definitions=[
        ('specific_event_addenda','explicit_precedence',pdf,1,'104.3',
         'Official event-specific addenda take precedence over the general tournament rules'),
        ('general_prize_sharing','conditional_permission',pdf,48,'704.5.b',
         'General prize-sharing agreements permitted subject to no exchange for match outcomes, game actions or dropping; not a specific ticket-transfer rule'),
        ('outcome_contingent_rewards','explicit_prohibition',pdf,48,'704.5.a',
         'Rewards or incentives may not determine tournament-game outcomes; no manipulated outcomes modeled'),
        ('prize_ticket_ownership_and_transfer','ambiguous_no_specific_rule_found',pdf,None,None,
         'No specific post-award prize-ticket ownership/transfer permission established in reviewed rules or event pages'),
        ('combining_attendees_tickets','unavailable_event_specific_permission',schedule,None,'catalog',
         'Cross-event prize eligibility is explicit, but combining tickets across attendees is not established'),
        ('metal_per_person_or_badge_limit','unavailable',schedule,None,'catalog',
         '40-ticket price verified; no inventory quantity or per-person/badge limit established'),
        ('side_event_pass_and_registration','explicit_requirement',signup,None,'How to Sign-Up',
         'Valid festival/competitor pass and Riot ID required for side-event entry; fixed events purchased ahead through Tixr'),
        ('friday_team_award_unit','explicit_team_total',schedule,None,'Friday Radiance 2v2 Team Challenge',
         'Published tickets are per team; individual ownership/allocation remains unspecified'),
        ('friday_fee_unit','ambiguous',schedule,None,'Friday Radiance 2v2 Team Challenge',
         '$50 published without per-team/per-player qualifier; both cost interpretations modeled'),
        ('team_ode_registration','explicit_individual_registration',schedule,None,'2v2 ODE',
         'Eight individually enrolled players form four teams; two BO1 rounds; 3/6 tickets per team at one/two wins'),
        ('ticket_vendor_details','unavailable_HTTP_'+str(sources[2]['http_status']),sources[2],None,None,
         'No verified vendor clarification of fee unit, allocation, transfer, cutoffs or redemption'),
    ]
    return [{'topic':topic,'evidence_status':status,'source_id':src['source_id'],'url':src['url'],
             'retrieved_at':src['retrieved_at'],'raw_path':src['raw_path'],'pdf_page':page,
             'section_or_locator':section,'finding_and_scope':finding} for topic,status,src,page,section,finding in definitions]


def team_weekend(event,events,p_team=F(1,2),p_solo=F(1,2),allocation='integer_equal',fee_person=50):
    """Friday shared outcome, then each member's own stopped mixed schedule.

    Team event conflicts with Friday Nexus, so it REPLACES that prefix. Shared
    Friday awards are sampled once; later individual paths are independent
    conditional on the shared outcome. Neither cross-team Swiss independence
    nor the allocation rule is asserted as observed or permitted.
    """
    plans,_,_,_=make_plans(events,p_solo,F(0))
    suffix=[v for v in plans['mixed'] if v.day>0]
    validate_schedule(suffix)
    friday=Visit(event['event_id'],0,645,1110,fee_person,F(375,2),465,())
    validate_schedule([friday,*suffix])
    joint=defaultdict(F);marginals=[defaultdict(F),defaultdict(F)];pair_wall=defaultdict(F)
    resources=[{'cost':F(fee_person),'hours':F(465,60)},{'cost':F(fee_person),'hours':F(465,60)}]
    pmf=team_pmf(event,p_team,F(0))
    for tickets,prob in pmf.items():
        if not prob: continue
        awards=allocate_two(tickets,allocation)
        results=[];finishes=[]
        for role,award in enumerate(awards):
            states=fixed_policy(suffix,starting=award)
            dist=defaultdict(F)
            for state,mass in states.items(): dist[state[0]]+=mass
            results.append(dist)
            clock=defaultdict(F)
            for state,mass in states.items(): clock[F(state[4],60) if state[2] else F(15,2)]+=mass
            finishes.append(clock)
            for t,mass in dist.items(): marginals[role][t]+=prob*mass
            for state,mass in states.items():
                resources[role]['cost']+=prob*mass*state[1]
                resources[role]['hours']+=prob*mass*F(state[2],60)
        for a,pa in results[0].items():
            for b,pb in results[1].items(): joint[(a+b,a//40+b//40,int(a>=40)+int(b>=40))]+=prob*pa*pb
        for a,pa in finishes[0].items():
            for b,pb in finishes[1].items(): pair_wall[max(a,b)]+=prob*pa*pb
    assert sum(joint.values())==1
    return dict(joint),[dict(d) for d in marginals],resources,dict(pair_wall)


def expected_max_clock(pmf,n):
    """Independent clock blocks: E[max], not the sum of member clocks."""
    total=cumulative=previous=F(0)
    for hour,mass in sorted(pmf.items()):
        cumulative+=mass
        total+=hour*(cumulative**n-previous**n)
        previous=cumulative
    if cumulative!=1: raise ValueError('Clock PMF not normalized')
    return total


def baseline_weekends(root):
    distributions=read_csv(root/'outputs/tables/phase4_strategy_distributions.csv')
    results=read_csv(root/'outputs/tables/phase4_strategy_results.csv')
    answer={}
    for name in ('competitive_first','mixed','ticket_aware_adaptive','ode_constructed'):
        pmf={int(r['tickets']):F(r['probability_exact']) for r in distributions if r['strategy']==name}
        row=next(r for r in results if r['strategy']==name and r['conditional_decisive_win_probability_exact']=='1/2' and r['competitive_draw_rate_exact']=='0')
        if metrics(pmf)['expected_tickets']!=F(row['expected_tickets_exact']): raise ValueError('Phase 4 PMF/metrics mismatch')
        answer[name]=(pmf,row)
    return answer


def historical_odes(root):
    from .collectors.evidence import EvidenceStore
    from .collectors.schedules import TableRows
    store=EvidenceStore(root)
    ledger=[json.loads(s) for s in store.ledger.read_text().splitlines()]
    result=[]
    for row in read_csv(root/'outputs/tables/phase4_historical_side_inventory.csv'):
        if row['event_name']!='On Demand Competitive Constructed': continue
        source=next(r for r in ledger if r['source_id']==row['source_id'] and r['url']==row['url'])
        parser=TableRows();parser.feed(store.read(source).decode())
        cells=parser.rows[int(row['source_row_index'])]
        if cells!=json.loads(row['schedule_cells']) or cells[3]!='3hr:45m' or '3 Wins : 12 PW Tickets' not in cells[4] or 'single elimination' not in cells[-1]:
            raise ValueError('Historical ODE source no longer reconciles')
        casual=[(i,r) for i,r in enumerate(parser.rows) if len(r)>7 and r[1]=='On Demand Constructed']
        if len(casual)!=1 or casual[0][1][3]!='2hr:15m' or not all(f'{w} Wins : {w} PW Tickets' in casual[0][1][4] for w in (2,3)):
            raise ValueError('Concurrent historical casual ODE offer needs review')
        result.append({**row,'maximum_tickets':12,'rounds_to_win':3,'published_duration_minutes':225,
                       'concurrent_casual_source_row_index':casual[0][0],'concurrent_casual_schedule_cells':casual[0][1],
                       'concurrent_casual_duration_minutes':135,'concurrent_casual_payout':casual[0][1][4],
                       'actual_desk_hours':None,'fee_currency':'CAD' if 'CA$' in row['fee'] else 'EUR' if '€' in row['fee'] else 'dollar_currency_not_explicit_in_cell'})
    if len(result)!=8: raise ValueError('Expected comparable offer in eight archived locations')
    return result


def analytical_tables(root):
    sources,events=evidence(root)
    prior={r['event_id']:json.loads(r['raw_cells']) for r in read_csv(root/'outputs/tables/phase4_event_inventory.csv')}
    if any(prior.get(e['event_id'])!=e['raw_cells'] for e in events) or len(prior)!=len(events):
        raise ValueError('Current schedule changed: review before modeling')
    _,rules=rules_from_archive(root)
    policies=policy_review(root,sources)
    inventory=[{**e,'individual_ticket_entitlement':None,
                'model_status':'Riftbound_team_WDL_sensitivity' if e['game']=='Riftbound' else 'TFT_team_format_not_assigned_a_Riftbound_WDL_model',
                'non_ticket_product_quantity':15 if e['event_name']=='Team Trios Sealed' else None,
                'non_ticket_product_unit':'booster_packs_per_team_for_construction' if e['event_name']=='Team Trios Sealed' else 'see_original_prize_cells_unknown_not_zero'}
               for e in events if e['award_unit']=='team']
    E={e['event_id']:e for e in events}
    friday=E['friday-radiance-2v2-team-challenge']
    team_rows,team_distributions,allocations=[],[],[]
    rift_teams=[e for e in inventory if e['game']=='Riftbound']
    for event in rift_teams:
        for p in PERFORMANCE:
            for d in DRAWS:
                pmf=team_pmf(event,p,d)
                base={'event_id':event['event_id'],'team_decisive_win_probability':p,'draw_rate':d,
                      'performance_basis':'hypothetical_team_round_probability_not_derived_from_individual_p',
                      'source_id':event['source_id'],'source_row_index':event['source_row_index']}
                team_rows.append({**base,**metrics(pmf),'duration_hours':F(event['published_duration_minutes'],60),
                    'fee_text':event['entry_fee_text'],'fee_unit':event['fee_unit'],
                    'individual_entitlement':'unknown_allocation_not_verified'})
                team_distributions.extend({**base,'team_tickets':t,'probability':mass} for t,mass in pmf.items())
                size=3 if event['event_name']=='Team Trios Sealed' else 2
                fees=(25,50) if event['event_name']=='Radiance 2v2 Team Challenge' else (event['entry_fee_usd'],)
                for allocation in ('integer_equal','prioritize_A'):
                    for role in range(size):
                        apmf=allocate_pmf(pmf,allocation,role,size)
                        for fee in fees:
                            allocations.append({**base,'allocation':allocation,'role':chr(65+role),
                                'role_index':role,'team_size':size,
                                'allocation_status':'hypothetical_not_verified','entry_fee_per_person_scenario_usd':fee,
                                'entry_fee_per_team_scenario_usd':size*fee,**metrics(apmf),
                                'tickets_per_entry_dollar':metrics(apmf)['expected_tickets']/fee,
                                'occupied_hours':F(event['published_duration_minutes']+15,60)})
    saturday=[]
    for split in (False,True):
        pmf=historical_ticket_distribution(512,split_top8=split)
        counts={t:int(p*512) for t,p in pmf.items() if p}
        for method in ('without_replacement','independent'):
            for n in GROUPS:
                joint=without_replacement(counts,n) if method=='without_replacement' else independent_joint(pmf,n)
                saturday.append({'event_model':'historical_split' if split else 'historical_official','draw_rate':F(0),
                    'field_size':512,'sampling':method,'scope':'conditional_funded_rank_slots_not_actual_split_or_issuance',**group_metrics(joint,n)})
    for d in DRAWS:
        pmf=vegas_draw_ticket_distribution(rules,outcomes(F(1,2),d))
        for n in GROUPS:
            saturday.append({'event_model':'vegas_rebound','draw_rate':d,'field_size':512,
                'sampling':'independent','scope':'marginal_independence_counterfactual_not_joint_finite_field_Swiss',
                **group_metrics(independent_joint(pmf,n),n)})
    comparisons=[]
    for d in DRAWS:
        for split in (False,True):
            for n in GROUPS:
                old=next(r for r in saturday if r['event_model']==('historical_split' if split else 'historical_official') and r['sampling']=='without_replacement' and r['group_size']==n)
                new=next(r for r in saturday if r['event_model']=='vegas_rebound' and r['draw_rate']==d and r['group_size']==n)
                row={'group_size':n,'vegas_draw_rate':d,'historical_allocation':old['event_model'],
                     'old_method':'without_replacement','new_method':'independent_marginals'}
                for key in ('p_any_individual_40','p_aggregate_40','incremental_success_probability','relative_success_lift',
                            'units_no_pool_per_participant','units_full_pool_per_participant','incremental_units_per_participant',
                            'expected_fragmented_tickets_no_pool','expected_residual_full_pool'):
                    row['historical_'+key]=old[key];row['vegas_'+key]=new[key]
                row['new_minus_old_increment_pp']=100*(new['incremental_success_probability']-old['incremental_success_probability'])
                row['new_minus_old_pooled_success_pp']=100*(new['p_aggregate_40']-old['p_aggregate_40'])
                row['new_minus_old_incremental_units_per_participant']=new['incremental_units_per_participant']-old['incremental_units_per_participant']
                comparisons.append(row)
    weekends,partial,week_pmfs=[],[],[]
    for name,(pmf,r) in baseline_weekends(root).items():
        clock={'competitive_first':{F(54):F(11,32),F(111,2):F(21,32)},
               'mixed':{F(111,2):F(1)},'ticket_aware_adaptive':{F(111,2):F(1)},
               'ode_constructed':{F(213,4):F(1)}}[name]
        if expected_max_clock(clock,1)!=F(r['expected_calendar_span_hours_exact']): raise ValueError('Phase4 clock reconstruction differs')
        for n in GROUPS:
            weekends.append({'strategy':name,'allocation':'individual_original','stopping_policy':'each_individual_stops_at_40_event_boundary',
                'dependence':'independent_individual_weekends_not_shared_target_stop','resource_basis':'unconditional_means_include_failures',
                'group_entry_expenditure_usd':n*F(r['expected_entry_fee_usd_exact']),
                'per_participant_entry_expenditure_usd':F(r['expected_entry_fee_usd_exact']),
                'participant_hours':n*F(r['expected_occupied_hours_exact']),
                'per_participant_occupied_hours':F(r['expected_occupied_hours_exact']),
                'elapsed_group_wall_hours':expected_max_clock(clock,n),
                'wall_time_status':'Friday_11am_to_last_member_stop_includes_nights_independent_clock_blocks',
                **group_metrics(independent_joint(pmf,n),n)})
            for policy in ('own_first_surplus','keep10_remainders'):
                partial.append({'strategy':name,'individual_stopping':'original_Phase4_stop_at_40',**partial_metrics(pmf,n,policy)})
    # Two concrete, paired weekend allocations. Equal allocation never doubles
    # a team prize; the shared Friday outcome is one common random variable.
    for allocation in ('integer_equal','prioritize_A'):
        for fee in (25,50):
            joint,marginals,resources,pair_wall=team_weekend(friday,events,allocation=allocation,fee_person=fee)
            for role in (0,1):
                week_pmfs.extend({'strategy':'Friday_team_then_mixed','allocation':allocation,'role':'A' if role==0 else 'B',
                    'fee_person_usd':fee,'tickets':t,'probability':mass} for t,mass in sorted(marginals[role].items()))
            block={(0,0,0):F(1)}
            for n in (2,4,8):
                block={(0,0,0):F(1)}
                for _ in range(n//2): block=joint_convolve(block,joint)
                weekends.append({'strategy':'Friday_team_then_mixed','allocation':allocation,'allocation_status':'hypothetical_not_permission',
                    'fee_person_scenario_usd':fee,'team_win_probability':F(1,2),'solo_win_probability':F(1,2),
                    'stopping_policy':'each_member_stops_at_40_including_Friday_award',
                    'dependence':'shared_Friday_team_outcome_then_independent_later_individuals_and_separate_pairs',
                    'group_entry_expenditure_usd':F(n,2)*sum(r['cost'] for r in resources),
                    'per_participant_entry_expenditure_usd':sum(r['cost'] for r in resources)/2,
                    'participant_hours':F(n,2)*sum(r['hours'] for r in resources),
                    'per_participant_occupied_hours':sum(r['hours'] for r in resources)/2,
                    'elapsed_group_wall_hours':expected_max_clock(pair_wall,n//2),
                    'wall_time_status':'Friday_11am_to_last_member_stop_includes_nights_shared_Friday_pair_blocks',**group_metrics(block,n)})
    # Friday opportunity comparison uses same published occupancy and source rows.
    friday_comparison=[]
    for r in read_csv(root/'outputs/tables/phase4_event_economics.csv'):
        if r['event_id'].startswith('friday-') and r['conditional_decisive_win_probability_exact']=='1/2' and r['competitive_draw_rate_exact']=='0' and r['bo1_draw_rate_exact']=='0':
            friday_comparison.append({'event_id':r['event_id'],'award_basis':'verified_individual_award_model',
                'entry_fee_person_usd':F(r['entry_fee_usd']),'expected_tickets_person':F(r['expected_tickets_exact']),
                'p40_person':F(r['p_at_least_40_exact']),'occupied_hours':F(r['elapsed_hours_exact'])+F(1,4),
                'source_row_index':r['source_row_index']})
    for fee in (25,50):
        pmf=allocate_pmf(team_pmf(friday,F(1,2),F(0)),'integer_equal',0)
        friday_comparison.append({'event_id':friday['event_id'],'award_basis':'hypothetical_integer_equal_team_allocation',
            'entry_fee_person_usd':fee,'expected_tickets_person':metrics(pmf)['expected_tickets'],
            'p40_person':metrics(pmf)['p_at_least_40'],'occupied_hours':F(31,4),'source_row_index':friday['source_row_index']})
    plans,_,_,_=make_plans(events,F(1,2),F(0))
    solo_friday=fixed_policy([v for v in plans['casual_focused'] if v.day==0])
    m=terminal_metrics(solo_friday)
    friday_comparison.append({'event_id':'friday_sealed_plus_nexus','award_basis':'two_nonoverlapping_solo_events_conditional_admission',
        'entry_fee_person_usd':m['expected_entry_fee_usd'],'expected_tickets_person':m['expected_tickets'],
        'p40_person':m['p_at_least_40'],'occupied_hours':m['expected_occupied_hours'],
        'source_row_index':[E['friday-radiance-sealed-deck']['source_row_index'],E['friday-super-nexus-night']['source_row_index']]})
    # Controlled ODE examples use common windows, NOT measured historical desk hours.
    old_offers=historical_odes(root)
    ode_rows=[]
    vegas_ode=E['ode-standard-constructed']
    for p in PERFORMANCE:
        for slots in ('published_durations','common_225_minute_slots'):
            for version in ('historical_competitive','vegas_constructed'):
                duration=225 if version=='historical_competitive' or slots=='common_225_minute_slots' else 135
                pmf={0:1-p**3,12:p**3} if version=='historical_competitive' else win_awards(3,{w:w for w in range(4)},p)
                visits=ode_visits(vegas_ode,p=p,queue=15,duration=duration)
                converted=[Visit(v.event_id,v.day,v.start,v.end,10,v.active,v.occupied,tuple(pmf.items())) for v in visits]
                states=fixed_policy(converted)
                ode_rows.append({'version':version,'throughput_basis':slots,'decisive_win_probability':p,
                    'queue_minutes':15,'other_break_minutes':15,'meal_after_second_pod_minutes':30,
                    'pod_slot_minutes':duration,'maximum_pods':len(visits),'maximum_tickets':max(pmf)*len(visits),
                    'elapsed_hour_windows':'Friday/Saturday_11_to_21_30_Sunday_11_to_18_30_conditional_common_reference',
                    'availability':'unverified_historical_desk_hours_and_all_pod_fills',
                    'fee_basis':'nominal_10_dollar_sensitivity_no_historical_currency_conversion',
                    'single_pod_expected_tickets':sum(F(t)*q for t,q in pmf.items()),
                    'single_pod_maximum_tickets':max(pmf),'single_pod_expected_tickets_per_published_hour':sum(F(t)*q for t,q in pmf.items())/F(duration,60),
                    'stopping':'stop_at_40_event_boundary','early_loss_release':'not_used_full_slot_reserved',**terminal_metrics(states),
                    'expected_active_hours':None,'success_conditional_active_hours':None,
                    'active_time_status':'not_estimated_for_cross_format_single_elimination_comparison'})
    claims=[]
    for r in comparisons:
        if r['historical_allocation']=='historical_official' and r['vegas_draw_rate']==0 and r['group_size']>1:
            claims.append({'claim_id':'S'+str(r['group_size']),'numerical_claim':f"For {r['group_size']} people, pooling adds {100*float(r['historical_incremental_success_probability']):.2f} pp historically versus {100*float(r['vegas_incremental_success_probability']):.2f} pp in Vegas",
                'plain_english':'Aggregation helps the Vegas threshold chance more, while its absolute pooled success remains lower',
                'qualification':'N=512, historical without replacement, Vegas independent marginals, equal skill, no draws, unrestricted pooling hypothetical',
                'supporting_table':'phase5_saturday_comparison.csv','supporting_figure':'phase5_pooling_advantage.svg','video_use':'yes_with_qualification'})
    claims.extend([
        {'claim_id':'CAP8','numerical_claim':'Eight-person capacity increment per participant: historical 0.0676 versus Vegas 0.0660',
         'plain_english':'The capacity-efficiency advantage does not uniformly grow after the redesign','qualification':'Ticket units, not actual metals; same benchmark as S8',
         'supporting_table':'phase5_saturday_comparison.csv','supporting_figure':'phase5_units_per_participant.svg','video_use':'yes_counterexample_to_blanket_thesis'},
        {'claim_id':'FRI','numerical_claim':'Friday equal-allocation mean 5.9375 tickets per person; 3.125% personal 40+; 7.75 occupied hours',
         'plain_english':'Friday team play adds an upside path but takes longer than Nexus and blocks it',
         'qualification':'Team p=50%, no draws; allocation and $25/$50 per-person fee interpretations hypothetical',
         'supporting_table':'phase5_friday_comparison.csv','supporting_figure':'phase5_friday_team.svg','video_use':'conditional_example_only'},
        {'claim_id':'ODE','numerical_claim':'Both ODE formats average 1.5 tickets per pod; published-duration rates 0.4 historical versus 0.6667 Vegas tickets per hour',
         'plain_english':'The winner-only offer adds a high-ceiling option; the higher-rate casual format was already available historically',
         'qualification':'Cross-format comparison, not a new Vegas throughput improvement. Equal p despite BO3/BO1 differences; actual desk throughput unknown',
         'supporting_table':'phase5_ode_comparison.csv','supporting_figure':'phase5_competitive_ode.svg','video_use':'yes_with_qualification'},
        {'claim_id':'WEEK','numerical_claim':'Four mixed players: 99.47% aggregate 40+, $540 expected group entry spending, 78 occupied participant-hours',
         'plain_english':'A likely single group threshold is not one metal for each member',
         'qualification':'Phase4 individual stopping, independent itineraries, seats/queues conditional, transfers unresolved',
         'supporting_table':'phase5_weekend_groups.csv','supporting_figure':None,'video_use':'conditional_example_only'},
        {'claim_id':'TITLE','numerical_claim':None,'plain_english':'No entire-weekend historical decline established',
         'qualification':'No historical weekend optimizer or field-composition forecast undertaken',
         'supporting_table':None,'supporting_figure':None,'video_use':'required_limit_on_title'},
    ])
    tables={'video_findings':claims,'team_inventory':inventory,'policy_evidence':policies,'team_economics':team_rows,
            'team_distributions':team_distributions,'team_allocation':allocations,'saturday_groups':saturday,
            'saturday_comparison':comparisons,'weekend_groups':weekends,'partial_pooling':partial,
            'team_weekend_distributions':week_pmfs,'friday_comparison':friday_comparison,
            'historical_ode_offers':old_offers,'ode_comparison':ode_rows}
    announcement_html=Phase5SourceStore(root).read(sources[7]).decode()
    announcement_verification=verify_announcement_content(announcement_html)
    if not announcement_verification['verified_primary_announcement_content'] or 'opening up at noon on Saturday' not in announcement_html:
        raise ValueError('Current primary announcement content needs review')
    review={'sources':sources,'current_schedule_matches_Phase4':True,'rules_date':'2026-10-09',
        'rules_page_review':[1,48],'ticket_pooling_permission':'not_verified',
        'verified_primary_announcement_TFT_ODE_start':'Saturday noon; Phase4 TFT all-weekend scenarios are conditional and should not become itinerary advice',
        'announcement_verification':announcement_verification,
        'PDF_copy_sha256':sha256(root/'data/phase5/tournament_rules.pdf'),
        'extracted_text_sha256':sha256(root/'data/phase5/tournament_rules_extracted.txt')}
    return {f'phase5_{name}.csv':[serial(r) for r in rows] for name,rows in tables.items()},review


def preservation(root):
    manifest=json.loads((root/'data/phase5/preserved_artifacts.json').read_text())
    changed=[p for p,d in manifest['files'].items() if not (root/p).is_file() or sha256(root/p)!=d]
    return {'passed':not changed,'checked_files':len(manifest['files']),'changed_files':changed}


def build(root):
    root=Path(root).resolve();tables,review=analytical_tables(root)
    for name,rows in tables.items(): write_csv(root/'outputs/tables'/name,rows)
    document=root/'docs/PHASE5_GROUP_AND_TEAM_ECONOMICS.md'
    if document.exists():
        text=document.read_text();start='<!-- phase5-summary-start -->';end='<!-- phase5-summary-end -->'
        if start in text and end in text:
            head,tail=text.split(start,1);_,tail=tail.split(end,1)
            document.write_text(head+start+'\n'+report_summary(tables['phase5_saturday_comparison.csv'])+'\n'+end+tail)
    write_json(root/'data/phase5/source_review.json',review)
    write_csv(root/'data/phase5/sources.csv',[serial(r) for r in review['sources']])
    inputs=['data/phase5/source_review.json','data/phase5/sources.csv','data/raw/phase5/retrievals.jsonl','data/phase5/policy_extraction.json',
            'data/phase5/preserved_artifacts.json','data/phase5/tournament_rules_extracted.txt',
            'outputs/tables/phase4_strategy_distributions.csv','outputs/tables/phase4_strategy_results.csv',
            'outputs/tables/phase4_historical_side_inventory.csv','outputs/tables/phase4_event_economics.csv',
            'outputs/tables/phase4_event_inventory.csv','data/phase3a/vegas_rules.json']
    report={'model':'exact_fraction_convolution_hypergeometric_and_shared_team_blocks',
        'table_rows':{k:len(v) for k,v in tables.items()},'input_sha256':{p:sha256(root/p) for p in inputs},
        'code_sha256':{p:sha256(root/p) for p in NEW_CODE if (root/p).exists()},
        'output_sha256':{'outputs/tables/'+p:sha256(root/'outputs/tables'/p) for p in tables}}
    write_json(root/'outputs/tables/phase5_report.json',report)
    return report


def audit(root,write=True):
    root=Path(root).resolve();report=json.loads((root/'outputs/tables/phase5_report.json').read_text())
    hashes={**report['input_sha256'],**report['code_sha256'],**report['output_sha256']}
    mismatch=[p for p,d in hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    tables,review=analytical_tables(root);differences=[]
    for name,rows in tables.items():
        fields=list(dict.fromkeys(k for r in rows for k in r))
        if read_csv(root/'outputs/tables'/name)!=[{k:str(r.get(k,'')) for k in fields} for r in rows]: differences.append(name)
    if json.loads((root/'data/phase5/source_review.json').read_text())!=review: differences.append('source_review')
    document=root/'docs/PHASE5_GROUP_AND_TEAM_ECONOMICS.md'
    if not document.exists() or '<!-- phase5-summary-start -->' not in document.read_text():differences.append('missing_report_summary')
    elif document.read_text().split('<!-- phase5-summary-start -->',1)[1].split('<!-- phase5-summary-end -->',1)[0].strip()!=report_summary(tables['phase5_saturday_comparison.csv']): differences.append('report_summary')
    store=Phase5SourceStore(root)
    for r in [json.loads(s) for s in store.ledger.read_text().splitlines()]:store.read(r)
    extraction=json.loads((root/'data/phase5/policy_extraction.json').read_text())
    mismatch.extend(p for p,d in extraction['derived_and_readable_files_sha256'].items() if not (root/p).is_file() or sha256(root/p)!=d)
    figure=[];path=root/'outputs/figures/phase5_manifest.json'
    if path.exists():
        m=json.loads(path.read_text())
        figure=[p for p,d in {**m['input_sha256'],**m['figure_sha256'],**m['renderer_sha256']}.items() if not (root/p).is_file() or sha256(root/p)!=d]
    else: figure=['missing_manifest']
    protected=preservation(root)
    result={'passed':not mismatch and not differences and not figure and protected['passed'],
        'hash_mismatches':mismatch,'table_differences':differences,'figure_hash_mismatches':figure,
        'preservation':protected,'recalculation':True}
    if write:write_json(root/'outputs/tables/phase5_validation.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('collect','build','audit','figures'))
    parser.add_argument('--root',type=Path,default=Path.cwd());parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    if args.command=='collect':collect(args.root,refresh=args.refresh)
    elif args.command=='build':print(json.dumps(build(args.root)['table_rows'],indent=2))
    elif args.command=='figures':
        from .charts.aggregation import render_figures
        print('\n'.join(render_figures(args.root)))
    else:
        result=audit(args.root);print(json.dumps(result,indent=2))
        if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
