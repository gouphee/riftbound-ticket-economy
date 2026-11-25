import unittest
import hashlib
from pathlib import Path
from unittest.mock import patch

from riftbound_tickets.pipeline import build
from riftbound_tickets.validation import audit_outputs

ROOT=Path(__file__).resolve().parents[1]


class AllEventOutputTests(unittest.TestCase):
    def test_all_24_events_and_distributions_reconcile(self):
        build(ROOT)
        result=audit_outputs(ROOT)
        self.assertTrue(result['passed'])
        self.assertEqual(result['events'],24)
        self.assertEqual(result['standings_rows'],20651)
        self.assertEqual(result['roster_rows'],20652)
        self.assertFalse(result['actual_issuance_verified'])

    def test_offline_rebuild_is_byte_reproducible(self):
        files = [*sorted((ROOT/'outputs/tables').rglob('*.csv')),
                 *sorted((ROOT/'data/processed').rglob('*.csv')),
                 ROOT/'data/processed/payout_rules.json', ROOT/'data/sources.csv',
                 ROOT/'docs/COVERAGE.md', ROOT/'docs/SOURCES.md']
        before = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        with patch('riftbound_tickets.collectors.evidence.urlopen', side_effect=AssertionError('Offline build attempted network access')):
            build(ROOT)
        after = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        self.assertEqual(before,after)
