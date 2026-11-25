"""Run and record the complete offline suite without rewriting Phase 2 reports."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from riftbound_tickets.phase3a import preserved_artifacts_check, sha256, write_json


def main():
    output = ROOT / "outputs/phase3a/validation"
    output.mkdir(parents=True, exist_ok=True)
    before = preserved_artifacts_check(ROOT)
    if not before["passed"]:
        raise SystemExit("Historical artifacts differ before verification: " + repr(before))
    commands = [["-m", "unittest", "discover", "-s", "tests", "-v"]]
    commands += [["-m", "riftbound_tickets.cli", c] for c in ("build", "verify", "audit", "validate-pilot", "audit-phase2")]
    commands += [["-m", "riftbound_tickets.phase3a", c] for c in ("build", "audit")]
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
              "python_version": sys.version, "runner_sha256": sha256(Path(__file__)),
              "historical_preservation_before": before, "commands": [],
              "phase2_test_isolation": "Existing Phase 2 integration checks rebuild in disposable outputs with read-only input use; original Phase 2 report and validation bytes are never replaced.",
              "network": "All commands offline; official sources already archived in dedicated Phase 3A ledger."}
    env = {**os.environ, "PYTHONPATH": "src"}
    for index, args in enumerate(commands, 1):
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run([sys.executable, *args], cwd=ROOT, env=env, capture_output=True, text=True)
        log = output / f"{index:02d}-{args[-1].replace('-','_')}.log"
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        entry = {"command": "PYTHONPATH=src python3.12 " + " ".join(args), "started_at_utc": started,
                 "finished_at_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode,
                 "log_path": str(log.relative_to(ROOT)), "log_sha256": sha256(log)}
        report["commands"].append(entry)
        print(entry["command"] + f" -> {result.returncode}", flush=True)
        if result.returncode:
            print(result.stdout[-3000:] + result.stderr[-3000:], flush=True)
            break
    report["historical_preservation_after"] = preserved_artifacts_check(ROOT)
    report["passed"] = len(report["commands"]) == len(commands) and all(c["exit_code"] == 0 for c in report["commands"]) and report["historical_preservation_after"]["passed"]
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(ROOT / "outputs/tables/saturday_execution_validation.json", report)
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
