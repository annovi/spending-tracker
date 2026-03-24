#!/usr/bin/env python3
"""Import every .csv in a directory into the spending-tracker database.

Uses the same parsers and deduplication (import_hash) as the HTTP import API.

Run from the repository backend folder so `.env` / DATABASE_URL resolve:

  cd backend
  python scripts/bulk_import_csv.py ~/Downloads/statements --bank-preset td_visa
  python scripts/bulk_import_csv.py ~/Downloads/mixed --auto
  python scripts/bulk_import_csv.py ~/data --mapping-json mapping.json

Bank presets: td_visa, scotia_visa, scotia_bank, amex
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal  # noqa: E402
from app.schemas.csv_import import ColumnMapping  # noqa: E402
from app.services.bank_parsers import BankPreset, parse_bank_csv  # noqa: E402
from app.services.csv_parser_v2 import parse_transactions_csv_with_mapping  # noqa: E402
from app.services.import_batch import import_parsed_transactions  # noqa: E402


def _csv_paths(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir() if p.suffix.lower() == ".csv" and p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", type=Path, help="Folder containing .csv files")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--bank-preset",
        choices=[p.value for p in BankPreset],
        help="Parse all files with this bank-specific parser",
    )
    mode.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect columns per file (generic CSV)",
    )
    mode.add_argument(
        "--mapping-json",
        type=Path,
        help="Path to JSON column mapping applied to every file",
    )
    parser.add_argument(
        "--account-id",
        type=int,
        default=None,
        help="Optional account id to attach to imported rows",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse only; do not write to the database",
    )
    args = parser.parse_args()
    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        print(f"Not a directory: {directory}", file=sys.stderr)
        return 1

    paths = _csv_paths(directory)
    if not paths:
        print(f"No .csv files in {directory}", file=sys.stderr)
        return 1

    fixed_mapping: ColumnMapping | None = None
    if args.mapping_json:
        raw = json.loads(args.mapping_json.read_text(encoding="utf-8"))
        fixed_mapping = ColumnMapping(**raw)

    total_imported = 0
    total_dups = 0
    db = None
    if not args.dry_run:
        db = SessionLocal()

    try:
        for path in paths:
            data = path.read_bytes()
            try:
                if args.bank_preset:
                    parsed = parse_bank_csv(data, BankPreset(args.bank_preset))
                elif args.auto:
                    parsed, _ = parse_transactions_csv_with_mapping(data, mapping=None)
                else:
                    parsed, _ = parse_transactions_csv_with_mapping(data, mapping=fixed_mapping)
            except Exception as e:
                print(f"{path.name}: ERROR {e}", file=sys.stderr)
                continue

            if args.dry_run:
                print(f"{path.name}: would import {len(parsed)} row(s) (dry-run)")
                continue

            assert db is not None
            result = import_parsed_transactions(db, parsed, path.name, args.account_id)
            imp = result["rows_imported"]
            dup = result["duplicates_skipped"]
            total_imported += imp
            total_dups += dup
            print(f"{path.name}: imported {imp}, duplicates skipped {dup}")
    finally:
        if db is not None:
            db.close()

    if not args.dry_run:
        print(f"Total: imported {total_imported}, duplicates skipped {total_dups}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
