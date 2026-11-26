"""Separate, attributable current policy and team-event evidence."""
from pathlib import Path
import json

from .evidence import EvidenceStore
from .phase4_sources import URLS as PRIOR_URLS, schedule_rows
from .phase3a_sources import ELEVENTH_ROUND_ANNOUNCEMENT

HUB='https://playriftbound.com/en-us/rules-hub/'
RULES='https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/861752822d217edf37d9febaeaf77a7d924c1bb6.pdf'
URLS=(*PRIOR_URLS[:5],HUB,RULES,ELEVENTH_ROUND_ANNOUNCEMENT)


class Phase5SourceStore(EvidenceStore):
    def __init__(self,root):
        self.root=Path(root)
        self.raw=self.root/'data/raw/phase5'
        self.raw.mkdir(parents=True,exist_ok=True)
        self.ledger=self.raw/'retrievals.jsonl'

    def archived(self,url):
        rows=[json.loads(s) for s in self.ledger.read_text().splitlines()]
        row=next(r for r in reversed(rows) if r['url']==url)
        self.read(row)
        return row


def collect(root,refresh=False):
    store=Phase5SourceStore(root)
    for url in URLS:
        r=store.fetch(url,category='phase5_official_policy_and_team_schedule',refresh=refresh)
        print(r['http_status'],url,flush=True)


def evidence(root):
    store=Phase5SourceStore(root)
    sources=[store.archived(url) for url in URLS]
    if sources[0]['http_status']!=200: raise ValueError('No current schedule content')
    rows=schedule_rows(store.read(sources[0]).decode())
    for row in rows:
        row.update({k:sources[0][k] for k in ('source_id','url','retrieved_at','raw_path')})
    return sources,rows
