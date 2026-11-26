"""Additive conditional-performance research. Only `collect` accesses the network."""
import argparse
import json
import re
from collections import defaultdict
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path

from .collectors.conditional_sources import ConditionalSourceStore, collect, read_checkpoints
from .collectors.locator import read_collection
from .collectors.schedules import TableRows
from .models.conditional_rewards import (PERFORMANCE, DRAWS, bracket_distribution, expected,
    gated_checkpoint, last_round_rewards, strong_record_metrics)
from .payouts.rules import saturday_placement
from .phase3a import read_csv, rules_from_archive, sha256, write_csv, write_json
from .phase4 import serial

NEW_CODE = ('src/riftbound_tickets/collectors/conditional_sources.py',
    'src/riftbound_tickets/models/conditional_rewards.py','src/riftbound_tickets/conditional_rewards.py',
    'src/riftbound_tickets/charts/conditional_rewards.py','scripts/validate_conditional_rewards.py',
    'tests/test_conditional_rewards.py')


def preservation(root):
    manifest=json.loads((root/'data/conditional_rewards/preserved_artifacts.json').read_text())
    changed=[p for p,d in manifest['files'].items() if not (root/p).is_file() or sha256(root/p)!=d]
    return {'passed':not changed,'checked_files':len(manifest['files']),'changed_files':changed}


def pointer(w, prefix):
    return {prefix+k:w[k] for k in ('source_id','source_url','raw_path','retrieved_at','page','row_index')}


def historical_rows(root):
    groups=read_checkpoints(root)
    indexed={(g['event_key'],g['round_number']):g for g in groups}
    old={(r['event_key'],int(r['registration_id'])):r for r in read_csv(root/'outputs/tables/historical_individual_awards.csv')}
    rows=[]
    for key in sorted({g['event_key'] for g in groups}):
        c=read_collection(root,key)
        a,b=indexed[key,6],indexed[key,7]
        if not a['complete'] or not b['complete']: raise ValueError('Missing checkpoint pages')
        # Round-level match_record is historical; nested status/record reflects later results.
        ids=lambda g: {w['row']['user_event_status']['id']:w for w in g['rows']}
        six,seven=ids(a),ids(b)
        if len(six)!=len(a['rows']) or set(six)!=set(seven): raise ValueError('Checkpoint identity mismatch')
        if sorted(w['row']['rank'] for w in seven.values())!=list(range(1,len(seven)+1)):
            raise ValueError('Final Swiss ranks are not a unique sequence')
        cut_groups=[g for g in c['match_sets'] if g['phase_type']!='SWISS' and g['round_number']==8]
        cut_wrappers=[w for g in cut_groups for w in g['rows']]
        all_cut=[w for g in c['match_sets'] if g['phase_type']!='SWISS' for w in g['rows']]
        assigned={p for w in cut_wrappers for p in w['row']['players']}
        if assigned and len(assigned)!=8:raise ValueError('Partial cut pairing coverage needs separate bounds')
        played={p for w in cut_wrappers if w['row']['status']=='COMPLETE' and not w['row'].get('is_ghost_match')
                and not w['row'].get('match_is_bye') for p in w['row']['players']}
        for rid,wrap in six.items():
            r6,r7=wrap['row'],seven[rid]['row'];prior=old[key,rid]
            if r6['player']['id']!=r7['player']['id']:raise ValueError('Player identity changed')
            cut=r7['rank']<=8
            reward_cut=r6['player']['id'] in assigned if assigned else cut
            known=prior['official_resolved_individual_tickets']
            award=int(known) if known!='' else None
            if not reward_cut:
                calculated=saturday_placement(r7['rank'])
                if award is None:award=calculated
            elif award is not None and award not in (144,216,288,432):raise ValueError('Unexpected resolved cut payout')
            lo,hi=(award,award) if award is not None else (144,432)
            wins=sum(w['row']['status']=='COMPLETE' and not w['row'].get('reports_are_in_conflict')
                and w['row']['winning_player']==r6['player']['id'] for w in all_cut)
            if award is None:lo=(144,216,288,432)[wins]
            delta=tuple(y-x for x,y in zip(map(int,r6['match_record'].split('-')),map(int,r7['match_record'].split('-'))))
            transition={(1,0,0):'win_credit',(0,1,0):'loss_credit',(0,0,1):'draw_credit',(0,0,0):'no_recorded_increment'}.get(delta)
            if transition is None:raise ValueError('Checkpoint record failed one-round reconciliation')
            sources=[{**pointer(w,''),'match_id':w['row']['id'],'status':w['row']['status']}
                for w in cut_wrappers if r6['player']['id'] in w['row']['players']]
            rows.append({'event_key':key,'official_event_id':c['spec']['official_event_id'],
                'registration_id':rid,'player_id':r6['player']['id'],'round6_record':r6['match_record'],
                'round6_rank':r6['rank'],'round7_record':r7['match_record'],'round7_rank':r7['rank'],
                'round7_result_credit':transition,'published_top8_cut_eligible':cut,
                'reward_model_cut_slot':reward_cut,
                'reward_model_cut_basis':'archived_QF_pairing' if assigned else 'final_Swiss_standings_implied_only',
                'Swiss_seed_vs_bracket_disagreement':bool(assigned) and cut!=reward_cut,
                'cut_pairing_evidenced':r6['player']['id'] in assigned if assigned else None,
                'completed_cut_match_evidenced':r6['player']['id'] in played if assigned else None,
                'cut_pairing_sources':sources,'cut_observation_status':'archived_QF_pairings' if assigned else 'no_archived_QF_pairings_not_zero_actual_cut',
                'completed_cut_wins_evidenced':wins,
                'cut_result_sources':[{**pointer(w,''),'match_id':w['row']['id']} for w in all_cut if r6['player']['id'] in w['row']['players']],
                'status_at_latest_retrieval':r7['user_event_status']['registration_status'],
                'published_resolved_tickets':award,'published_tickets_lower':lo,'published_tickets_upper':hi,
                'published_payout_status':'resolved_prior_bracket_evidence' if reward_cut and award is not None else
                    'unresolved_cut_placement_bounds' if reward_cut else 'resolved_prior_noncut_or_final_Swiss_placement',
                'hypothetical_top8_equal_tickets':216 if reward_cut else award,
                'physically_issued_tickets':None,'event_specific_split_verified':False,
                'payout_source_id':prior['payout_source_id'],'payout_source_url':prior['payout_source_url'],
                'resolved_award_input':'outputs/tables/historical_individual_awards.csv',
                **pointer(wrap,'round6_'),**pointer(seven[rid],'round7_')})
    return rows


def feasible_cut_assignments(rows):
    """Conserve the 1,728 pool and all known awards/win-derived minimums.

    Bounds allow all remaining placement assignments satisfying these facts;
    they do not claim a completed bracket or an observed sharing agreement.
    """
    by_event=defaultdict(list)
    for r in rows:
        if r['reward_model_cut_slot']:by_event[r['event_key']].append(r)
    support={}
    prizes=sorted(set(permutations((432,288,216,216,144,144,144,144))))
    for event,rs in by_event.items():
        if len(rs)!=8:raise ValueError('Reward cut must contain eight slots')
        valid=[prize for prize in prizes if all(r['published_tickets_lower']<=p<=r['published_tickets_upper'] for r,p in zip(rs,prize))]
        if not valid:raise ValueError('Bracket evidence cannot fit published Top8 pool')
        support[event]=(rs,valid)
    return support


def cohort_published_bounds(rows,support):
    low=high=sum(r['published_resolved_tickets'] for r in rows if not r['reward_model_cut_slot'])
    for event in {r['event_key'] for r in rows}:
        ids={r['registration_id'] for r in rows if r['event_key']==event and r['reward_model_cut_slot']}
        if not ids:continue
        all_rows,assignments=support[event]
        positions=[i for i,r in enumerate(all_rows) if r['registration_id'] in ids]
        sums=[sum(a[i] for i in positions) for a in assignments]
        low+=min(sums);high+=max(sums)
    return F(low,len(rows)),F(high,len(rows))


def cohort_tables(rows):
    support=feasible_cut_assignments(rows)
    grouped=defaultdict(list)
    for r in rows:
        for scope in (r['event_key'],'all_eight_events'):
            for round_ in (6,7):grouped[scope,round_,r[f'round{round_}_record']].append(r)
    cohorts, rewards, transitions=[],[],[]
    for (scope,round_,record),rs in sorted(grouped.items()):
        n=len(rs);cut=sum(r['published_top8_cut_eligible'] for r in rs)
        reward_cut=sum(r['reward_model_cut_slot'] for r in rs)
        known=[r['published_resolved_tickets'] for r in rs if r['published_resolved_tickets'] is not None]
        lower,upper=cohort_published_bounds(rs,support)
        base={'event_key':scope,'checkpoint_round':round_,'record':record,'cohort_entries':n,
            'cut_eligible_entries':cut,'empirical_cut_fraction':F(cut,n),
            'reward_model_cut_slots':reward_cut,'reward_model_cut_fraction':F(reward_cut,n),
            'Swiss_seed_vs_bracket_disagreements':sum(r['Swiss_seed_vs_bracket_disagreement'] for r in rs),
            'cut_fraction_status':'descriptive_standings_implied_not_skill_forecast',
            'match_evidenced_cut_entries':sum(r['completed_cut_match_evidenced'] is True for r in rs),
            'unknown_cut_pairing_observation_entries':sum(r['cut_pairing_evidenced'] is None for r in rs),
            'resolved_payout_entries':len(known),'unresolved_payout_entries':n-len(known),
            'resolved_subset_mean_tickets':F(sum(known),len(known)) if known else None,
            'full_cohort_published_mean_tickets':lower if lower==upper else None,
            'full_cohort_mean_status':'unique_pool_conserving_mean' if lower==upper else 'bounded_unresolved_placement_mean',
            'full_cohort_published_mean_lower':lower,'full_cohort_published_mean_upper':upper,
            'mean_bound_basis':'pool_conserving_placement_assignments_with_known_awards_and_cut_win_minimums_not_split_or_issuance',
            'observed_support_minimum_tickets':min(r['published_tickets_lower'] for r in rs),
            'prospective_checkpoint_guarantee_tickets':None,
            'checkpoint_guarantee_status':'not_inferred_from_finite_observed_cohort',
            'top8_equal_scenario_mean_tickets':F(sum(r['hypothetical_top8_equal_tickets'] for r in rs),n),
            'source_event_keys':sorted({r['event_key'] for r in rs}),
            'source_ids':sorted({r[f'round{round_}_source_id'] for r in rs})}
        cohorts.append(base)
        if round_!=6 or record not in ('5-1-0','6-0-0'):continue
        noncut=sum(r['published_resolved_tickets'] for r in rs if not r['reward_model_cut_slot'])
        for q in PERFORMANCE:
            for arrangement in ('published','top8_equal','top4_equal','top2_equal'):
                rewards.append({'event_key':scope,'checkpoint_round':6,'record':record,
                    'cohort_entries':n,'cut_eligible_entries':cut,'empirical_cut_fraction':F(cut,n),
                    'reward_model_cut_slots':reward_cut,'reward_model_cut_fraction':F(reward_cut,n),
                    'future_bracket_win_probability_q':q,'arrangement':arrangement,
                    'conditional_expected_tickets':F(noncut,n)+F(reward_cut,n)*expected(bracket_distribution(q,arrangement)),
                    'basis':'hybrid_fixed_observed_R6_to_R7_noncut_outcomes_plus_hypothetical_future_bracket',
                    'guaranteed_tickets_at_checkpoint':None,'maximum_possible_if_qualifies':432 if arrangement=='published' else
                        216 if arrangement=='top8_equal' else 288 if arrangement=='top4_equal' else 360})
        outcomes=defaultdict(list)
        for r in rs:outcomes[r['round7_result_credit']].append(r)
        for result,subset in sorted(outcomes.items()):
            transitions.append({'event_key':scope,'round6_record':record,'round7_result_credit':result,
                'entries':len(subset),'cut_eligible_entries':sum(r['published_top8_cut_eligible'] for r in subset),
                'empirical_cut_fraction_given_record_and_result':F(sum(r['published_top8_cut_eligible'] for r in subset),len(subset)),
                'basis':'observed_transition_not_predictive_WDL_tiebreak_model'})
    return cohorts,rewards,transitions


def analytical_tables(root):
    _,rules=rules_from_archive(root)
    store=ConditionalSourceStore(root)
    source=next(json.loads(l) for l in reversed(store.ledger.read_text().splitlines())
        if json.loads(l)['category']=='conditional_current_Vegas_schedule')
    parser=TableRows();parser.feed(store.read(source).decode())
    schedule=next(row for row in parser.rows if len(row)>8 and row[2]=='Standard Rebound Day 1')
    if not all(term in schedule[-1] for term in ('6 Rounds Day 1','5 Rounds Day 2','12 Match Points')):
        raise ValueError('Fresh schedule changed gate/round count')
    parsed=[(int(a),int(b or a),int(t)) for a,b,t in re.findall(r'(\d+)(?:-(\d+))? Match Points\s*:\s*(\d+) Tickets',schedule[5])]
    if sorted(parsed)!=sorted(rules.point_tiers):raise ValueError('Fresh payout table changed')
    probabilities,pmf,vegas,brackets=[],[],[],[]
    for p in PERFORMANCE:
        for d in DRAWS:
            m=strong_record_metrics(p,d,rules)
            for metric in ('vegas_exact_8_2','vegas_at_least_8_wins','vegas_at_least_24_points','vegas_exact_10_0'):
                m[metric+'_given_R6_qualification']=m[metric]/m['vegas_reach_R10']
            for old,new,label in (('historical_exact_5_1','vegas_exact_8_2','exact'),
                ('historical_at_least_5_wins','vegas_at_least_8_wins','wins_tail'),
                ('historical_exact_6_0','vegas_exact_10_0','undefeated')):
                m[label+'_historical_over_vegas_ratio']=m[old]/m[new]
            probabilities.append({'decisive_win_probability_p':p,'draw_probability_d':d,
                'probability_basis':'unconditional_per_entry_iid_WDL_no_byes_no_drops',**m})
            reached,stopped=gated_checkpoint(rules,p,d)
            pmf.append({'p':p,'d':d,'state':'stopped_after_R6','wins':None,'losses':None,'draws':None,'probability':stopped})
            for (w,l,x),mass in sorted(reached.items()):
                pmf.append({'p':p,'d':d,'state':'reached_R10','wins':w,'losses':l,'draws':x,'probability':mass})
            for w,l in ((8,2),(9,1),(10,0)):
                vegas.append({'decisive_win_probability_p':p,'draw_probability_d':d,
                    'entering_round':11,'checkpoint_record':f'{w}-{l}-0','checkpoint_points':3*w,
                    'gate':'at_least_12_points_after_R6_explicitly_applied',
                    'unconditional_checkpoint_probability':reached[w,l,0],
                    **last_round_rewards(w,l,p,d,rules),
                    'physical_issuance':'unverified','forced_final_draw_status':'draw_tickets_is_local_outcome_not_assumed_available_strategy'})
        for arrangement in ('published','top8_equal','top4_equal','top2_equal'):
            dist=bracket_distribution(p,arrangement)
            brackets.append({'future_bracket_win_probability_q':p,'condition':'secured_historical_Top8_slot',
                'arrangement':arrangement,'expected_tickets':expected(dist),
                'guaranteed_tickets_under_arrangement':min(dist),'maximum_possible_tickets':max(dist),
                'ticket_distribution':{str(k):str(v) for k,v in dist.items()},
                'remaining_stage_pool':1728 if arrangement in ('published','top8_equal') else 1152 if arrangement=='top4_equal' else 720,
                'stage_equal_tickets':None if arrangement=='published' else 216 if arrangement=='top8_equal' else 288 if arrangement=='top4_equal' else 360,
                'evidence':'published_placement_schedule' if arrangement=='published' else 'hypothetical_scenario_not_universal_practice'})
    rows=historical_rows(root);cohorts,hybrid,transitions=cohort_tables(rows)
    raw={'record_probabilities':probabilities,'vegas_R10_record_pmf':pmf,'vegas_final_round_rewards':vegas,
        'secured_cut_rewards':brackets,'historical_checkpoint_rows':rows,'historical_record_cohorts':cohorts,
        'historical_hybrid_rewards':hybrid,'historical_R7_transitions':transitions}
    return {f'conditional_{k}.csv':[serial(r) for r in rs] for k,rs in raw.items()}


def build(root):
    root=Path(root).resolve();tables=analytical_tables(root)
    for name,rows in tables.items():write_csv(root/'outputs/tables'/name,rows)
    store=ConditionalSourceStore(root);sources=[json.loads(l) for l in store.ledger.read_text().splitlines()]
    for r in sources:store.read(r)
    write_csv(root/'data/conditional_rewards/sources.csv',[serial(r) for r in sources])
    inputs=['data/conditional_rewards/round_standings.json.gz','data/conditional_rewards/observations.json',
        'data/conditional_rewards/source_review.json','data/conditional_rewards/sources.csv',
        'data/conditional_rewards/preserved_artifacts.json','data/raw/conditional_rewards/retrievals.jsonl',
        'outputs/tables/historical_individual_awards.csv','data/phase3a/vegas_rules.json']
    report={'model':'exact_Fraction_iid_record_probabilities_plus_descriptive_historical_cut_conversion',
        'table_rows':{k:len(v) for k,v in tables.items()},'input_sha256':{p:sha256(root/p) for p in inputs},
        'code_sha256':{p:sha256(root/p) for p in NEW_CODE},
        'output_sha256':{'outputs/tables/'+p:sha256(root/'outputs/tables'/p) for p in tables},
        'historical_checkpoint_rows':len(tables['conditional_historical_checkpoint_rows.csv']),
        'physical_issuance_verified':False}
    write_json(root/'outputs/tables/conditional_report.json',report)
    return report


def audit(root,write=True):
    root=Path(root).resolve();report=json.loads((root/'outputs/tables/conditional_report.json').read_text())
    hashes={**report['input_sha256'],**report['code_sha256'],**report['output_sha256']}
    mismatch=[p for p,d in hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    tables=analytical_tables(root);differences=[]
    for name,rows in tables.items():
        fields=list(dict.fromkeys(k for r in rows for k in r))
        if read_csv(root/'outputs/tables'/name)!=[{k:str(r.get(k,'')) for k in fields} for r in rows]:differences.append(name)
    store=ConditionalSourceStore(root)
    for r in [json.loads(l) for l in store.ledger.read_text().splitlines()]:store.read(r)
    figures=[];path=root/'outputs/figures/conditional_manifest.json'
    if path.exists():
        m=json.loads(path.read_text())
        figures=[p for p,d in {**m['input_sha256'],**m['figure_sha256'],**m['renderer_sha256']}.items() if sha256(root/p)!=d]
    else:figures=['missing_manifest']
    protected=preservation(root)
    result={'passed':not mismatch and not differences and not figures and protected['passed'],
        'hash_mismatches':mismatch,'table_differences':differences,'figure_mismatches':figures,
        'preservation':protected,'offline_recalculation':True}
    if write:write_json(root/'outputs/tables/conditional_validation.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('collect','build','figures','audit'))
    parser.add_argument('--root',type=Path,default=Path.cwd());parser.add_argument('--refresh',action='store_true');a=parser.parse_args()
    if a.command=='collect':collect(a.root,refresh=a.refresh)
    elif a.command=='build':print(json.dumps(build(a.root)['table_rows'],indent=2))
    elif a.command=='figures':
        from .charts.conditional_rewards import render_figures
        print('\n'.join(render_figures(a.root)))
    else:
        result=audit(a.root);print(json.dumps(result,indent=2))
        if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
