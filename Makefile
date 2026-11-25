PYTHON ?= python3.12
export PYTHONPATH := src

.PHONY: test build verify audit pilot collect
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
