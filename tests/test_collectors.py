"""Synthetic pagination fixtures are tests only, never historical observations."""
import unittest

from riftbound_tickets.collectors.locator import paginate
from riftbound_tickets.collectors.flight import find_event


class FakeStore:
    def __init__(self, pages): self.pages=iter(pages)
    def get_json(self, url, **kwargs):
        data=next(self.pages)
        if isinstance(data,Exception): raise data
        return data, {"source_id":"test-only", "raw_path":"test-only", "retrieved_at":"test-only"}


def page(n, count, ids, next_page):
    return {"count":count,"total":count,"current_page_number":n,"results":[{"id":i} for i in ids],"next":next_page,"next_page_number":next_page}


class PaginationTests(unittest.TestCase):
    def test_follows_next_and_server_count(self):
        r=paginate(FakeStore([page(1,3,[1,2],2),page(2,3,[3],None)]),"https://example.test",category="test_fixture")
        self.assertTrue(r['complete']);self.assertEqual(len(r['rows']),3)

    def test_missing_page_is_not_empty_success(self):
        r=paginate(FakeStore([page(1,3,[1,2],2),ValueError('HTTP 404')]),"https://example.test",category="test_fixture")
        self.assertFalse(r['complete']);self.assertEqual(len(r['rows']),2)

    def test_stops_loop_and_detects_duplicates(self):
        r=paginate(FakeStore([page(1,3,[1,1],1)]),"https://example.test",category="test_fixture")
        self.assertFalse(r['complete']);self.assertIn('missing_or_duplicate_row_ids',r['issues'])

    def test_detects_changed_count_and_wrong_page(self):
        r=paginate(FakeStore([page(1,3,[1,2],2),page(3,4,[3],None)]),"https://example.test",category="test_fixture")
        self.assertFalse(r['complete']);self.assertIn('page_2_total_changed',r['issues'])

    def test_truncated_last_page(self):
        r=paginate(FakeStore([page(1,10,[1,2],None)]),"https://example.test",category="test_fixture")
        self.assertFalse(r['complete'])

    def test_does_not_execute_flight_javascript(self):
        with self.assertRaises(ValueError):find_event('<script>alert(1)</script>',123)
