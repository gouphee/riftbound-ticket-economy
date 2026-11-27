"""Final bounded field/recommendation synthesis. Earlier artifacts stay immutable."""
import argparse
import json
from pathlib import Path

from .collectors.phase6_sources import (Phase6SourceStore,metadata,operations,collect_main,RC_UPDATE)
from .collectors.phase4_sources import URLS,schedule_rows
from .collectors.phase5_sources import RULES
from .field_composition import analyze
from .recommendations import build_tables
from .phase3a import read_csv,write_csv,write_json,sha256
from .phase4 import serial

NEW_CODE=('src/riftbound_tickets/collectors/phase6_sources.py','src/riftbound_tickets/field_composition.py',
    'src/riftbound_tickets/recommendations.py','src/riftbound_tickets/phase6_claims.py','src/riftbound_tickets/phase6.py',
    'src/riftbound_tickets/charts/field_composition.py','scripts/validate_phase6.py','tests/test_phase6.py')


def preservation(root):
    manifest=json.loads((root/'data/phase6/preserved_artifacts.json').read_text())
    changed=[p for p,d in manifest['files'].items() if not (root/p).is_file() or sha256(root/p)!=d]
    return {'passed':not changed,'checked_files':len(manifest['files']),'changed_files':changed}


def operations_table(root):
    store=Phase6SourceStore(root);schedule=store.archived(URLS[0])
    fresh=schedule_rows(store.read(schedule).decode());old=read_csv(root/'outputs/tables/phase4_event_inventory.csv')
    if {r['event_id']:r['raw_cells'] for r in fresh}!={r['event_id']:json.loads(r['raw_cells']) for r in old}:
        raise ValueError('Current official schedule changed; recommendations require review')
    prior=json.loads((root/'data/phase5/source_review.json').read_text())
    current_rules=store.archived(RULES)
    # Same source bytes permit reuse of the already visually reviewed policy extraction.
    from .collectors.phase5_sources import Phase5SourceStore
    if current_rules['sha256']!=Phase5SourceStore(root).archived(RULES)['sha256']:
        raise ValueError('Current tournament rules differ; review before policy synthesis')
    items=[
        ('RC_progression','confirmed','Friday6Swiss/12points;Saturday6Swiss/Top8/QF;Sundaysemifinals/final',URLS[3],'availability mechanism;not a side attendance forecast'),
        ('scheduled_registration','confirmed','valid_festival_pass_and_Riot_ID;scheduled_events_purchased_ahead_via_Tixr',URLS[1],'advance does not establish an exact deadline or seats'),
        ('registration_stock','unresolved','current_vendor_page_not_readable',URLS[2],'HTTP403;do not claim sold out or available'),
        ('exact_registration_cutoffs','unresolved','not_documented_in_recovered_official_pages',URLS[1],'no post-elimination purchase or refund assumption'),
        ('Rebound_reserved_seats','confirmed','256_of1024_published_seats_reserved_for_RC_competitors',URLS[0],'reserved capacity is not observed entries or field strength'),
        ('Sunday_conflict','confirmed','Rebound_continuation_and_Challenge_both_start11:00',URLS[0],'qualifying commits Sunday;fallback Challenge needs separate advance booking'),
        ('Friday_team_conflict','confirmed','2v2_11:00_to18:30;Nexus18:30_start',URLS[0],'cannot finish team event and honor Nexus advance checkin/break in modeled schedule'),
        ('Friday_team_fee_allocation','unresolved','team_awards_confirmed;50USD_fee_unit_and_individual_distribution_unconfirmed',URLS[0],'25/50USD_per_person_and_equal_integer_allocations_are_scenarios'),
        ('required_pass','confirmed','Attendee_or_TFT_competitor_or_Riftbound_competitor_pass',URLS[1],'pass price/fees not included in entry-only model'),
        ('ODE_purchase','confirmed','on_demand_purchase_available_throughout_event_as_offered',URLS[1],'pod seats/queue/start guarantees not established'),
        ('ODE_desk_last_launch','unresolved','no_explicit_Riftbound_last_launch_policy_recovered',URLS[0],'programme closing time is not an ODE last-launch rule'),
        ('TFT_ODE_start','confirmed','Saturday_noon_onward', 'https://x.com/RiotSherman/status/2122889583201591569','do not promote preserved Phase4_all_weekend_TFT_scenarios'),
        ('redemption_threshold','confirmed','40_tickets_for_advertised_Plated_Legend_catalog_entries',URLS[0],'inventory and successful redemption unverified'),
        ('badge_limits_transfers','unresolved','no_verified_ticket_specific_cross_attendee_transfer_or_one_metal_badge_rule',URLS[0],'do not represent mathematical pooling as authorized redemption'),
        ('general_prize_sharing','confirmed','current_general_policy_bytes_match_reviewed_Oct9_rules',RULES,'conditional general prize sharing is not unrestricted ticket pooling'),
        ('RC_only_update','confirmed','Nov23_policy_changes_explicitly_exclusive_to_NA_RC',RC_UPDATE,'do not extend RC_only_concession_or_decklist_rules_to_side_events'),
        ('non_ticket_products','confirmed','published_product_quantities_retained_not_valued',URLS[0],'packs/promo/format enjoyment can justify choices outside ticket metric'),
    ]
    rows=[]
    for code,status,value,url,qualification in items:
        s=store.archived(url)
        rows.append({'operational_item':code,'status':status,'finding':value,'necessary_qualification':qualification,
            **{k:s[k] for k in ('source_id','url','retrieved_at','raw_path','http_status')}})
    return rows


def analytical_tables(root):
    raw={**analyze(root),**build_tables(root),'operations':operations_table(root)}
    # Reuse, rather than recompute, the existing independent historical sensitivity.
    raw['group_sampling_sensitivity']=[r for r in read_csv(root/'outputs/tables/phase5_saturday_groups.csv')
        if r['event_model'] in ('historical_official','historical_split')]
    raw['draw_robustness']=[{k:r[k] for k in ('event_id','conditional_decisive_win_probability','competitive_draw_rate',
        'p_at_least_40','p_at_least_40_exact','expected_tickets','expected_tickets_exact','source_id','source_row_index')}
        for r in read_csv(root/'outputs/tables/phase4_event_economics.csv')
        if r['event_id'] in ('saturday-standard-rebound-day-1','sunday-radiance-standard-challenge')
        and r['conditional_decisive_win_probability']=='0.5' and r['competitive_draw_rate'] in ('0.0','0.02')]
    return {f'phase6_{name}.csv':[serial(r) for r in rows] for name,rows in raw.items()}


def build(root):
    root=Path(root).resolve();tables=analytical_tables(root)
    for name,rows in tables.items():write_csv(root/'outputs/tables'/name,rows)
    from .phase6_claims import claim_rows,claims_markdown,handoff_markdown
    claims=claim_rows(root);write_csv(root/'outputs/tables/phase6_claims.csv',[serial(r) for r in claims])
    tables['phase6_claims.csv']=claims
    (root/'docs/VIDEO_CLAIMS.md').write_text(claims_markdown(claims))
    (root/'docs/VIDEO_DATA_HANDOFF.md').write_text(handoff_markdown(root,claims))
    store=Phase6SourceStore(root);sources=list(map(json.loads,store.ledger.read_text().splitlines()))
    for s in sources:store.read(s)
    write_csv(root/'data/phase6/sources.csv',[serial(r) for r in sources])
    inputs=['data/phase6/main_events.json','data/phase6/main_metadata.json.gz','data/phase6/main_collections.json.gz',
        'data/phase6/claim_registry.json','data/phase6/production_inventory.json','data/phase6/preserved_artifacts.json',
        'data/phase6/sources.csv','data/raw/phase6/retrievals.jsonl']
    report={'model':'aggregate_exact_ID_linkage_and_existing_model_synthesis_no_player_ratings',
        'table_rows':{k:len(v) for k,v in tables.items()},'input_sha256':{p:sha256(root/p) for p in inputs},
        'code_sha256':{p:sha256(root/p) for p in NEW_CODE},
        'output_sha256':{'outputs/tables/'+p:sha256(root/'outputs/tables'/p) for p in tables},
        'generated_document_sha256':{p:sha256(root/p) for p in ('docs/VIDEO_CLAIMS.md','docs/VIDEO_DATA_HANDOFF.md')},
        'privacy':'Aggregate only; no names, player identifiers, profiles or individual histories in analytical exports',
        'not_established':['causal_skill_difference','weakest_Vegas_day','whole_weekend_historical_decline','physical_issuance_or_redemption']}
    write_json(root/'outputs/tables/phase6_report.json',report);return report


def audit(root,write=True):
    root=Path(root).resolve();report=json.loads((root/'outputs/tables/phase6_report.json').read_text())
    hashes={**report['input_sha256'],**report['code_sha256'],**report['output_sha256'],**report['generated_document_sha256']}
    mismatch=[p for p,d in hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    tables=analytical_tables(root)
    from .phase6_claims import claim_rows,claims_markdown,handoff_markdown
    claims=claim_rows(root);tables['phase6_claims.csv']=[serial(r) for r in claims]
    differences=[]
    for name,rows in tables.items():
        fields=list(dict.fromkeys(k for r in rows for k in r))
        if read_csv(root/'outputs/tables'/name)!=[{k:str(r.get(k,'')) for k in fields} for r in rows]:differences.append(name)
    if (root/'docs/VIDEO_CLAIMS.md').read_text()!=claims_markdown(claims):differences.append('VIDEO_CLAIMS.md')
    if (root/'docs/VIDEO_DATA_HANDOFF.md').read_text()!=handoff_markdown(root,claims):differences.append('VIDEO_DATA_HANDOFF.md')
    figures=[];path=root/'outputs/figures/phase6_manifest.json'
    if path.exists():
        m=json.loads(path.read_text());figures=[p for p,d in {**m['input_sha256'],**m['figure_sha256'],**m['renderer_sha256']}.items() if not (root/p).is_file() or sha256(root/p)!=d]
    else:figures=['missing_manifest']
    protected=preservation(root)
    result={'passed':not mismatch and not differences and not figures and protected['passed'],
        'hash_mismatches':mismatch,'table_or_document_differences':differences,'figure_mismatches':figures,
        'preservation':protected,'offline_recalculation':True}
    if write:write_json(root/'outputs/tables/phase6_validation.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('collect','build','figures','audit'))
    p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args()
    if a.command=='collect':metadata(a.root);collect_main(a.root);operations(a.root)
    elif a.command=='build':print(json.dumps(build(a.root)['table_rows'],indent=2))
    elif a.command=='figures':
        from .charts.field_composition import render_figures
        print('\n'.join(render_figures(a.root)))
    else:
        result=audit(a.root);print(json.dumps(result,indent=2))
        if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
