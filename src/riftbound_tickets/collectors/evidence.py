"""Content-addressed HTTP evidence with an append-only retrieval ledger."""

from __future__ import annotations

import hashlib
import gzip
import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class EvidenceStore:
    _ledger_lock = threading.RLock()
    def __init__(self, root: Path):
        self.root = Path(root)
        self.raw = self.root / "data" / "raw"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.ledger = self.raw / "retrievals.jsonl"

    def fetch(self, url: str, *, category: str, refresh: bool = False) -> dict:
        """Cache by URL; retain response bytes, including HTTP error bodies.

        Only GET requests, no authentication, no registration or player updates.
        Failed requests are recorded but are never treated as empty result sets.
        """
        if not refresh and self.ledger.exists():
            with self._ledger_lock:
                lines = self.ledger.read_text().splitlines()
            for line in reversed(lines):
                record = json.loads(line)
                if record["url"] == url and record["http_status"] == 200:
                    self.read(record)  # A corrupt cache must fail loudly.
                    return record
        body = b""
        status = None
        headers = {}
        error = None
        final_url = url
        for attempt in range(3):
            try:
                request = Request(url, headers={"User-Agent": "riftbound-ticket-research/0.1 (public historical research)", "Accept": "*/*"})
                with urlopen(request, timeout=45) as response:
                    body = response.read()
                    status = response.status
                    headers = dict(response.headers)
                    final_url = response.url
                error = None
                break
            except HTTPError as exc:
                status, body, headers, error = exc.code, exc.read(), dict(exc.headers), str(exc)
                if exc.code not in (429, 500, 502, 503, 504):
                    break
            except (URLError, TimeoutError, OSError) as exc:
                error = f"{type(exc).__name__}: {exc}"
            if attempt < 2:
                time.sleep(1 + attempt)
        digest = hashlib.sha256(body).hexdigest()
        content_type = headers.get("Content-Type", headers.get("content-type", ""))
        suffix = ".json" if "json" in content_type else ".html" if "html" in content_type else ".bin"
        compress = len(body) > 16_384
        path = self.raw / "objects" / (digest + suffix + (".gz" if compress else ""))
        path.parent.mkdir(exist_ok=True)
        if not path.exists():
            path.write_bytes(gzip.compress(body, mtime=0) if compress else body)
        record = {
            "source_id": "sha256:" + digest,
            "url": url,
            "final_url": final_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "http_status": status,
            "content_type": content_type,
            "sha256": digest,
            "raw_path": str(path.relative_to(self.root)),
            "category": category,
            "storage_encoding": "gzip" if compress else "identity",
            "error": error,
            "response_headers": {k: v for k, v in headers.items() if k.lower() in {"content-type", "etag", "last-modified", "date", "content-length"}},
        }
        with self._ledger_lock:
            with self.ledger.open("a") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def read(self, record: dict) -> bytes:
        body = (self.root / record["raw_path"]).read_bytes()
        if record.get("storage_encoding") == "gzip":
            body = gzip.decompress(body)
        if hashlib.sha256(body).hexdigest() != record["sha256"]:
            raise ValueError(f"Evidence hash mismatch: {record['raw_path']}")
        return body

    def get_json(self, url: str, *, category: str, refresh: bool = False) -> tuple[dict, dict]:
        record = self.fetch(url, category=category, refresh=refresh)
        if record["http_status"] != 200:
            raise ValueError(f"HTTP evidence unavailable: {url}: {record['http_status']} {record['error']}")
        return json.loads(self.read(record)), record
