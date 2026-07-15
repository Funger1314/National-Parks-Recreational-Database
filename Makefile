PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
DOCKER_COMPOSE ?= docker compose

.PHONY: setup inspect export-recovered restore-legacy audit-legacy initialize-core migrate quality analysis figures test reproduce

setup:
	python3 -m venv .venv
	$(PIP) install -e ".[dev]"

inspect:
	./scripts/inspect_dump.sh

export-recovered:
	./scripts/export_recovered_data.sh

restore-legacy:
	./scripts/restore_legacy_dump.sh

audit-legacy:
	./scripts/inspect_dump.sh

initialize-core:
	./scripts/initialize_core_database.sh

migrate:
	./scripts/migrate_legacy_to_core.sh

quality:
	./scripts/run_quality_checks.sh

analysis:
	./scripts/run_analysis.sh

figures:
	$(PYTHON) -m national_parks.cli run-analysis --write-figures

test:
	$(PYTHON) -m pytest

reproduce: export-recovered analysis

