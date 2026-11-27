"""Single production claim index with checked, reusable source-cell selectors."""
import json
from .phase3a import read_csv

STATUSES={'supported','conditional','anecdotal','unresolved','contradicted'}


def claim_rows(root):
    definitions=json.loads((root/'data/phase6/claim_registry.json').read_text());rows=[]
    cache={};seen=set()
    for r in definitions:
        if r['claim_id'] in seen or r['status'] not in STATUSES:raise ValueError('Invalid/duplicate production claim')
        seen.add(r['claim_id']);values=[]
        if r['supporting_figure'] and not (root/r['supporting_figure']).is_file():
            # The new figure can be rendered after the initial build.
            if not r['supporting_figure'].startswith('outputs/figures/phase6_'):raise ValueError('Missing referenced figure')
        for e in r.get('evidence_cells',[]):
            path=e['table']
            if path not in cache:cache[path]=read_csv(root/path)
            selected=[row for row in cache[path] if all(row.get(k)==str(v) for k,v in e['selector'].items())]
            if len(selected)!=1:raise ValueError(f"Claim evidence selector must resolve exactly once: {r['claim_id']} {e}")
            cell={k:selected[0][k] for k in e['columns']}
            values.append({'table':path,'selector':e['selector'],'values':cell})
        for p in r['source_report'].split(';'):
            if not (root/p).is_file():raise ValueError('Missing claim report '+p)
        rows.append({**r,'evidence_values':values,
            'production_instruction':'DO_NOT_ASSERT' if r['status'] in ('unresolved','contradicted') else
                'INCLUDE_QUALIFICATION' if r['status'] in ('conditional','anecdotal') else 'AVAILABLE_WITH_STATED_SCOPE'})
    if {r['video_sequence'] for r in rows}!={f'S{i:02d}' for i in range(1,14)}:raise ValueError('Incomplete sequence coverage')
    return rows


def claims_markdown(rows):
    out=['# Authoritative video claim index','',
        'Research handoff dated 2026-11-26. This is an evidence index, not narration or a replacement script. '
        'The machine-readable authority is [phase6_claims.csv](../outputs/tables/phase6_claims.csv), '
        'including exact evidence cells and selectors. Supported means supported within the written scope; '
        'conditional and anecdotal claims require their qualification. Unresolved/contradicted rows are **not assertions for production**.','',
        'The first eight sequences already have narration in a separate project. Use the correction notes below to check it; no narration was imported, reviewed line by line or replaced here.','']
    for sequence in [f'S{i:02d}' for i in range(1,14)]:
        out += ['## '+sequence,'']
        for r in rows:
            if r['video_sequence']!=sequence:continue
            out += [f"### {r['claim_id']} — {r['status']}",'',r['proposed_statement'],'',
                '**Evidence:** '+r['evidence_class']+'. Reports: '+', '.join(f'[{p.split("/")[-1]}]({p.split("/",1)[-1]})' for p in r['source_report'].split(';'))+'.',
                '**Spoken qualification:** '+r['spoken_qualification'],
                '**On screen:** '+r['on_screen_qualification'],
                '**Assumptions:** '+r['required_assumptions'],
                '**Support:** '+r['supporting_table']+'; '+(r['supporting_figure'] or 'machine-readable cells preferred')+'.',
                '**Official source:** '+r['official_source']+'.',
                '**Production action:** '+r['production_instruction']+'. '+r['correction_or_use_note'],'']
    return '\n'.join(out)


def handoff_markdown(root,claims):
    inventory=json.loads((root/'data/phase6/production_inventory.json').read_text())
    out=['# Video data and evidence handoff','',
        'For the separate Remotion production project. This file specifies data and evidence constraints only. '
        'No script, Remotion implementation or graphics redesign is included. Preserve the existing S01–S13 outline and webcam-overlay presentation.','',
        'Start with [the claim index](VIDEO_CLAIMS.md) and [machine-readable claims](../outputs/tables/phase6_claims.csv). '
        'Use exact rational columns for calculation; round only the display. Claims marked DO_NOT_ASSERT must not enter narration as facts.','',
        '| Sequence | Numerical inputs / exact source columns | Suggested comparison | Display rounding | Must remain visible | Do not assert |',
        '|---|---|---|---|---|---|']
    for r in inventory:
        out.append('| '+' | '.join(str(r[k]).replace('|','/').replace('\n',' ') for k in
            ('sequence','source_inputs','visual_comparison','display_rounding','visible_assumptions','do_not_assert'))+' |')
    out += ['','## Asset inventory','',
        '- Existing Phase 2, 3A, 3B, 4, 5 and conditional-performance PNG/SVG assets remain unchanged. Their figure manifests identify input tables and hashes.',
        '- New distinct finding: [historical composition](../outputs/figures/phase6_field_composition.png) / [SVG](../outputs/figures/phase6_field_composition.svg). Data: `phase6_composition.csv` and `phase6_weekday_summary.csv`.',
        '- Recommendations are supplied as data rather than additional static graphics: `phase6_recommendation_matrix.csv`, `phase6_itineraries.csv`, `phase6_itinerary_events.csv`, `phase6_event_objectives.csv`, `phase6_close_to_40.csv`.',
        '- Robustness: `phase6_performance_sensitivities.csv`, `phase6_performance_thresholds.csv`, `phase6_group_sampling_sensitivity.csv`.',
        '- Operations: `phase6_operations.csv`; raw/source index under `data/phase6/` and `data/raw/phase6/`. Analytical outputs contain no player names, stable player IDs or individual performance histories.','',
        '## Corrections to check in S01–S08','',
        '- S02/S06: historical 5–1 and 6–0 are R6 checkpoints before a seventh Swiss round; Vegas records are R10 checkpoints before Round 11.',
        '- S04/S05: 32 historical funded 40+ slots versus 33.5 expected Vegas full-cap recipients is not 32 versus 33.5 actual metals. Keep matched attendance separate from different full capacities.',
        '- S06: separate exact and cumulative probabilities. At p=80%, the cumulative comparison reverses; no uniform all-skill claim.',
        '- S07: the owner’s 216 receipt is firsthand anecdote, not a universal frequency. Hybrid 57.139/212.108 are model rewards, not receipts. Prize sharing is not a Vegas match draw.',
        '- S08: the casual ODE already existed historically. Equal p50 per-pod means do not establish equal per-hour production or a new casual-event improvement. Competitive ceiling and skill sensitivity differ.','',
        '## Final production gate','',
        'Recheck schedule revisions, registration availability, actual fee/allocation terms and redemption rules before publishing actionable itinerary advice. '
        'There is no verified weakest Vegas day, universal split practice, unrestricted pooling policy, whole-weekend causal decline, physical issuance count or metal-stock guarantee. '
        'The working title is defensible only when the opening and conclusion explicitly scope the demonstrated change to the historical Saturday/premier competitive route and lost competitive ODE opportunity. '
        'This repository did not inspect the separate narration project. No further research phase is started.','']
    return '\n'.join(out)
