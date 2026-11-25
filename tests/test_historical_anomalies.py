"""Real-source regressions for misleading completed-round metadata."""

import unittest
import json
from pathlib import Path

from riftbound_tickets.collectors.evidence import EvidenceStore
from riftbound_tickets.collectors.locator import read_collection
from riftbound_tickets.collectors.schedules import schedule_rule
from riftbound_tickets.pipeline import normalize

ROOT=Path(__file__).resolve().parents[1]


class HistoricalAnomalyTests(unittest.TestCase):
    def evaluate(self,key):
        collection=read_collection(ROOT,key)
        store=EvidenceStore(ROOT)
        captures=[json.loads(line) for line in store.ledger.read_text().splitlines()]
        source=next(s for s in reversed(captures) if s['url']==collection['spec']['payout_url'] and s['http_status']==200)
        rule=schedule_rule(store.read(source).decode(),collection['spec']['event_type'])
        return normalize(collection,rule,source)

    def test_empty_vancouver_bracket_is_not_played_top8(self):
        rows,_,_,summary,_=self.evaluate('vancouver-saturday')
        self.assertEqual(summary['unknown_payout_rows'],8)
        self.assertFalse(summary['final_order_resolved'])
        self.assertTrue(all(r['final_placement'] is None for r in rows[:8]))
        self.assertEqual(summary['top8_equal_split_scenario_total'],4992)
        self.assertEqual(summary['official_schedule_pool_for_observed_rank_slots'],4992)

    def test_utrecht_empty_semifinals_and_unresolved_quarters(self):
        rows,_,_,summary,_=self.evaluate('utrecht-saturday')
        self.assertFalse(summary['final_order_resolved'])
        self.assertEqual(summary['unknown_payout_rows'],7)
        self.assertIn('top_cut_matches_without_resolved_outcomes',summary['event_issues'])
        self.assertEqual(rows[7]['published_ticket_entitlement'],144)

    def test_singapore_extra_round_is_flagged(self):
        _,_,_,summary,_=self.evaluate('singapore-friday')
        self.assertIn('published_round_limit_disagrees:6!=5',summary['event_issues'])
        self.assertIsNone(summary['reconstructed_event_tickets'])
