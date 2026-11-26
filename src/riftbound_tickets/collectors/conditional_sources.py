"""Isolated official Swiss-checkpoint standings and limited split evidence."""
import gzip
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .evidence import EvidenceStore
from .locator import API,paginate,read_collection
from .phase3a_sources import VEGAS_SCHEDULE

SPLIT_REPORT='https://www.reddit.com/r/riftboundtcg/comments/1vxb7j8/regionals_in_singapore_solo/'
RELATED_SPLITS=(
    'https://www.magmachamberriftbound.com/tournaments/rq-singapore-2026-09-06',
    'https://www.magmachamberriftbound.com/articles/champions-of-the-rift-2026-08-23',
)


class ConditionalSourceStore(EvidenceStore):
    def __init__(self,root):
        self.root=Path(root)
        self.raw=self.root/'data/raw/conditional_rewards'
        self.raw.mkdir(parents=True,exist_ok=True)
        self.ledger=self.raw/'retrievals.jsonl'


def collect(root,refresh=False):
    root=Path(root);store=ConditionalSourceStore(root)
    jobs=[]
    for path in sorted((root/'data/interim').glob('*-saturday.json.gz')):
        c=read_collection(root,path.name.replace('.json.gz',''))
        swiss=next(p for p in c['metadata']['tournament_phases'] if p['round_type']=='SWISS')
        if swiss['number_of_rounds']!=7:raise ValueError('Review changed historical Swiss count')
        for r in swiss['rounds']:
            if r['round_number'] in (6,7):jobs.append((c['event_key'],r['round_number'],r['id']))
    def fetch(job):
        key,number,rid=job
        result=paginate(store,f'{API}/tournament-rounds/{rid}/standings/paginated/',category='conditional_historical_Swiss_checkpoint',refresh=refresh)
        print(key,number,len(result['rows']),result['complete'],flush=True)
        return {'event_key':key,'round_number':number,'round_id':rid,**result}
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,jobs))
    path=root/'data/conditional_rewards/round_standings.json.gz'
    path.write_bytes(gzip.compress((json.dumps(results,ensure_ascii=False)+'\n').encode(),mtime=0))
    for url,category in ((VEGAS_SCHEDULE,'conditional_current_Vegas_schedule'),(SPLIT_REPORT,'conditional_community_split_attempt')):
        row=store.fetch(url,category=category,refresh=refresh);print(row['http_status'],url,flush=True)
    for url in RELATED_SPLITS:
        row=store.fetch(url,category='conditional_related_format_split_report',refresh=refresh)
        print(row['http_status'],url,flush=True)


def read_checkpoints(root):
    root=Path(root);store=ConditionalSourceStore(root)
    groups=json.loads(gzip.decompress((root/'data/conditional_rewards/round_standings.json.gz').read_bytes()))
    for group in groups:
        replay=[]
        for page in group['pages']:
            source=page['source'];payload=json.loads(store.read(source))
            for i,row in enumerate(payload['results']):
                replay.append({'row':row,'source_id':source['source_id'],'source_url':source['url'],
                    'raw_path':source['raw_path'],'retrieved_at':source['retrieved_at'],'page':page['page'],'row_index':i})
        if replay!=group['rows']:raise ValueError('Checkpoint manifest does not replay from raw')
        if group['complete'] and len(group['rows'])!=group['expected_count']:raise ValueError('Incomplete checkpoint marked complete')
    return groups
