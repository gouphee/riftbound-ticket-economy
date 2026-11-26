"""Isolated Phase 4 official captures and fail-closed schedule extraction."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .evidence import EvidenceStore
from .phase3a_sources import VEGAS_SCHEDULE, parse_vegas_schedule
from .schedules import TableRows

SIGNUP = 'https://teamfighttactics.leagueoflegends.com/en-us/news/community/convergence-fest-side-events-and-the-encore-details/'
REGISTRATION = 'https://www.tixr.com/groups/convergencefest/events/convergence-fest-200990'
RC = 'https://playriftbound.com/en-us/news/organizedplay/north-american-regional-championship-info/'
FESTIVAL = 'https://convergencefest.riotgames.com/en-us/'
TFT_MAIN = 'https://teamfighttactics.leagueoflegends.com/en-us/news/esports/tft-vegas-open-2026-competitor-info/'
URLS = (VEGAS_SCHEDULE, SIGNUP, REGISTRATION, RC, FESTIVAL, TFT_MAIN)


class Phase4SourceStore(EvidenceStore):
    def __init__(self, root: Path):
        self.root = Path(root)
        self.raw = self.root/'data/raw/phase4'
        self.raw.mkdir(parents=True, exist_ok=True)
        self.ledger = self.raw/'retrievals.jsonl'

    def archived(self, url):
        rows = [json.loads(s) for s in self.ledger.read_text().splitlines()]
        row = next(r for r in reversed(rows) if r['url'] == url)
        self.read(row)
        return row


def collect(root: Path, *, refresh=False):
    store = Phase4SourceStore(root)
    for url in URLS:
        row = store.fetch(url, category='phase4_official_schedule_or_context', refresh=refresh)
        print(row['http_status'], row['url'], flush=True)


def schedule_rows(html: str) -> list[dict]:
    parser = TableRows()
    parser.feed(html)
    result, day = [], 'ode'
    for index, row in enumerate(parser.rows):
        if row and row[0] == 'Time':
            day = 'friday'
        if row and row[0] == 'Game':
            day = 'saturday' if day == 'friday' else 'sunday'
        if len(row) == 7 and row[0] != 'Event Name':
            game, time, name, fmt, duration, prizes, fee, cap, desc = ('TFT' if row[0].startswith('TFT') else 'Riftbound', '', *row)
        elif len(row) == 8 and day == 'friday' and row[0] != 'Time':
            game, time, name, fmt, duration, prizes, fee, cap, desc = ('Riftbound', *row)
        elif len(row) == 9 and row[0] != 'Game':
            game, time, name, fmt, duration, prizes, fee, cap, desc = row
        else:
            continue
        slug = re.sub('[^a-z0-9]+', '-', name.lower()).strip('-')
        match = re.fullmatch(r'(\d+)hr:(\d+)m', duration)
        if not match:
            raise ValueError('Unrecognized published duration: '+duration)
        minutes = int(match[1])*60+int(match[2])
        start = None
        if time:
            t = re.fullmatch(r'(\d+):(\d+) (AM|PM)', time)
            if not t:
                raise ValueError('Unrecognized start time: '+time)
            start = (int(t[1]) % 12 + (12 if t[3] == 'PM' else 0))*60+int(t[2])
        rounds = re.findall(r'(\d+) Rounds\.', desc)
        round_count=int(rounds[-1]) if rounds else None
        if name in ('Standard Constructed','Radiance Draft'):
            round_count=3
        elif name in ('Free for All','TFT Normal','TFT Double Up'):
            round_count=1
        elif name=='2v2':
            round_count=2
        elif 'Day 1' in name or 'Day 2' in name:
            stage='1' if 'Day 1' in name else '2'
            count=re.search(r'(\d+) Rounds Day '+stage,desc)
            if count: round_count=int(count[1])
        elif name.startswith('Top Cut #'):
            round_count=4
        limits = re.findall(r'(\d+)m time limit', fmt)
        team = 'per team' in prizes.lower()
        result.append(dict(event_id=day+'-'+slug, day=day, game=game, event_name=name,
                           source_row_index=index, raw_cells=row, format=fmt, description=desc,
                           start_local=time, start_minute=start, published_duration_minutes=minutes,
                           scheduled_end_minute=start+minutes if start is not None else None,
                           entry_fee_text=fee, entry_fee_usd=int(re.search(r'\d+', fee)[0]) if re.search(r'\d+', fee) else None,
                           capacity_text=cap, capacity=int(cap) if cap.isdigit() else None,
                           rounds=round_count,
                           fee_unit='team' if 'per team' in fee else 'individual' if not team or 'enroll individually' in desc else 'unspecified',
                           capacity_unit='teams' if name=='Radiance 2v2 Team Challenge' else 'players_or_pod_seats',
                           round_limit_minutes=int(limits[0]) if limits else None,
                           payout_text=prizes, award_unit='team' if team else 'individual',
                           ticket_status='continuation' if 'continuation' in desc else 'confirmed' if 'Ticket' in prizes else 'not_advertised',
                           registration='onsite_pod_queue' if day=='ode' else 'advance_Tixr_Riot_ID_valid_festival_pass',
                           repeatability='conditional_on_pod_availability_and_desk_hours' if day=='ode' else 'one_scheduled_instance',
                           earliest_realistic_completion=None,
                           evidence_class='official_published_schedule_not_observed_operations'))
    if len({r['event_id'] for r in result}) != len(result) or len(result) < 30:
        raise ValueError('Incomplete or duplicate schedule inventory')
    return result


def sources_and_inventory(root: Path):
    store = Phase4SourceStore(root)
    records = [store.archived(url) for url in URLS]
    source = records[0]
    if source['http_status'] != 200:
        raise ValueError('No successful Phase 4 official schedule')
    html = store.read(source).decode()
    rules = parse_vegas_schedule(html)
    # Phase 3A remains immutable; compare normalized tables, not changing page chrome.
    old = json.loads((root/'data/phase3a/vegas_rules.json').read_text())
    old_html = EvidenceStore(root).read(old['official_schedule']).decode()
    prior_rows = schedule_rows(old_html)
    inventory = schedule_rows(html)
    prior = {r['event_id']:r for r in prior_rows}
    revisions = []
    for row in inventory:
        row.update({k:source[k] for k in ('source_id','url','retrieved_at','sha256','raw_path')})
        was = prior.get(row['event_id'])
        if was is None or was['raw_cells'] != row['raw_cells']:
            revisions.append({'event_id':row['event_id'], 'before':was['raw_cells'] if was else None, 'after':row['raw_cells']})
    for event_id in prior.keys()-{r['event_id'] for r in inventory}:
        revisions.append({'event_id':event_id,'before':prior[event_id]['raw_cells'],'after':None})
    parser=TableRows();parser.feed(html)
    metal_rows=[r for r in parser.rows if len(r)==2 and 'Plated Legend' in r[0]]
    if not metal_rows or any(r[1]!='40 Tickets' for r in metal_rows):
        raise ValueError('Current Plated Legend threshold needs explicit review')
    return records, inventory, {'comparison_basis':'normalized official schedule cells; page hash may change independently',
                                'prior_source':old['official_schedule'], 'current_source':source,
                                'revisions':revisions, 'current_saturday_rules':rules,
                                'redemption_price_review':{'plated_legend_catalog_cells':metal_rows,
                                  'tickets_required':40,'inventory_quantities':None,'transfer_permission':None,
                                  'one_per_badge_policy':'not_established_by_this_capture'}}
