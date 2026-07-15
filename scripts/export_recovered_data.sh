#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
require_legacy_dump

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN. Run 'make setup' first." >&2
  exit 1
fi

mkdir -p data/recovered

"$PYTHON_BIN" -m national_parks.cli export-recovered-visitation \
  --dump "$(legacy_dump_host_path)" \
  --output-csv data/recovered/np_visitation_recovered.csv

echo "Recovered visitation data exported to data/recovered/np_visitation_recovered.csv"

