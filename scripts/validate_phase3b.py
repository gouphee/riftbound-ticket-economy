"""Execute all applicable offline checks and preserve previous research bytes."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from riftbound_tickets.phase3a import sha256,write_json
from riftbound_tickets.phase3b import preservation_check


def main():
    output = ROOT/"outputs/phase3b/validation"
    output.mkdir(parents=True,exist_ok=True)
    before = preservation_check(ROOT)
    if not before["passed"]:
        raise SystemExit("Previous research differs before validation: "+repr(before))
    commands = [["-m","unittest","discover","-s","tests","-v"]]
    commands += [["-m","riftbound_tickets.cli",command] for command in ("build","verify","audit","validate-pilot","audit-phase2")]
    commands += [["-m","riftbound_tickets.phase3a","audit"]]
    commands += [["-m","riftbound_tickets.phase3b",command] for command in ("build","audit")]
    report = {"started_at_utc":datetime.now(timezone.utc).isoformat(),"python_version":sys.version,
              "runner_sha256":sha256(Path(__file__)),"preservation_before":before,"commands":[],
              "network":"All commands offline. Existing immutable official captures are reused; no sources refreshed.",
              "artifact_policy":"No old execution reports/logs are rewritten. Existing integration tests preserve archival outputs; only general validation_report.json refreshes its code inventory."}
    env = {**os.environ,"PYTHONPATH":"src"}
    for index,args in enumerate(commands,1):
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True,text=True)
        label = "unittest" if index==1 else args[-2].rsplit(".",1)[-1]+"-"+args[-1]
        path = output/f"{index:02d}-{label}.log"
        path.write_text(result.stdout+result.stderr,encoding="utf-8")
        entry = {"command":"PYTHONPATH=src python3.12 "+" ".join(args),"started_at_utc":started,
                 "finished_at_utc":datetime.now(timezone.utc).isoformat(),"exit_code":result.returncode,
                 "log_path":str(path.relative_to(ROOT)),"log_sha256":sha256(path)}
        report["commands"].append(entry)
        print(entry["command"]+f" -> {result.returncode}",flush=True)
        if result.returncode:
            print(result.stdout[-4000:]+result.stderr[-4000:],flush=True)
            break
    report["preservation_after"] = preservation_check(ROOT)
    report["passed"] = len(report["commands"])==len(commands) and all(c["exit_code"]==0 for c in report["commands"]) and report["preservation_after"]["passed"]
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(ROOT/"outputs/tables/saturday_draw_execution_validation.json",report)
    if not report["passed"]:
        raise SystemExit(1)


if __name__=="__main__":
    main()
