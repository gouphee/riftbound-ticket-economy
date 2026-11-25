"""Offline evidence integrity and reviewed Friday/Sunday pilot gate."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.locator import read_collection
from .pipeline import build


def verify_archive(root: Path) -> dict:
    store = EvidenceStore(root)
    sources = [json.loads(x) for x in store.ledger.read_text().splitlines()]
    checked = set()
    for source in sources:
        if source['raw_path'] not in checked:
            store.read(source)
            checked.add(source['raw_path'])
    return {"retrievals":len(sources),"unique_objects_verified":len(checked)}


def validate_pilot(root: Path) -> dict:
    reference = json.loads((root / 'docs/pilot_reference.json').read_text())
    summaries = {s['event_key']:s for s in build(root)}
    reviewed = []
    for key, expected in reference['events'].items():
        actual = summaries[key]
        for field, value in expected.items():
            if field in ('payout_bins','missing_registration_ids'):
                continue
            if actual[field] != value:
                raise ValueError(f"Pilot drift: {key} {field}: {actual[field]!r} != {value!r}")
        for field in ('standings_pagination_complete','roster_pagination_complete','match_pagination_complete','final_order_resolved'):
            if actual[field] is not True:
                raise ValueError(f"Pilot incomplete: {key} {field}")
        rows = list(csv.DictReader((root/'data/processed'/key/'standings.csv').read_text().splitlines()))
        if dict(Counter(r['published_ticket_entitlement'] for r in rows)) != expected['payout_bins']:
            raise ValueError(f"Pilot distribution changed: {key}")
        collection = read_collection(root,key)
        ids = {r['row']['user_event_status']['id'] for r in collection['standings']['rows']}
        missing = sorted({r['row']['id'] for r in collection['roster']['rows']} - ids)
        if missing != expected['missing_registration_ids']:
            raise ValueError(f"Pilot reconciliation changed: {key}")
        reviewed.append(key)
    result = {"validated":True,"scope":"complete_extraction_of_available_rows_and_published_payout_calculation",
              "events":reviewed,"known_gaps":{"atlanta-friday":"1 roster-only registration retained separately; no inferred record or event-wide exact total"},
              "actual_issuance_validated":False,"reference_sha256":hashlib.sha256((root/'docs/pilot_reference.json').read_bytes()).hexdigest(),
              "archive":verify_archive(root)}
    path=root/'data/processed/pilot_validation.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    return result


def audit_outputs(root: Path) -> dict:
    """Reconcile every export to its row-level inputs without network access."""
    def read_csv(path):
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    specs = json.loads((root/'data/events.json').read_text())
    summaries = read_csv(root/'outputs/tables/event_summary.csv')
    if {s['event_key'] for s in summaries} != {s['event_key'] for s in specs} or len(summaries) != len(specs):
        raise ValueError("Output coverage does not match the requested event registry")
    distribution = read_csv(root/'outputs/tables/payout_distribution.csv')
    standings_total, roster_total, relationships_total = 0, 0, 0
    for summary in summaries:
        key = summary['event_key']
        rows = read_csv(root/'data/processed'/key/'standings.csv')
        roster = read_csv(root/'data/processed'/key/'roster.csv')
        matches = read_csv(root/'data/processed'/key/'match_observations.csv')
        if len(rows) != int(summary['standings_rows_extracted']) or len(roster) != int(summary['roster_rows_extracted']):
            raise ValueError(f"CSV row-count mismatch: {key}")
        if summary['standings_pagination_complete'] != 'True' or summary['roster_pagination_complete'] != 'True':
            raise ValueError(f"Incomplete final extraction: {key}")
        if sum(int(r['published_ticket_entitlement']) for r in rows if r['published_ticket_entitlement']) != int(summary['published_entitlement_tickets_known']):
            raise ValueError(f"Ticket subtotal mismatch: {key}")
        if len({r['registration_id'] for r in matches}) != int(summary['participants_with_match_evidence']):
            raise ValueError(f"Match participant mismatch: {key}")
        if summary['verified_tickets_issued'] or summary['verified_tickets_per_entrant'] or any(r['verified_tickets_issued'] for r in rows):
            raise ValueError(f"Unsubstantiated verified issuance: {key}")
        metrics = ['published_ticket_entitlement', 'supported_eligible_tickets']
        if summary['event_type'] == 'saturday':
            metrics.append('top8_equal_split_scenario_tickets')
            if int(summary['top8_equal_split_scenario_total']) != 4992:
                raise ValueError(f"Split failed pool conservation: {key}")
            if sum(r['top8_equal_split_scenario_tickets']=='216' for r in rows[:8]) != 8:
                raise ValueError(f"Split Top 8 distribution mismatch: {key}")
        for metric in metrics:
            expected = Counter(r[metric] for r in rows)
            actual = {d['tickets_per_player']:int(d['player_rows']) for d in distribution if d['event_key']==key and d['basis']==metric}
            if dict(expected) != actual:
                raise ValueError(f"Payout distribution mismatch: {key} {metric}")
        standings_total += len(rows)
        roster_total += len(roster)
        relationships_total += len(matches)
    inputs = [root/'data/events.json', root/'data/raw/retrievals.jsonl', root/'docs/pilot_reference.json',
              *sorted((root/'src').rglob('*.py'))]
    result = {"passed":True,"events":len(summaries),"standings_rows":standings_total,"roster_rows":roster_total,
              "match_player_observations":relationships_total,
              "complete_published_entitlement_reconstructions":sum(bool(s['reconstructed_event_tickets']) for s in summaries),
              "actual_issuance_verified":False,"archive":verify_archive(root),
              "input_sha256":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (root/'outputs/tables/validation_report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
