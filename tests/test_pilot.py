import csv
import unittest
from pathlib import Path

from riftbound_tickets.validation import validate_pilot

ROOT=Path(__file__).resolve().parents[1]


class ArchivedPilotTests(unittest.TestCase):
    def test_complete_available_extraction_and_reviewed_payouts(self):
        result=validate_pilot(ROOT)
        self.assertTrue(result['validated'])
        self.assertFalse(result['actual_issuance_validated'])

    def test_no_roster_count_promoted_to_standings(self):
        rows=list(csv.DictReader((ROOT/'data/processed/atlanta-friday/standings.csv').read_text().splitlines()))
        self.assertEqual(len(rows),1019)
        self.assertNotIn('3084340',{r['registration_id'] for r in rows})

    def test_no_claim_ledger_no_verified_issuance(self):
        for key in ['atlanta-friday','atlanta-sunday']:
            rows=list(csv.DictReader((ROOT/'data/processed'/key/'standings.csv').read_text().splitlines()))
            self.assertTrue(all(r['verified_tickets_issued']=='' for r in rows))
