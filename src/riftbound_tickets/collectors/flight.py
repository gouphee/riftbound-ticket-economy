"""Read JSON data embedded in the public locator's React Flight stream.

No JavaScript execution. Only JSON-bearing records are decoded. This is a
discovery fallback, not a claim that a server-rendered first page is complete.
"""

import json
import re


def flight_values(html: str) -> list:
    chunks = []
    for match in re.finditer(r"self\.__next_f\.push\((.*?)\)</script>", html, re.DOTALL):
        payload = json.loads(match.group(1))
        if len(payload) == 2 and payload[0] == 1 and isinstance(payload[1], str):
            chunks.append(payload[1])
    values = []
    for line in "".join(chunks).splitlines():
        _, separator, value = line.partition(":")
        if not separator:
            continue
        try:
            values.append(json.loads(value))
        except json.JSONDecodeError:
            continue  # Flight module references and length-framed text, not JSON.
    return values


def find_event(html: str, event_id: int) -> dict:
    for value in flight_values(html):
        if isinstance(value, dict) and value.get("id") == event_id and "tournament_phases" in value:
            return value
    raise ValueError(f"No event object for {event_id} in locator HTML")
