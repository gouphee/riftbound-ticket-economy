"""Aggregate-only official-identifier linkage. Names never participate in joins."""
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.locator import read_collection
from .collectors.phase6_sources import read_main
from .collectors.conditional_sources import read_checkpoints
from .collectors.schedules import TableRows
from .conditional_rewards import historical_rows, feasible_cut_assignments, cohort_published_bounds
from .draws import classify_match, unique_matches
from .phase3a import read_csv


def valid_uid(value):
    return value if type(value) is int and value>0 else None


def roster_uid(row):
    return valid_uid((row.get('user') or {}).get('id'))


def standings_uid(row):
    a=valid_uid((row.get('player') or {}).get('id'))
    b=valid_uid(((row.get('user_event_status') or {}).get('user') or {}).get('id'))
    return None if a is not None and b is not None and a!=b else a or b


def id_disagrees(row):
    a=valid_uid((row.get('player') or {}).get('id'))
    b=valid_uid(((row.get('user_event_status') or {}).get('user') or {}).get('id'))
    return a is not None and b is not None and a!=b


def unique_index(wrappers,identity):
    buckets=defaultdict(list);missing=0
    for w in wrappers:
        uid=identity(w['row'])
        if uid is None:missing+=1
        else:buckets[uid].append(w)
    collisions={uid for uid,rs in buckets.items() if len(rs)>1}
    return {uid:rs[0] for uid,rs in buckets.items() if uid not in collisions},collisions,missing


def link_group(uid,main_index,collisions,complete):
    if uid is None or uid in collisions:return 'unresolved_identity'
    if uid in main_index:return 'main_registry_linked'
    return 'absent_complete_main_registry' if complete else 'unresolved_main_coverage'


def record(value):
    m=re.fullmatch(r'(\d+)-(\d+)-(\d+)',value or '')
    return tuple(map(int,m.groups())) if m else None


def ratio(a,b):return F(a,b) if b else None


def source_ids(groups):
    return sorted({p['source']['source_id'] for g in groups for p in g['pages']})


def analyze(root):
    root=Path(root);mains=read_main(root)
    checkpoint={(g['event_key'],g['round_number']):g for g in read_checkpoints(root)}
    payouts={(r['event_key'],int(r['registration_id'])):r for r in read_csv(root/'outputs/tables/historical_individual_awards.csv')}
    old_cut=historical_rows(root);cut_support=feasible_cut_assignments(old_cut)
    cut_rows={(r['event_key'],r['registration_id']):r for r in old_cut}
    original=EvidenceStore(root);ledger=list(map(json.loads,original.ledger.read_text().splitlines()))
    feasibility,audit,entry_rows,cross_rows,overlap=[],[],[],[],[]
    performance=defaultdict(list);main_distribution=Counter();side_distribution=Counter();sunday=[]
    for main in mains:
        city=main['spec']['city_key'];roster=main['roster']
        idx,collisions,missing=unique_index(roster['rows'],roster_uid)
        d1,dcoll,dmiss=unique_index(main['checkpoints'][0]['rows'],standings_uid)
        final,fcoll,fmiss=unique_index(main['checkpoints'][1]['rows'],standings_uid)
        roster_index=idx
        conflicts=set()
        for g in main['checkpoints']:
            for w in g['rows']:
                r=w['row'];a=valid_uid((r.get('player') or {}).get('id'))
                b=valid_uid(((r.get('user_event_status') or {}).get('user') or {}).get('id'))
                if a is not None and b is not None and a!=b:conflicts.update((a,b))
        idx={**idx,**d1,**final}
        duplicate_ids=collisions|dcoll|fcoll
        collisions=duplicate_ids|conflicts
        idx={uid:w for uid,w in idx.items() if uid not in collisions}
        if not all(g['complete'] for g in (roster,*main['checkpoints'],main['first_day2_matches'])):
            raise ValueError('Partial main collection: review before aggregate inference')
        day2={p for w in main['first_day2_matches']['rows'] for p in w['row']['players']}
        schedule=next(r for r in ledger if r['url']==f'https://uvsgames.com/rq-{city}-schedule/' and r['http_status']==200)
        parser=TableRows();parser.feed(original.read(schedule).decode())
        mainrow=next(r for r in parser.rows if any('Day 1 Main Event' in v for v in r))
        if '18 or more match points' not in mainrow[-1]:raise ValueError('Historical gate needs review')
        sources=source_ids([roster,*main['checkpoints'],main['first_day2_matches']])
        feasibility.append({'city':city,'main_event_id':main['spec']['official_event_id'],
            'main_roster_entries':len(roster['rows']),'D1_standings_entries':len(main['checkpoints'][0]['rows']),
            'final_Swiss_standings_entries':len(main['checkpoints'][1]['rows']),
            'first_Day2_pairing_participants':len(day2),'D1_rounds':8,'D2_Swiss_rounds':5,'D2_gate_points':18,
            'main_start_datetime':main['metadata']['start_datetime'],'main_day2_start_datetime':main['metadata']['day_2_start_datetime'],
            'metadata_source_id':main['metadata_source']['source_id'],'main_official_url':main['spec']['discovery_url'],
            'schedule_source_id':schedule['source_id'],'schedule_url':schedule['url'],'data_source_ids':sources,
            'complete_roster_and_checkpoint_pages':True,'performance_scope':'Swiss_records_not_elimination_placements'})
        audit.append({'scope':city+'-main','rows':len(roster['rows']),'unique_stable_ids':len(roster_index),
            'registry_unique_usable_ids':len(idx),'missing_stable_id_rows':missing,'colliding_stable_ids':len(duplicate_ids),
            'conflicting_identifier_values':len(conflicts),
            'roster_status_counts':dict(Counter(w['row']['registration_status'] for w in roster['rows'])),
            'D1_unusable_id_rows':dmiss,'D1_conflicting_id_rows':sum(id_disagrees(w['row']) for w in main['checkpoints'][0]['rows']),
            'D1_collisions':len(dcoll),'final_unusable_id_rows':fmiss,'final_collisions':len(fcoll),
            'roster_ids_without_D1_row':len(set(roster_index)-set(d1)),
            'D1_ids_absent_roster':len(set(d1)-set(roster_index)),
            'join_method':'exact_positive_integer_user_id_only_no_names',
            'source_ids':sources})
        side_uids={}
        for weekday in ('friday','saturday','sunday'):
            key=city+'-'+weekday;c=read_collection(root,key)
            standing=checkpoint[key,7] if weekday=='saturday' else c['standings']
            side_idx,side_coll,side_missing=unique_index(standing['rows'],standings_uid)
            ambiguous_side_ids=side_coll|{w['row']['player']['id'] for w in standing['rows'] if standings_uid(w['row']) is None}
            side_uids[weekday]=set(side_idx)
            audit.append({'scope':key,'rows':len(standing['rows']),'unique_stable_ids':len(side_idx),
                'missing_stable_id_rows':sum(standings_uid(w['row']) is None and not id_disagrees(w['row']) for w in standing['rows']),
                'conflicting_id_rows':sum(id_disagrees(w['row']) for w in standing['rows']),
                'unusable_stable_id_rows':side_missing,'colliding_stable_ids':len(side_coll),
                'join_method':'exact_positive_integer_user_id_only_no_names','source_ids':source_ids([standing])})
            match_members=set();excluded=Counter();cross=Counter();cross_sources=set()
            for entry in unique_matches(c):
                if entry['phase_type']!='SWISS':continue
                m=entry['match'];players=m.get('players') or []
                match_members.update(players)
                classified=classify_match(m,duplicate_conflict=entry['duplicate_conflict'])
                if not classified['included_in_draw_denominator']:
                    excluded[classified['exclusion_reason']]+=1;continue
                labels=['unresolved_identity' if p in ambiguous_side_ids else link_group(valid_uid(p),idx,collisions,roster['complete']) for p in players]
                if set(labels)!={'main_registry_linked','absent_complete_main_registry'}:continue
                main_player=players[labels.index('main_registry_linked')]
                cross['matches']+=1
                if classified['explicit_draw']:cross['draws']+=1
                elif m['winning_player']==main_player:cross['main_wins']+=1
                else:cross['not_listed_wins']+=1
                cross_sources.update(s['source_id'] for s in entry['sources'])
            cross_rows.append({'event_key':key,'weekday':weekday,**{k:cross[k] for k in ('matches','main_wins','not_listed_wins','draws')},
                'main_decisive_win_fraction':ratio(cross['main_wins'],cross['main_wins']+cross['not_listed_wins']),
                'exclusions_all_Swiss_matches':dict(excluded),'source_ids':sorted(cross_sources),
                'interpretation':'within_event_descriptive_cross_group_matches_not_skill_or_causal_effect'})
            for w in standing['rows']:
                raw=w['row'];uid=standings_uid(raw)
                group='unresolved_identity' if uid in side_coll else link_group(uid,idx,collisions,roster['complete'])
                reg=raw['user_event_status']['id'];award=payouts[key,reg]
                sr=record(raw.get('match_record'));mr=record(d1[uid]['row']['match_record']) if uid in d1 else None
                finalrow=final.get(uid);finalrank=finalrow['row']['rank'] if finalrow else None
                # Qualification is published-rule entitlement, distinct from observed Day2 pairings.
                qualified=(3*mr[0]+mr[2]>=18) if mr is not None else None
                status='not_main_registry' if group=='absent_complete_main_registry' else 'qualification_unknown'
                if group=='main_registry_linked' and qualified is not None:status='qualified_by_R8_points' if qualified else 'below_R8_gate'
                tick=award['primary_ticket_award'] if weekday!='saturday' else award['official_resolved_individual_tickets']
                row={'event_key':key,'city':city,'weekday':weekday,'group':group,'uid':uid,'registration_id':reg,
                    'side_record':sr,'main_D1_record':mr,'main_final_Swiss_rank':finalrank,
                    'match_evidenced':uid in match_members if uid is not None else None,
                    'main_standings_positive_credit':bool(mr and sum(mr)>0) if group=='main_registry_linked' else None,
                    'main_Day2_pairing_evidenced':uid in day2 if group=='main_registry_linked' else None,
                    'main_qualification_status':status,'ticket_award':int(tick) if tick!='' else None,
                    'source_id':w['source_id'],'main_source_ids':sources,'payout_source_id':award['payout_source_id']}
                entry_rows.append(row);performance[key,weekday,group].append(row)
                side_distribution[key,weekday,group,'win_credits',str(sr[0]) if sr is not None else 'unknown']+=1
                if mr is not None and group=='main_registry_linked':
                    points=3*mr[0]+mr[2]
                    bin_='18+' if points>=18 else '15–17' if points>=15 else '9–14' if points>=9 else '0–8'
                    main_distribution[key,weekday,'D1_match_point_band',bin_]+=1
                if finalrank is not None and group=='main_registry_linked':
                    bin_='1–64' if finalrank<=64 else '65–256' if finalrank<=256 else '257+'
                    main_distribution[key,weekday,'final_Swiss_rank_band',bin_]+=1
            if weekday=='sunday':
                subset=[r for r in entry_rows if r['event_key']==key and r['group']=='main_registry_linked']
                counts=Counter(r['main_qualification_status'] for r in subset)
                sunday.append({'event_key':key,'main_linked_entries':len(subset),
                    'qualified_by_R8_points':counts['qualified_by_R8_points'],'below_R8_gate':counts['below_R8_gate'],
                    'qualification_unknown':counts['qualification_unknown'],
                    'Day2_pairing_evidenced':sum(r['main_Day2_pairing_evidenced'] for r in subset),
                    'qualified_but_no_R9_pairing_evidence':sum(r['main_qualification_status']=='qualified_by_R8_points' and not r['main_Day2_pairing_evidenced'] for r in subset),
                    'source_ids':sources})
        for a,b in (('friday','saturday'),('friday','sunday'),('saturday','sunday')):
            common=side_uids[a]&side_uids[b]
            overlap.append({'city':city,'weekday_a':a,'weekday_b':b,'both_side_events_stable_ids':len(common),
                'both_and_main_registry_linked':sum(uid in idx for uid in common),
                'basis':'unique_same_city_exact_ids_not_unique_attendance_across_cities'})
    composition=[]
    for key,weekday,group in sorted(performance):
        rs=performance[key,weekday,group];valid=[r for r in rs if r['side_record'] is not None]
        wins=sum(r['side_record'][0] for r in valid);losses=sum(r['side_record'][1] for r in valid);draws=sum(r['side_record'][2] for r in valid)
        awards=[r['ticket_award'] for r in rs if r['ticket_award'] is not None]
        low=high=None
        if weekday=='saturday':low,high=cohort_published_bounds([cut_rows[key,r['registration_id']] for r in rs],cut_support)
        elif len(awards)==len(rs):low=high=F(sum(awards),len(rs))
        composition.append({'event_key':key,'weekday':weekday,'identity_group':group,'standings_entries':len(rs),
            'fraction_of_side_standings':F(len(rs),sum(len(v) for (k,d,g),v in performance.items() if k==key)),
            'match_evidenced_entries':sum(r['match_evidenced'] is True for r in rs),
            'main_standings_positive_credit_entries':sum(r['main_standings_positive_credit'] is True for r in rs),
            'valid_side_record_entries':len(valid),'missing_side_record_entries':len(rs)-len(valid),
            'record_win_credits':wins,'record_loss_credits':losses,'record_draw_credits':draws,
            'decisive_record_credit_win_fraction':ratio(wins,wins+losses),
            'record_scope':'final_Swiss_R7' if weekday=='saturday' else 'final_published_record',
            'known_ticket_award_entries':len(awards),'unknown_ticket_award_entries':len(rs)-len(awards),
            'known_ticket_award_sum':sum(awards),'published_mean_lower':low,'published_mean_upper':high,
            'ticket_basis':'published_placement_pool_bounds' if weekday=='saturday' else 'primary_qualifying_record_entitlement_includes_DROPPED',
            'source_ids':sorted({r['source_id'] for r in rs}),
            'main_source_ids':sorted({s for r in rs for s in r['main_source_ids']}),
            'payout_source_ids':sorted({r['payout_source_id'] for r in rs}),
            'physical_issuance':None,'names_or_player_ids_exported':False})
    dist=[{'event_key':k,'weekday':d,'metric':m,'value':v,'entries':n} for (k,d,m,v),n in sorted(main_distribution.items())]
    summary=[]
    for day in ('friday','saturday','sunday'):
        rs=[r for r in composition if r['weekday']==day];n=sum(r['standings_entries'] for r in rs)
        counts={group:sum(r['standings_entries'] for r in rs if r['identity_group']==group)
            for group in ('main_registry_linked','absent_complete_main_registry','unresolved_identity')}
        cr=[r for r in cross_rows if r['weekday']==day];wins=sum(r['main_wins'] for r in cr);loss=sum(r['not_listed_wins'] for r in cr)
        summary.append({'weekday':day,'standings_entries':n,**counts,
            'main_registry_fraction':F(counts['main_registry_linked'],n),
            'unresolved_identity_fraction':F(counts['unresolved_identity'],n),
            'main_positive_record_credit_entries':sum(r['main_standings_positive_credit_entries'] for r in rs),
            'cross_group_main_wins':wins,'cross_group_not_listed_wins':loss,
            'cross_group_draws':sum(r['draws'] for r in cr),'cross_group_main_decisive_win_fraction':ratio(wins,wins+loss),
            'cross_group_event_min_win_fraction':min(r['main_decisive_win_fraction'] for r in cr if r['main_decisive_win_fraction'] is not None),
            'cross_group_event_max_win_fraction':max(r['main_decisive_win_fraction'] for r in cr if r['main_decisive_win_fraction'] is not None),
            'source_event_keys':sorted({r['event_key'] for r in rs}),'weighting':'entry_or_match_weighted_not_unique_people_across_cities',
            'performance_interpretation':'selected_within_event_association_not_field_skill_or_Vegas_p_forecast'})
    return {'main_feasibility':feasibility,'identity_audit':audit,'composition':composition,
        'cross_group_matches':cross_rows,'main_performance_distribution':dist,'sunday_qualification':sunday,
        'side_overlap':overlap,'weekday_summary':summary,
        'side_performance_distribution':[{'event_key':k,'weekday':d,'identity_group':g,'metric':m,'value':v,'entries':n,
            'interpretation':'credited_record_wins_include_byes_administrative_credits_not_a_skill_rating'}
            for (k,d,g,m,v),n in sorted(side_distribution.items())]}

