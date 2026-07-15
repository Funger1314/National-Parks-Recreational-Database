"""Command-line entry points for the national parks data workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from national_parks.config import project_paths
from national_parks.logging_config import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="National parks spatial database utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    raw_parser = subparsers.add_parser("process-raw-visitation")
    raw_parser.add_argument("--input-dir", type=Path, default=project_paths().raw_visitation_dir)
    raw_parser.add_argument(
        "--output-csv",
        type=Path,
        default=project_paths().processed_dir / "np_visitation_processed.csv",
    )
    raw_parser.add_argument(
        "--quality-report",
        type=Path,
        default=project_paths().quality_reports_dir / "visitation_quality_report.csv",
    )

    export_parser = subparsers.add_parser("export-recovered-visitation")
    export_parser.add_argument("--dump", type=Path, required=True)
    export_parser.add_argument(
        "--output-csv",
        type=Path,
        default=project_paths().recovered_dir / "np_visitation_recovered.csv",
    )

    audit_parser = subparsers.add_parser("run-analysis")
    audit_parser.add_argument("--dump", type=Path, required=True)
    audit_parser.add_argument("--write-figures", action="store_true")

    reconcile_parser = subparsers.add_parser("reconcile-migration")
    reconcile_parser.add_argument("--dump", type=Path, required=True)
    reconcile_parser.add_argument(
        "--output-path",
        type=Path,
        default=project_paths().quality_reports_dir / "migration_reconciliation.csv",
    )

    manifest_parser = subparsers.add_parser("write-source-manifest")
    manifest_parser.add_argument(
        "--output-path",
        type=Path,
        default=project_paths().root / "data" / "source_manifest.yml",
    )

    return parser


def main() -> None:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "process-raw-visitation":
        from national_parks.visitation_cleaning import process_raw_visitation_directory

        process_raw_visitation_directory(args.input_dir, args.output_csv, args.quality_report)
    elif args.command == "export-recovered-visitation":
        from national_parks.visitation_cleaning import export_recovered_visitation

        export_recovered_visitation(args.dump, args.output_csv)
    elif args.command == "run-analysis":
        from national_parks.analysis import run_analysis

        run_analysis(args.dump, write_figures_flag=args.write_figures)
    elif args.command == "reconcile-migration":
        from national_parks.analysis import load_public_tables
        from national_parks.migration import write_migration_reconciliation

        write_migration_reconciliation(load_public_tables(args.dump), args.output_path)
    elif args.command == "write-source-manifest":
        from national_parks.provenance import write_source_manifest

        write_source_manifest(args.output_path)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
