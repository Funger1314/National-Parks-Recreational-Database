#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
require_legacy_dump

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN. Run 'make setup' first." >&2
  exit 1
fi

mkdir -p outputs/query_results outputs/quality_reports outputs/figures
mkdir -p work/mplconfig

MPLCONFIGDIR="$PROJECT_ROOT/work/mplconfig" "$PYTHON_BIN" -m national_parks.cli run-analysis \
  --dump "$(legacy_dump_host_path)" \
  --write-figures

"$PYTHON_BIN" -m national_parks.cli write-source-manifest

echo "Analysis outputs refreshed under outputs/ and data/source_manifest.yml"
