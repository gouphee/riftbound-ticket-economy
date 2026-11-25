"""Isolated read-only source snapshots for the Saturday analytical comparison.

The historical/Phase 2 ledger and index remain byte-identical. This dedicated
ledger uses the same content-addressing, retrieval timestamps, and hash checks.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

from .evidence import EvidenceStore
from .schedules import TableRows

VEGAS_SCHEDULE = "https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/"
ELEVENTH_ROUND_ANNOUNCEMENT = "https://x.com/RiotSherman/status/2122889583201591569"


class _Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = {}
        self.in_heading = False
        self.heading = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.values[attrs.get("property", attrs.get("name"))] = attrs.get("content", "")
        if tag == "h1":
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_heading = False

    def handle_data(self, data):
        if self.in_heading:
            self.heading.append(data)


def verify_announcement_content(html: str) -> dict:
    parser = _Metadata()
    parser.feed(html)
    values = parser.values
    statement = " ".join(parser.heading)
    verified = (values.get("og:url") == ELEVENTH_ROUND_ANNOUNCEMENT
                and values.get("article:author") == "https://x.com/RiotSherman"
                and "Standard Rebound by adding an 11th round" in statement)
    return {"verified_primary_announcement_content": verified,
            "published_time": values.get("article:published_time"),
            "author": values.get("article:author"),
            "verification_basis": "Canonical post URL, author metadata, and explicit Standard Rebound 11th-round statement in captured h1 post text; HTTP 200 alone is insufficient."}


class Phase3ASourceStore(EvidenceStore):
    def __init__(self, root: Path):
        self.root = Path(root)
        self.raw = self.root / "data/raw/phase3a"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.ledger = self.raw / "retrievals.jsonl"

    def archived(self, url: str) -> dict:
        if not self.ledger.exists():
            raise ValueError("Collect Phase 3A official sources first")
        records = [json.loads(line) for line in self.ledger.read_text().splitlines()]
        record = next((r for r in reversed(records) if r["url"] == url and r["http_status"] == 200), None)
        if record is None:
            raise ValueError(f"No successful preserved Phase 3A source: {url}")
        self.read(record)
        return record


def parse_vegas_schedule(html: str) -> dict:
    """Parse official table cells; preserve the obsolete Round 10 sentences."""
    parser = TableRows()
    parser.feed(html)
    day1 = [r for r in parser.rows if "Standard Rebound Day 1" in r]
    day2 = [r for r in parser.rows if "Standard Rebound Day 2" in r]
    if len(day1) != 1 or len(day2) != 1 or len(day1[0]) != 9:
        raise ValueError("Official Standard Rebound schedule row shape changed")
    first, second = day1[0], day2[0]
    tiers = []
    for low, high, tickets in re.findall(r"(\d+)(?:\s*[-–]\s*(\d+))?\s+Match Points\s*:\s*(\d+)\s+Tickets", first[5]):
        tiers.append([int(low), int(high or low), int(tickets)])
    if not tiers or sum(high-low+1 for low, high, _ in tiers) != 15:
        raise ValueError("Expected complete published point tiers from 19 through 33")
    if sorted(p for low, high, _ in tiers for p in range(low, high+1)) != list(range(19,34)):
        raise ValueError("Missing or overlapping Vegas point tiers")
    one = re.search(r"(\d+) Rounds Day 1", first[-1])
    two = re.search(r"(\d+) Rounds Day 2", first[-1])
    two_again = re.search(r"(\d+) Rounds Day 2", second[-1])
    cut = re.search(r"Players at (\d+) Match Points or more will advance to Day 2", first[-1])
    if not all((one, two, two_again, cut)) or two[1] != two_again[1]:
        raise ValueError("Ambiguous official stage structure or advancement cut")
    rounds1, rounds2 = int(one[1]), int(two[1])
    if rounds1 + rounds2 != 11:
        raise ValueError("Official structure does not support the requested updated 11-round model")
    stale = re.findall(r"(?:remaining )?[Pp]rizes are awarded by the end of Round (\d+)", first[-1] + " " + second[-1])
    return {"event_name": "Convergence Fest Las Vegas Standard Rebound", "day1_rounds": rounds1,
            "day2_rounds": rounds2, "total_rounds": rounds1 + rounds2,
            "day2_minimum_match_points": int(cut[1]), "published_capacity": int(first[7]),
            "points_per_win": 3, "points_per_draw": 1, "point_tiers": tiers,
            "payout_cell": first[5], "day1_schedule_row": first, "day2_schedule_row": second,
            "obsolete_award_round_references": [int(r) for r in stale if int(r) != rounds1 + rounds2],
            "round_resolution": "Use explicit 6 Day 1 + 5 Day 2 rounds and 33-point payout ceiling; retain stale Round 10 prose as source discrepancy.",
            "reserved_rc_competitor_seats": 256 if "256 seats will be held for Regional Championship competitors" in first[-1] else None,
            "no_top_cut": "NO Top Cut" in first[3]}


def collect_sources(root: Path, *, refresh: bool = False) -> dict:
    store = Phase3ASourceStore(root)
    source = store.fetch(VEGAS_SCHEDULE, category="phase3a_official_vegas_schedule", refresh=refresh)
    if source["http_status"] != 200:
        raise ValueError("Official Vegas schedule retrieval failed; no assumptions substituted")
    rules = parse_vegas_schedule(store.read(source).decode())
    announcement = store.fetch(ELEVENTH_ROUND_ANNOUNCEMENT, category="phase3a_official_announcement_attempt", refresh=refresh)
    announcement_check = verify_announcement_content(store.read(announcement).decode()) if announcement["http_status"] == 200 else {"verified_primary_announcement_content": False}
    result = {"official_schedule": source, "rules": rules,
              "announcement_retrieval": announcement,
              "announcement_verification": announcement_check,
              "announcement_note": "The official Riot schedule explicitly specifies six plus five rounds. The separate official announcement capture is checked for its actual statement, not merely HTTP status."}
    path = Path(root) / "data/phase3a/vegas_rules.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def archived_rules(root: Path) -> dict:
    store = Phase3ASourceStore(root)
    source = store.archived(VEGAS_SCHEDULE)
    announcement = store.archived(ELEVENTH_ROUND_ANNOUNCEMENT)
    return {"source": source, "announcement_source": announcement,
            "announcement_verification": verify_announcement_content(store.read(announcement).decode()),
            **parse_vegas_schedule(store.read(source).decode())}
