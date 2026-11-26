"""Run required offline checks with isolated logs and preservation verification."""
from __future__ import annotations
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from riftbound_tickets.phase3a import sha256,write_json
from riftbound_tickets.phase4 import preservation


def main():
    output=ROOT/'outputs/phase4/validation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output.mkdir(parents=True,exist_ok=False)
    before=preservation(ROOT)
    if not before['passed']: raise SystemExit('Prior artifacts differ before validation: '+repr(before))
    commands=[['-m','unittest','discover','-s','tests','-v']]
    commands += [['-m','riftbound_tickets.cli',c] for c in ('build','verify','audit','validate-pilot','audit-phase2')]
    commands += [['-m','riftbound_tickets.phase3a','audit'],['-m','riftbound_tickets.phase3b','audit']]
    commands += [['-m','riftbound_tickets.phase4',c] for c in ('build','figures','audit')]
    report={'started_at_utc':datetime.now(timezone.utc).isoformat(),'client_research_date':'2026-11-25',
            'client_timezone':'America/Chicago','python_version':sys.version,'runner_sha256':sha256(Path(__file__)),
            'preservation_before':before,'commands':[],
            'network':'All validation commands offline; isolated official source retrievals recorded separately',
            'prior_report_policy':'Older execution logs/reports unchanged; general validation report may refresh code inventory'}
    for index,args in enumerate(commands,1):
        started=datetime.now(timezone.utc).isoformat()
        executable=str(ROOT/'.venv-figures/bin/python') if args[-1]=='figures' else sys.executable
        result=subprocess.run([executable,*args],cwd=ROOT,env={**os.environ,'PYTHONPATH':'src'},capture_output=True,text=True)
        label='unittest' if index==1 else args[-2].rsplit('.',1)[-1]+'-'+args[-1]
        path=output/f'{index:02d}-{label}.log'
        path.write_text(result.stdout+result.stderr)
        display='.venv-figures/bin/python' if args[-1]=='figures' else 'python3.12'
        report['commands'].append({'command':'PYTHONPATH=src '+display+' '+' '.join(args),'started_at_utc':started,
            'finished_at_utc':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode,
            'log_path':str(path.relative_to(ROOT)),'log_sha256':sha256(path)})
        print(report['commands'][-1]['command']+f' -> {result.returncode}',flush=True)
        if result.returncode:
            print(result.stdout[-3000:]+result.stderr[-3000:],flush=True)
            break
    report['preservation_after']=preservation(ROOT)
    report['passed']=len(report['commands'])==len(commands) and all(c['exit_code']==0 for c in report['commands']) and report['preservation_after']['passed']
    report['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    write_json(ROOT/'outputs/tables/phase4_execution_validation.json',report)
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__':main()
