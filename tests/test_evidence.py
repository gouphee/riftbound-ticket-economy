import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path

from riftbound_tickets.collectors.evidence import EvidenceStore


class EvidenceIntegrityTests(unittest.TestCase):
    def test_hash_identifies_original_bytes_even_when_gzipped(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);store=EvidenceStore(root)
            body=b'Original synthetic evidence fixture\n'*100
            p=store.raw/'fixture.gz';p.write_bytes(gzip.compress(body,mtime=0))
            record={'raw_path':str(p.relative_to(root)), 'sha256':hashlib.sha256(body).hexdigest(),'storage_encoding':'gzip'}
            self.assertEqual(store.read(record),body)
            p.write_bytes(gzip.compress(body+b'tampered',mtime=0))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):store.read(record)

    def test_uncompressed_evidence_is_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);store=EvidenceStore(root)
            p=store.raw/'fixture.json';p.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                store.read({'raw_path':str(p.relative_to(root)),'sha256':'incorrect'})
