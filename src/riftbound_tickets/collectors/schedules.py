"""Extract payout cells from the official historical HTML schedule tables."""

from __future__ import annotations

import re
from html.parser import HTMLParser

from ..payouts.rules import SATURDAY_TIERS


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell = [], None, None
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.ignored += 1
        if tag == "tr":
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = []
        if tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.ignored = max(0, self.ignored - 1)
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None and not self.ignored:
            self.cell.append(data + " ")


def schedule_rule(html: str, event_type: str) -> dict:
    parser = TableRows()
    parser.feed(html)
    names = {"friday": "Pre-Regional Challenge", "saturday": "Super Saturday Standard Challenge", "sunday": "Regional Rebound"}
    matches = [row for row in parser.rows if len(row) >= 6 and any(names[event_type] in cell for cell in row[:3])]
    if len(matches) != 1:
        raise ValueError(f"Expected one {event_type} schedule row, found {len(matches)}")
    row = matches[0]
    payout = row[4]  # Time / name / format / duration / prizes.
    description = row[-1]
    capacity = int(row[7]) if len(row) > 7 and row[7].isdigit() else None
    if event_type == "saturday":
        tiers = re.findall(r"(\d+(?:st|nd|rd|th)(?:\s*[-/]\s*\d+(?:st|nd|rd|th))?)\s*:\s*(\d+)\s*PW Tickets", payout)
        values = [int(value) for _, value in tiers]
        if values != [x[2] for x in SATURDAY_TIERS]:
            raise ValueError(f"Unrecognized Saturday payout table: {payout}")
        return {"kind": "placement", "rounds": 7, "top_cut": 8,
                "tiers": [list(t) for t in SATURDAY_TIERS], "payout_cell": payout, "schedule_row": row, "published_capacity": capacity}
    pairs = re.findall(r"(\d+)\s+Wins?\s*:\s*(\d+)\s*PW Tickets", payout)
    if not pairs:
        raise ValueError(f"No payout amounts in {payout}")
    table = {int(win): int(value) for win, value in pairs}
    round_matches = re.findall(r"(\d+) Rounds\.", description)
    if len(set(round_matches)) != 1:
        raise ValueError("Ambiguous published round limit")
    return {"kind": "wins", "rounds": int(round_matches[0]), "win_tickets": table,
            "payout_cell": payout, "schedule_row": row, "published_capacity": capacity}
