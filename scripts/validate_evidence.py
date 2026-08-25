#!/usr/bin/env python3
"""Validate high-value EvidenceRecord invariants using the Python stdlib."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


POLARITY = {"supporting", "contradicting", "null", "mixed", "contextual", "not_applicable"}
KINDS = {"primary_study", "synthesis", "official_record", "code", "data", "benchmark", "report", "commentary", "other"}
DIRECTNESS = {"direct", "indirect", "inference"}
STATUS = {"active", "superseded", "corrected", "withdrawn", "retracted", "deprecated", "unknown"}
REQUIRED = {
    "record_id",
    "source_id",
    "version_id",
    "study_family_id",
    "claim",
    "polarity",
    "evidence_kind",
    "directness",
    "method",
    "context",
    "independence_group",
    "status",
    "provenance",
}


def records(path: Path) -> list[tuple[int, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        output: list[tuple[int, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                output.append((line_number, json.loads(line)))
        return output
    return [(1, json.loads(text))]


def nonempty_string(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def validate_record(record: Any, line_number: int) -> list[str]:
    prefix = f"line {line_number}"
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{prefix}: record must be an object"]
    missing = sorted(REQUIRED - set(record))
    if missing:
        errors.append(f"{prefix}: missing required keys: {', '.join(missing)}")
        return errors

    for key in ("source_id", "version_id", "study_family_id", "claim", "independence_group"):
        nonempty_string(record[key], f"{prefix}.{key}", errors)
    if not isinstance(record["record_id"], str) or not record["record_id"].startswith("ER-"):
        errors.append(f"{prefix}.record_id must start with 'ER-'")
    if record["polarity"] not in POLARITY:
        errors.append(f"{prefix}.polarity must be one of {sorted(POLARITY)}")
    if record["evidence_kind"] not in KINDS:
        errors.append(f"{prefix}.evidence_kind must be one of {sorted(KINDS)}")
    if record["directness"] not in DIRECTNESS:
        errors.append(f"{prefix}.directness must be one of {sorted(DIRECTNESS)}")
    if record["status"] not in STATUS:
        errors.append(f"{prefix}.status must be one of {sorted(STATUS)}")
    if not isinstance(record["method"], str):
        errors.append(f"{prefix}.method must be a string")
    if not isinstance(record["context"], dict):
        errors.append(f"{prefix}.context must be an object")

    provenance = record["provenance"]
    provenance_required = {"retrieved_at", "query_block_id", "locator"}
    if not isinstance(provenance, dict):
        errors.append(f"{prefix}.provenance must be an object")
    else:
        missing_provenance = sorted(provenance_required - set(provenance))
        if missing_provenance:
            errors.append(
                f"{prefix}.provenance missing required keys: {', '.join(missing_provenance)}"
            )
        else:
            nonempty_string(provenance["locator"], f"{prefix}.provenance.locator", errors)
            query_id = provenance["query_block_id"]
            if not isinstance(query_id, str) or not query_id.startswith("QB-"):
                errors.append(f"{prefix}.provenance.query_block_id must start with 'QB-'")
            retrieved_at = provenance["retrieved_at"]
            if not isinstance(retrieved_at, str):
                errors.append(f"{prefix}.provenance.retrieved_at must be an ISO date")
            else:
                try:
                    date.fromisoformat(retrieved_at)
                except ValueError:
                    errors.append(f"{prefix}.provenance.retrieved_at must be an ISO date")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_evidence.py PATH_TO_RECORD.json|ledger.jsonl", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    try:
        items = records(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen: set[str] = set()
    for line_number, record in items:
        errors.extend(validate_record(record, line_number))
        if isinstance(record, dict) and isinstance(record.get("record_id"), str):
            record_id = record["record_id"]
            if record_id in seen:
                errors.append(f"line {line_number}: duplicate record_id {record_id!r}")
            seen.add(record_id)

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
