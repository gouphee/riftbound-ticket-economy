"""Focused synthesis of existing exact models; no new weekend optimizer."""
from fractions import Fraction as F
from collections import defaultdict
from .phase3a import read_csv, rules_from_archive
from .models.individual import (solo_distribution,visit,metrics,terminal_metrics,fixed_policy,
    rebound_policy,validate_schedule)
from .phase4 import make_plans


def inventory(root):
    import json
    rows=read_csv(root/'outputs/tables/phase4_event_inventory.csv')
    for r in rows:
        for k in ('start_minute','published_duration_minutes','entry_fee_usd','rounds','round_limit_minutes'):
            r[k]=int(r[k]) if r.get(k) else None
        for k in ('raw_cells','products_separate_from_tickets'):
            if r.get(k):r[k]=json.loads(r[k])
    return rows


def fraction(row,key):
    value=row.get(key+'_exact') or row.get(key)
    return F(value) if value not in ('',None) else None


def source_selector(row,columns):
    return {k:row[k] for k in columns}


def build_tables(root):
    events=inventory(root);E={r['event_id']:r for r in events};_,rules=rules_from_archive(root)
    strategies=read_csv(root/'outputs/tables/phase4_strategy_results.csv')
    itineraries,visits,close,economics=[],[],[],[]
    profiles={'mixed':'equal_skill_threshold','competitive_first':'premier_competitive_priority',
        'casual_focused':'limited_and_smaller_event_enjoyment','sunday_only':'single_day_budget_time'}
    definitions=read_csv(root/'outputs/tables/phase4_strategy_definitions.csv')
    for p in (F(1,2),F(7,10)):
        for strategy,profile in profiles.items():
            r=next(r for r in strategies if r['strategy']==strategy and fraction(r,'conditional_decisive_win_probability')==p
                and fraction(r,'competitive_draw_rate')==0 and r['performance_scope']=='same_hypothetical_p_per_Riftbound_format_TFT_exchangeable')
            ident=strategy+'-p'+str(int(100*p))
            itineraries.append({'itinerary_id':ident,'profile':profile,'strategy':strategy,'hypothetical_p':p,
                'draw_rate':F(0),'p40':fraction(r,'p_at_least_40'),'expected_tickets':fraction(r,'expected_tickets'),
                'modeled_entry_spend_usd':fraction(r,'expected_entry_fee_usd'),
                'occupied_hours':fraction(r,'expected_occupied_hours'),
                'full_booking_fee_exposure_usd':fraction(r,'full_reservation_fee_exposure_usd'),
                'cost_interpretation':'selected_entry_costs_exclude_unused_nonrefundable_advance_bookings_pass_fees_travel',
                'registration_risk':'all_scheduled_events_advance_purchase_capacity_unverified; competitive_fallback_requires_separate_prior_booking',
                'assumptions':'same_hypothetical_p_all_Riftbound_formats; published_durations;15m_queue/checkin;stop_only_after_settlement',
                'important_alternative':'Friday_team_replaces_Nexus_not_an_addition' if strategy=='mixed' else
                    'mixed_menu_if_ticket_threshold_is_more_important_than_premier_play' if strategy=='competitive_first' else
                    'choose_for_format_products_not_probability_from_zero' if strategy=='casual_focused' else 'Rebound_requires_both_days_if_qualified',
                'source_table':'outputs/tables/phase4_strategy_results.csv','source_selector':source_selector(r,('strategy','conditional_decisive_win_probability','competitive_draw_rate','performance_scope'))})
            for v in definitions:
                if v['strategy']==strategy:visits.append({'itinerary_id':ident,**{k:v[k] for k in ('branch','event_id','day','start_including_queue_or_checkin_minute','end_minute','occupied_minutes','entry_fee_usd')}})
    teams=read_csv(root/'outputs/tables/phase5_weekend_groups.csv')
    for fee in (25,50):
        r=next(r for r in teams if r['strategy']=='Friday_team_then_mixed' and r['allocation']=='integer_equal'
            and r['group_size']=='2' and r['fee_person_scenario_usd']==str(fee))
        ident='friday-team-mixed-fee'+str(fee)
        itineraries.append({'itinerary_id':ident,'profile':'Friday_team_consideration','strategy':'Friday_team_then_mixed',
            'hypothetical_p':F(1,2),'team_round_p':F(1,2),'draw_rate':F(0),
            'p40':fraction(r,'random_member_individual_40_probability'),
            'expected_tickets':fraction(r,'expected_total_tickets')/2,
            'modeled_entry_spend_usd':fraction(r,'per_participant_entry_expenditure_usd'),
            'occupied_hours':fraction(r,'per_participant_occupied_hours'),
            'full_booking_fee_exposure_usd':fee+110,
            'cost_interpretation':'hypothetical_equal_integer_allocation_fee25_or50_each; selected_entry_cost_not_all_advance_bookings',
            'registration_risk':'teammate_required;fee_and_ticket_allocation_unverified;Friday_Nexus_conflict',
            'assumptions':'shared_Friday_team_outcome;team_p_not_derived_from_individual_skill;later_independent_personal_paths',
            'important_alternative':'Friday_sealed_plus_Nexus_more_mean_tickets_and_less_time_at_equal_p_but_no40_personal_tail',
            'source_table':'outputs/tables/phase5_weekend_groups.csv','source_selector':source_selector(r,('strategy','allocation','group_size','fee_person_scenario_usd'))})
        visits.append({'itinerary_id':ident,'branch':'unconditional','event_id':'friday-radiance-2v2-team-challenge',
            'day':0,'start_including_queue_or_checkin_minute':645,'end_minute':1110,'occupied_minutes':465,'entry_fee_usd':fee})
        for v in definitions:
            if v['strategy']=='mixed' and v['day']!='0':visits.append({'itinerary_id':ident,**{k:v[k] for k in ('branch','event_id','day','start_including_queue_or_checkin_minute','end_minute','occupied_minutes','entry_fee_usd')}})
    # Reuse the adaptive result as a benchmark, not a guaranteed bookable itinerary.
    for p in (F(1,2),F(7,10)):
        r=next(r for r in strategies if r['strategy']=='ticket_aware_adaptive' and fraction(r,'conditional_decisive_win_probability')==p and fraction(r,'competitive_draw_rate')==0)
        itineraries.append({'itinerary_id':'adaptive-benchmark-p'+str(int(p*100)),
            'profile':'conditional_menu_benchmark_not_fixed_itinerary','strategy':'ticket_aware_adaptive','hypothetical_p':p,
            'draw_rate':F(0),'p40':fraction(r,'p_at_least_40'),'expected_tickets':fraction(r,'expected_tickets'),
            'modeled_entry_spend_usd':fraction(r,'expected_entry_fee_usd'),'occupied_hours':fraction(r,'expected_occupied_hours'),
            'full_booking_fee_exposure_usd':None,'menu_resource_cap_usd':200,
            'registration_risk':'adaptive_action_availability_unverified;not_a_global_optimum;all_branch_booking_cost_unknown',
            'assumptions':'finite_Phase4_menu_only;do_not_use_TFT_all_weekend_scenarios',
            'source_table':'outputs/tables/phase4_strategy_results.csv','source_selector':source_selector(r,('strategy','conditional_decisive_win_probability','competitive_draw_rate','performance_scope'))})
    for r in itineraries:
        r['full_plan_fee_exposure_usd']=r.pop('full_booking_fee_exposure_usd')
        vs=[v for v in visits if v['itinerary_id']==r['itinerary_id']]
        r['scheduled_booking_exposure_usd']=sum(int(v['entry_fee_usd']) for v in vs if not v['event_id'].startswith('ode-')) if vs else None
        r['planned_ODE_budget_usd']=sum(int(v['entry_fee_usd']) for v in vs if v['event_id'].startswith('ode-')) if vs else None
    for v in visits:
        day=int(v['day']);v['date_local']=f'2026-12-{11+day:02d}';v['time_zone']='America/Los_Angeles'
    for p in (F(1,2),F(7,10)):
        for e in events:
            if e['game']!='Riftbound' or e['ticket_status']!='confirmed' or e['award_unit']!='individual':continue
            pmf=solo_distribution(e,p,F(0),F(0),rules)
            if pmf is None:continue
            if e['event_id']=='saturday-standard-rebound-day-1':
                from .models.individual import saturday_stages
                qual=sum(m for (q,t),m in saturday_stages(rules,p,F(0),F(0)).items() if q)
                occupied=F(555+375*qual,60)
            else:occupied=F(e['published_duration_minutes']+15,60)
            if e['day']=='ode':occupied=F(e['published_duration_minutes']+15,60)
            mean=sum(t*m for t,m in pmf.items())
            economics.append({'event_id':e['event_id'],'hypothetical_p':p,'expected_tickets':mean,
                'p40_from_zero':sum(m for t,m in pmf.items() if t>=40),'entry_usd':e['entry_fee_usd'],
                'occupied_hours':occupied,'tickets_per_entry_dollar':mean/e['entry_fee_usd'] if e['entry_fee_usd'] else None,
                'tickets_per_occupied_hour':mean/occupied,'minimum_ticket_award_if_eligible':min(pmf),
                'maximum_ticket_award':max(pmf),'non_ticket_products':e.get('products_separate_from_tickets',{}),
                'product_valuation':'not_valued','schedule_source_row_index':e['source_row_index']})
            for starting in (20,25,30,35,38):
                close.append({'starting_tickets':starting,'gap':40-starting,'event_id':e['event_id'],'hypothetical_p':p,
                    'draw_rate':F(0),'p_reach_40':sum(m for t,m in pmf.items() if t+starting>=40),
                    'entry_usd':e['entry_fee_usd'],'occupied_hours':occupied,
                    'minimum_ticket_award_if_eligible':min(pmf),'maximum_ticket_award':max(pmf),
                    'can_cover_gap':max(pmf)>=40-starting,'guarantees_gap_if_completed_eligible':min(pmf)>=40-starting,
                    'availability':'depends_on_remaining_schedule_advance_booking_or_ODE_pod_availability',
                    'scope':'one_event_awards_only_not_optimized_remaining_day'})
    sensitivities=[]
    for tag,pr,ps,pm in [('equal_50',F(1,2),F(1,2),F(1,2)),('Rebound40_other50',F(2,5),F(1,2),F(1,2)),
        ('Rebound60_other50',F(3,5),F(1,2),F(1,2)),('both_competitive40_small50',F(2,5),F(2,5),F(1,2)),
        ('competitive50_small60',F(1,2),F(1,2),F(3,5))]:
        plans,prefix,_,_=make_plans(events,pm,F(0));_,_,sunday,_=make_plans(events,ps,F(0))
        mixed=[v for v in plans['mixed'] if v.day!=2]+sunday
        for name,states in [('mixed',fixed_policy(mixed)),('competitive_first',rebound_policy(rules,pr,F(0),prefix,sunday))]:
            m=terminal_metrics(states)
            sensitivities.append({'scenario_id':tag,'strategy':name,'p_Rebound':pr,'p_Sunday_Challenge':ps,'p_smaller_events':pm,
                'p40':m['p_at_least_40'],'expected_entry_usd':m['expected_entry_fee_usd'],'occupied_hours':m['expected_occupied_hours'],
                'interpretation':'hypothetical_format_dependent_probabilities_not_inferred_from_composition'})
    thresholds=[]
    # Small monotone threshold search, with an exact rational bracket of width 0.0001.
    for pc in (F(1,2),F(3,5),F(7,10),F(4,5)):
        target=pc**5
        def r40(p):return sum(m for t,m in solo_distribution(E['saturday-standard-rebound-day-1'],p,F(0),F(0),rules).items() if t>=40)
        low,high=0,10000
        while high-low>1:
            mid=(low+high)//2
            if r40(F(mid,10000))>=target:high=mid
            else:low=mid
        thresholds.append({'comparison':'standalone_Rebound_vs_Sunday_Challenge_same50USD_entry_objective_p40',
            'Sunday_Challenge_p':pc,'Sunday_Challenge_p40':target,'Rebound_p_threshold_lower':F(low,10000),
            'Rebound_p_threshold_upper':F(high,10000),'threshold_width':F(1,10000),
            'Rebound_p40_at_lower':r40(F(low,10000)),'Rebound_p40_at_upper':r40(F(high,10000)),
            'time_warning':'Rebound_commits_two_days_if_qualified;Challenge_one_day;not_a_whole_weekend_choice'})
    matrix=[
        ('equal_skill_target40','Use mixed as a fixed-plan reference; adaptive menu is a conditional higher-probability benchmark','mixed-p50','Threshold probability','Do not substitute expected tickets for success; reserve scheduled entries before relying on them'),
        ('stronger_hypothetical_competitor','Compare p=70% sensitivities; choose Rebound for competitive stakes, mixed for tested threshold objective','mixed-p70','Threshold versus premier competition','No measured classification of real players; format probabilities may differ'),
        ('premier_competitive_priority','Friday Nexus, Saturday Rebound; honor Sunday continuation if qualified','competitive_first-p50','Premier competition','Sunday Challenge fallback requires separate advance booking; no refund assumed'),
        ('limited_smaller_events','Sealed, Draft or Champion Trial and Nexus for formats/products; not a ticket-grinding recommendation','casual_focused-p50','Enjoyment and included products','Very low 40-from-zero chance in this reference; value packs separately'),
        ('budget_or_time','Sunday Challenge is the focused one-day $50 reference; short casual events supplement existing tickets','sunday_only-p50','Time/fee constraint','3.125% from zero at p50; a $50 fee does not buy a likely metal'),
        ('Friday_2v2','Consider with teammate and explicit fee/allocation information; replace Friday Nexus','friday-team-mixed-fee25','Team play and personal high tail','Team p is separate; $25/$50 person fee scenarios and equal division remain unverified'),
        ('holding20_or25_or30','Use gap-aware ceiling: one casual pod cannot fill a 10–20 ticket gap; Sunday Challenge can','','Supplement','At p50 Challenge success is18.75%/50%/50% for balances20/25/30; earlier tickets do not make single-pod success possible'),
        ('holding35','Compare Nexus or Sealed for the five-ticket gap; casual pod and Trial ceilings are too low','','Supplement','At p50 Nexus31.25%, Sealed50%; fee/time/product preference matters'),
        ('holding38','A two-ticket gap fits a casual pod; Trial has higher chance, Sealed has a two-ticket published floor','','Cheap versus high-confidence supplement','p50 casual50%, Trial87.5%, Sealed100% conditional completion/eligibility/booking; not a redemption guarantee'),
    ]
    recs=[{'profile':p,'recommendation':r,'reference_itinerary':i,'primary_objective':o,'required_qualification':q,
        'target_audience':'not_competing_in_invitational_RC','no_field_strength_forecast':True} for p,r,i,o,q in matrix]
    return {'itineraries':itineraries,'itinerary_events':visits,'close_to_40':close,'event_objectives':economics,
        'performance_sensitivities':sensitivities,'performance_thresholds':thresholds,'recommendation_matrix':recs}
