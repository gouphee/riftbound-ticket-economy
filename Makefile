PYTHON ?= python3.12
export PYTHONPATH := src

.PHONY: test build verify audit pilot collect phase2 audit-phase2 phase3a audit-phase3a validate-phase3a phase3b audit-phase3b validate-phase3b
test:
	$(PYTHON) -m unittest discover -s tests -v
build:
	$(PYTHON) -m riftbound_tickets.cli build
verify:
	$(PYTHON) -m riftbound_tickets.cli verify
audit:
	$(PYTHON) -m riftbound_tickets.cli audit
pilot:
	$(PYTHON) -m riftbound_tickets.cli validate-pilot
collect:
	$(PYTHON) -m riftbound_tickets.cli collect --scope all --workers 3
phase2:
	$(PYTHON) -m riftbound_tickets.cli phase2
audit-phase2:
	$(PYTHON) -m riftbound_tickets.cli audit-phase2
phase3a:
	$(PYTHON) -m riftbound_tickets.phase3a build
audit-phase3a:
	$(PYTHON) -m riftbound_tickets.phase3a audit
validate-phase3a:
	$(PYTHON) scripts/validate_phase3a.py
phase3b:
	$(PYTHON) -m riftbound_tickets.phase3b build
audit-phase3b:
	$(PYTHON) -m riftbound_tickets.phase3b audit
validate-phase3b:
	$(PYTHON) scripts/validate_phase3b.py

.PHONY: phase4 audit-phase4 validate-phase4
phase4:
	$(PYTHON) -m riftbound_tickets.phase4 build
audit-phase4:
	$(PYTHON) -m riftbound_tickets.phase4 audit
validate-phase4:
	$(PYTHON) scripts/validate_phase4.py
