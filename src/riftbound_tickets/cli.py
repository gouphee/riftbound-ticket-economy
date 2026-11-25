from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.locator import collect_event
from .pipeline import build
from .validation import audit_outputs, validate_pilot, verify_archive


def main():
    parser=argparse.ArgumentParser(description='Reproducible historical Riftbound ticket research')
    parser.add_argument('--root',type=Path,default=Path.cwd())
    sub=parser.add_subparsers(dest='command',required=True)
    collector=sub.add_parser('collect',help='GET public evidence; cache by URL')
    collector.add_argument('--scope',choices=['pilot','all'],default='pilot')
    collector.add_argument('--event',action='append',help='Explicit event_key (repeatable)')
    collector.add_argument('--refresh',action='store_true')
    collector.add_argument('--workers',type=int,choices=[1,2,3],default=1,help='Bounded parallel public GETs across independent events')
    sub.add_parser('build',help='Rebuild CSVs offline from archived collections')
    sub.add_parser('validate-pilot',help='Check archived Friday/Sunday pilot and explicit gap')
    sub.add_parser('verify',help='Verify every raw object against its original SHA-256')
    sub.add_parser('audit',help='Reconcile all CSVs, distributions, and preserved evidence')
    args=parser.parse_args();root=args.root.resolve()
    if args.command=='collect':
        specs=json.loads((root/'data/events.json').read_text())
        requested=set(args.event or [])
        if requested - {s['event_key'] for s in specs}:
            parser.error('Unknown event_key')
        selected=[s for s in specs if s['event_key'] in requested] if requested else [s for s in specs if args.scope=='all' or s.get('pilot')]
        if any(not s.get('pilot') for s in selected):
            # Re-evaluate the gate against the current archived inputs.
            validate_pilot(root)
        store=EvidenceStore(root)
        def collect_one(spec):
            source=store.fetch(spec['payout_url'],category='payout_source',refresh=args.refresh)
            if source['http_status']!=200:
                raise ValueError(f"Payout source unavailable: {spec['event_key']}")
            r=collect_event(root,spec,refresh=args.refresh)
            print(json.dumps({'event_key':spec['event_key'],'standings_rows':len(r['standings']['rows']),
                              'standings_issues':r['standings']['issues'],'roster_rows':len(r['roster']['rows'])}),flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(collect_one,selected))
    elif args.command=='build':
        for row in build(root):
            print(json.dumps({k:row[k] for k in ['event_key','standings_rows_extracted','reconstruction_status','published_entitlement_tickets_known']}))
    elif args.command=='validate-pilot':
        print(json.dumps(validate_pilot(root),indent=2))
    elif args.command=='verify':
        print(json.dumps(verify_archive(root),indent=2))
    elif args.command=='audit':
        print(json.dumps(audit_outputs(root),indent=2))


if __name__=='__main__':main()
