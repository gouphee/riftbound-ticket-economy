"""Bounded public main-event and operational evidence, isolated from older captures."""
import gzip
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .evidence import EvidenceStore
from .locator import API, paginate
from .phase4_sources import URLS as PRIOR_URLS
from .phase5_sources import HUB, RULES
from .phase3a_sources import ELEVENTH_ROUND_ANNOUNCEMENT

RC_UPDATE='https://playriftbound.com/en-us/news/organizedplay/regional-championship-na-rules-update/'


class Phase6SourceStore(EvidenceStore):
    def __init__(self,root):
        self.root=Path(root);self.raw=self.root/'data/raw/phase6'
        self.raw.mkdir(parents=True,exist_ok=True);self.ledger=self.raw/'retrievals.jsonl'

    def archived(self,url):
        row=next(json.loads(l) for l in reversed(self.ledger.read_text().splitlines()) if json.loads(l)['url']==url)
        self.read(row);return row


def metadata(root):
    root=Path(root);store=Phase6SourceStore(root)
    specs=json.loads((root/'data/phase6/main_events.json').read_text())
    def fetch(spec):
        data,source=store.get_json(f"{API}/events/{spec['official_event_id']}/",category='phase6_main_metadata')
        if data['id']!=spec['official_event_id'] or spec['city_key'].replace('-',' ').lower() not in data['name'].lower():
            raise ValueError('Main event identity mismatch')
        print(spec['city_key'],[(p['round_type'],p['number_of_rounds']) for p in data['tournament_phases']],flush=True)
        return {'spec':spec,'metadata':data,'metadata_source':source}
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,specs))
    (root/'data/phase6/main_metadata.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    return rows


def operations(root):
    store=Phase6SourceStore(root)
    for url in (*PRIOR_URLS[:5],HUB,RULES,ELEVENTH_ROUND_ANNOUNCEMENT,RC_UPDATE):
        r=store.fetch(url,category='phase6_current_operations')
        print(r['http_status'],url,flush=True)


def collect_main(root):
    root=Path(root);store=Phase6SourceStore(root)
    entries=json.loads(gzip.decompress((root/'data/phase6/main_metadata.json.gz').read_bytes()))
    def fetch(c):
        event=c['spec']['official_event_id'];phases=sorted(c['metadata']['tournament_phases'],key=lambda p:p['order_in_phases'])
        swiss=[p for p in phases if p['round_type']=='SWISS']
        if len(swiss)!=2:raise ValueError('Review unexpected main-event phase structure')
        c['roster']=paginate(store,f'{API}/events/{event}/registrations/',category='phase6_main_roster')
        c['checkpoints']=[]
        for phase,round_ in ((swiss[0],swiss[0]['rounds'][-1]),(swiss[1],swiss[1]['rounds'][-1])):
            g=paginate(store,f"{API}/tournament-rounds/{round_['id']}/standings/paginated/",category='phase6_main_Swiss_checkpoint')
            c['checkpoints'].append({'phase_id':phase['id'],'round_id':round_['id'],'round_number':round_['round_number'],**g})
        r=swiss[1]['rounds'][0]
        c['first_day2_matches']={'round_id':r['id'],'round_number':r['round_number'],
            **paginate(store,f"{API}/tournament-rounds/{r['id']}/matches/paginated/",category='phase6_main_first_Day2_pairings')}
        print(c['spec']['city_key'],len(c['roster']['rows']),[(g['round_number'],len(g['rows']),g['complete']) for g in c['checkpoints']],len(c['first_day2_matches']['rows']),flush=True)
        return c
    with ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(fetch,entries))
    (root/'data/phase6/main_collections.json.gz').write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0))


def read_main(root):
    root=Path(root);store=Phase6SourceStore(root)
    entries=json.loads(gzip.decompress((root/'data/phase6/main_collections.json.gz').read_bytes()))
    for c in entries:
        if json.loads(store.read(c['metadata_source']))!=c['metadata']:raise ValueError('Main metadata replay mismatch')
        for g in [c['roster'],*c['checkpoints'],c['first_day2_matches']]:
            replay=[]
            for page in g['pages']:
                s=page['source'];payload=json.loads(store.read(s))
                replay.extend({'row':r,'source_id':s['source_id'],'source_url':s['url'],'raw_path':s['raw_path'],
                    'retrieved_at':s['retrieved_at'],'page':page['page'],'row_index':i} for i,r in enumerate(payload['results']))
            if replay!=g['rows']:raise ValueError('Main rows do not replay from official evidence')
            if g['complete'] and len(replay)!=g['expected_count']:raise ValueError('Main pagination count mismatch')
    return entries
