"""Public locator API collector with explicit pagination and completeness checks."""

from __future__ import annotations

import json
import gzip
from pathlib import Path
from urllib.parse import urlencode

from .evidence import EvidenceStore

API = "https://api.cloudflare.riftbound.uvsgames.com/hydraproxy/api/v2"
LOCATOR = "https://locator.riftbound.uvsgames.com/events"


def paginate(store, endpoint: str, *, category: str, page_size: int = 500, refresh: bool = False) -> dict:
    """Follow server next-page metadata, not a computed number of roster pages.

    Preserve partial results on failure. Callers must inspect `issues`; a failed
    page is never converted into a successful, empty page.
    """
    rows, pages, issues = [], [], []
    expected, page, visited = None, 1, set()
    while page is not None:
        if type(page) is not int or page < 1 or page in visited:
            issues.append("invalid_or_repeated_next_page")
            break
        visited.add(page)
        url = endpoint + "?" + urlencode({"page": page, "page_size": page_size})
        try:
            data, source = store.get_json(url, category=category, refresh=refresh)
        except (ValueError, json.JSONDecodeError) as exc:
            issues.append(f"page_{page}_unavailable:{exc}")
            break
        pages.append({"page": page, "source": source})
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            issues.append(f"page_{page}_unexpected_shape")
            break
        count = data.get("count")
        if type(count) is not int or count < 0 or data.get("total", count) != count:
            issues.append(f"page_{page}_invalid_total")
            break
        if expected is None:
            expected = count
        if expected != count:
            issues.append(f"page_{page}_total_changed")
        if data.get("current_page_number") != page:
            issues.append(f"page_{page}_number_mismatch")
        for index, row in enumerate(data["results"]):
            rows.append({"row": row, "source_id": source["source_id"], "source_url": url,
                         "raw_path": source["raw_path"], "retrieved_at": source["retrieved_at"],
                         "page": page, "row_index": index})
        if "next_page_number" not in data or "next" not in data:
            issues.append(f"page_{page}_missing_pagination_metadata")
            break
        if data["next"] != data["next_page_number"]:
            issues.append(f"page_{page}_next_disagrees")
        if not data["results"] and data["next"] is not None:
            issues.append(f"page_{page}_empty_nonterminal_page")
            break
        page = data["next_page_number"]
    if expected is not None and len(rows) != expected:
        issues.append(f"row_count_mismatch:{len(rows)}!={expected}")
    ids = [row["row"].get("id") for row in rows]
    if None in ids or len(ids) != len(set(ids)):
        issues.append("missing_or_duplicate_row_ids")
    return {"expected_count": expected, "rows": rows, "pages": pages,
            "issues": issues, "complete": not issues}


def collect_event(root: Path, spec: dict, *, refresh: bool = False, matches: bool = True) -> dict:
    store = EvidenceStore(root)
    event_id, key = spec["official_event_id"], spec["event_key"]
    metadata, metadata_source = store.get_json(f"{API}/events/{event_id}/", category="event_metadata", refresh=refresh)
    if metadata.get("id") != event_id:
        raise ValueError("Event identity mismatch")
    expected_name = {"friday": "Pre-Regional Challenge", "saturday": "Super Saturday", "sunday": "Regional Rebound"}[spec["event_type"]]
    if spec["city"] not in metadata["name"] or expected_name not in metadata["name"]:
        raise ValueError(f"Event name does not match registry: {metadata['name']}")
    page_source = store.fetch(f"{LOCATOR}/{event_id}", category="event_page", refresh=refresh)
    roster = paginate(store, f"{API}/events/{event_id}/registrations/", category="roster_with_recorded_results", refresh=refresh)
    phases = sorted(metadata["tournament_phases"], key=lambda x: x["order_in_phases"])
    completed = [(p, r) for p in phases for r in p["rounds"] if r["status"] == "COMPLETE"]
    final = completed[-1] if completed else None
    standings = paginate(store, f"{API}/tournament-rounds/{final[1]['id']}/standings/paginated/", category="latest_completed_round_standings", refresh=refresh) if final else {
        "expected_count": None, "rows": [], "pages": [], "issues": ["no_completed_round"], "complete": False}
    match_sets = []
    if matches:
        for phase, round_ in completed:
            result = paginate(store, f"{API}/tournament-rounds/{round_['id']}/matches/paginated/", category="round_matches", refresh=refresh)
            match_sets.append({"phase_id": phase["id"], "phase_type": phase["round_type"],
                               "round_id": round_["id"], "round_number": round_["round_number"], **result})
    result = {"event_key": key, "spec": spec, "metadata": metadata, "metadata_source": metadata_source,
              "event_page_source": page_source, "roster": roster, "standings": standings,
              "selected_phase_id": final[0]["id"] if final else None,
              "selected_round_id": final[1]["id"] if final else None,
              "selected_round_number": final[1]["round_number"] if final else None,
              "match_sets": match_sets}
    output = root / "data" / "interim" / (key + ".json.gz")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress((json.dumps(result, ensure_ascii=False) + "\n").encode(), mtime=0))
    return result


def read_collection(root: Path, key: str) -> dict:
    path = root / "data" / "interim" / (key + ".json.gz")
    if path.exists():
        collection = json.loads(gzip.decompress(path.read_bytes()))
    else:
        collection = json.loads((root / "data" / "interim" / (key + ".json")).read_text())
    store = EvidenceStore(root)
    metadata = json.loads(store.read(collection["metadata_source"]))
    if metadata != collection["metadata"]:
        raise ValueError(f"Interim metadata disagrees with raw evidence: {key}")
    # Raw snapshots own the data. Interim row copies must exactly replay from
    # archived response pages, including source pointers and row order.
    for group in [collection["roster"], collection["standings"], *collection["match_sets"]]:
        replayed = []
        for page in group["pages"]:
            source = page["source"]
            payload = json.loads(store.read(source))
            for index, row in enumerate(payload["results"]):
                replayed.append({"row": row, "source_id": source["source_id"], "source_url": source["url"],
                                 "raw_path": source["raw_path"], "retrieved_at": source["retrieved_at"],
                                 "page": page["page"], "row_index": index})
        if replayed != group["rows"]:
            raise ValueError(f"Interim rows disagree with raw evidence: {key}")
    return collection
