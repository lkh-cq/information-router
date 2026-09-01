#!/usr/bin/env python3
"""Validate an Information Router Academic Protocol document.

This validator does two things that the previous "plan format" checks did not:

1. EXECUTES the real JSON Schema (schemas/academic-protocol.schema.json) with a
   self-contained draft-2020-12 executor covering the subset the schema uses
   (type/const/enum/required/properties/additionalProperties/items/minItems/
   maxItems/uniqueItems/minLength/pattern/minProperties/$ref/$defs). No external
   dependency; CI does not need to install anything.

2. Checks semantic invariants that a JSON Schema alone cannot express:
   - Target drift: statement_hash must equal sha256(statement); every round and
     alignment record must carry the same frozen hash and report no drift.
   - Theme topology: every referenced theme exists, the parent/child graph is a
     tree (no cycles, one parent per non-root), and sub_n ordinals are complete.
   - Strict phase order: rounds must be exactly coarse -> subtheme -> fine.
   - Query-block closure: every round references existing QB ids, every QB is
     referenced by a round whose phase matches, and every QB theme exists.
   - Evidence integrity: locators must be real (URL/DOI/arXiv/PMID/file), every
     evidence maps to an existing query block, and interest/funding/family are
     recorded.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    pass


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_node(instance: Any, schema: dict, defs: dict, path: str, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        return

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise SchemaError(f"{path}: unsupported $ref {ref!r}")
        name = ref[len("#/$defs/") :]
        if name not in defs:
            raise SchemaError(f"{path}: unknown $def {name!r}")
        _validate_node(instance, defs[name], defs, path, errors)
        return

    if "type" in schema and not _type_ok(instance, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']!r}, got {type(instance).__name__}")
        return

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: must equal const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: does not match pattern {schema['pattern']!r}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen: list[Any] = []
            for item in instance:
                if item in seen:
                    errors.append(f"{path}: items must be unique")
                    break
                seen.append(item)
        if "items" in schema:
            for index, item in enumerate(instance):
                _validate_node(item, schema["items"], defs, f"{path}[{index}]", errors)

    if isinstance(instance, dict):
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(f"{path}: fewer than minProperties {schema['minProperties']}")
        if "required" in schema:
            for key in schema["required"]:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")
        if "properties" in schema:
            for key, subschema in schema["properties"].items():
                if key in instance:
                    _validate_node(instance[key], subschema, defs, f"{path}.{key}", errors)
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            for key in instance:
                if key not in allowed:
                    errors.append(f"{path}: additional property {key!r} is not allowed")


def validate_schema(instance: Any, schema: dict) -> list[str]:
    errors: list[str] = []
    defs = schema.get("$defs", {})
    if not isinstance(defs, dict):
        raise SchemaError("$defs must be an object")
    _validate_node(instance, schema, defs, "$", errors)
    return errors


LOCATOR_PATTERNS = [
    re.compile(r"^https?://[^\s]+$"),
    re.compile(r"^10\.\d{4,9}/[^\s]+$"),
    re.compile(r"^arXiv:\d{4}\.\d{4,5}(v\d+)?$"),
    re.compile(r"^PMID:\d+$"),
    re.compile(r"^file://[^\s]+$"),
]

PHASE_ORDER = ["coarse", "subtheme", "fine"]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_target(protocol: dict, errors: list[str]) -> str:
    target = protocol["target"]
    statement = target["statement"]
    expected_hash = _sha256(statement)
    if target["statement_hash"] != expected_hash:
        errors.append(
            f"target.statement_hash {target['statement_hash']} != sha256(statement) {expected_hash}"
        )
    return target["statement_hash"]


def check_theme_topology(protocol: dict, errors: list[str]) -> None:
    themes = {t["theme_id"] for t in protocol["themes"]}
    topology = protocol["theme_topology"]
    roots = topology["roots"]
    edges = topology["edges"]

    for root in roots:
        if root not in themes:
            errors.append(f"theme_topology.roots references unknown theme {root!r}")
    for edge in edges:
        if edge["parent"] not in themes:
            errors.append(f"theme_topology edge parent {edge['parent']!r} not in themes")
        if edge["child"] not in themes:
            errors.append(f"theme_topology edge child {edge['child']!r} not in themes")

    children = {e["child"] for e in edges}
    for root in roots:
        if root in children:
            errors.append(f"theme {root!r} is both a root and a child")

    child_to_parent: dict[str, str] = {}
    for edge in edges:
        if edge["child"] in child_to_parent:
            errors.append(f"theme {edge['child']!r} has more than one parent")
        child_to_parent[edge["child"]] = edge["parent"]

    for theme_id in themes:
        if theme_id not in roots and theme_id not in child_to_parent:
            errors.append(f"theme {theme_id!r} is neither a root nor a child (disconnected)")

    visited: set[str] = set()
    stack: set[str] = set()

    def visit(node: str) -> None:
        if node in stack:
            errors.append(f"theme topology contains a cycle at {node!r}")
            return
        if node in visited:
            return
        stack.add(node)
        for edge in edges:
            if edge["parent"] == node:
                visit(edge["child"])
        stack.discard(node)
        visited.add(node)

    for root in roots:
        visit(root)

    parent_children: dict[str, list[str]] = {}
    for edge in edges:
        parent_children.setdefault(edge["parent"], []).append(edge["child"])
    for parent, kids in parent_children.items():
        ordinals = sorted(e["sub_n"] for e in edges if e["parent"] == parent)
        expected = list(range(1, len(kids) + 1))
        if ordinals != expected:
            errors.append(
                f"theme {parent!r} sub_n ordinals {ordinals} must be exactly {expected}"
            )


def check_rounds(protocol: dict, frozen_hash: str, errors: list[str]) -> None:
    rounds = protocol["rounds"]
    if len(rounds) != 3:
        errors.append(f"rounds must contain exactly 3 entries, got {len(rounds)}")
        return

    qb_ids = {qb["id"] for qb in protocol["query_blocks"]}
    qb_by_id = {qb["id"]: qb for qb in protocol["query_blocks"]}
    theme_ids = {t["theme_id"] for t in protocol["themes"]}

    for index, round_ in enumerate(rounds):
        expected_phase = PHASE_ORDER[index]
        if round_["phase"] != expected_phase:
            errors.append(
                f"rounds[{index}] phase {round_['phase']!r} must be {expected_phase!r} "
                f"(strict order coarse -> subtheme -> fine)"
            )
        if round_["target_hash"] != frozen_hash:
            errors.append(f"rounds[{index}] target_hash drifts from frozen target hash")
        if not round_["alignment"]["target_rechecked"]:
            errors.append(f"rounds[{index}] alignment.target_rechecked must be true")
        if round_["alignment"].get("drift_detected"):
            errors.append(f"rounds[{index}] alignment reports drift_detected=true")

        for qb_id in round_["query_blocks"]:
            if qb_id not in qb_ids:
                errors.append(f"rounds[{index}] references unknown query block {qb_id!r}")
            else:
                qb = qb_by_id[qb_id]
                if qb["phase"] != round_["phase"]:
                    errors.append(
                        f"query block {qb_id!r} phase {qb['phase']!r} does not match "
                        f"round phase {round_['phase']!r}"
                    )
                if qb["theme"] not in theme_ids:
                    errors.append(f"query block {qb_id!r} references unknown theme {qb['theme']!r}")

        for theme in round_["alignment"]["themes_covered"]:
            if theme not in theme_ids:
                errors.append(f"rounds[{index}] alignment covers unknown theme {theme!r}")

    referenced = {qb for round_ in rounds for qb in round_["query_blocks"]}
    for qb_id in qb_ids:
        if qb_id not in referenced:
            errors.append(f"query block {qb_id!r} is never referenced by any round (orphan)")


def check_alignment_records(protocol: dict, frozen_hash: str, errors: list[str]) -> None:
    round_ids = {r["round_id"] for r in protocol["rounds"]}
    for record in protocol["alignment_records"]:
        if record["round_id"] not in round_ids:
            errors.append(f"alignment record references unknown round {record['round_id']!r}")
        if record["target_hash"] != frozen_hash:
            errors.append(f"alignment record {record['round_id']} target_hash drifts")
        if record["drift_detected"]:
            errors.append(f"alignment record {record['round_id']} reports drift_detected=true")


def check_gates(protocol: dict, errors: list[str]) -> None:
    round_ids = {r["round_id"] for r in protocol["rounds"]}
    for gate in protocol["gates"]:
        if gate["round_id"] not in round_ids:
            errors.append(f"gate references unknown round {gate['round_id']!r}")
        if not (gate["cleaning_passed"] and gate["review_passed"] and gate["regression_passed"]):
            errors.append(f"gate {gate['round_id']} has an unpassed check")


def check_evidence(protocol: dict, errors: list[str]) -> None:
    qb_ids = {qb["id"] for qb in protocol["query_blocks"]}
    for record in protocol["evidence"]:
        if record["query_block"] not in qb_ids:
            errors.append(
                f"evidence {record['evidence_id']} references unknown query block "
                f"{record['query_block']!r}"
            )
        locator = record["locator"]
        if not any(pattern.match(locator) for pattern in LOCATOR_PATTERNS):
            errors.append(
                f"evidence {record['evidence_id']} locator {locator!r} is not a real "
                f"URL/DOI/arXiv/PMID/file locator"
            )
        if not record["interest"]["declared"]:
            errors.append(f"evidence {record['evidence_id']} interest.declared must be true")
        if not record["funding"].strip():
            errors.append(f"evidence {record['evidence_id']} funding must be non-empty")
        if not record["family"].strip():
            errors.append(f"evidence {record['evidence_id']} family must be non-empty")


def _coverage_counts(protocol: dict) -> dict[str, int]:
    counts = {
        "counter_evidence": 0,
        "negative_results": 0,
        "long_tail": 0,
        "small_papers": 0,
        "side_paths": 0,
    }
    for record in protocol["evidence"]:
        kind = record.get("evidence_kind")
        polarity = record.get("polarity")
        if polarity == "contradicting" or kind == "counter_evidence":
            counts["counter_evidence"] += 1
        if polarity == "null" or kind == "negative_result":
            counts["negative_results"] += 1
        if kind == "long_tail":
            counts["long_tail"] += 1
        if kind == "small_paper":
            counts["small_papers"] += 1
        if kind == "side_path":
            counts["side_paths"] += 1
    return counts


def check_coverage(protocol: dict, errors: list[str]) -> None:
    """Verify minimum coverage for counter-evidence, negative results, long-tail,
    small papers, and side paths is DERIVED from actual evidence records, not
    self-reported. A declared satisfied=true with too few real records is an error."""
    coverage = protocol.get("coverage", {})
    counts = _coverage_counts(protocol)
    for category, requirement in coverage.items():
        min_records = requirement.get("min_records", 0)
        actual = counts.get(category, 0)
        if actual < min_records:
            errors.append(
                f"coverage.{category}: need at least {min_records} record(s), "
                f"found {actual}"
            )
        derived_satisfied = actual >= min_records
        if requirement.get("satisfied") != derived_satisfied:
            errors.append(
                f"coverage.{category}: declared satisfied={requirement.get('satisfied')} "
                f"does not match derived {derived_satisfied} from {actual} record(s)"
            )


def validate_academic(protocol: dict, schema: dict) -> list[str]:
    errors = validate_schema(protocol, schema)
    if errors:
        return errors
    frozen_hash = check_target(protocol, errors)
    check_theme_topology(protocol, errors)
    check_rounds(protocol, frozen_hash, errors)
    check_alignment_records(protocol, frozen_hash, errors)
    check_gates(protocol, errors)
    check_evidence(protocol, errors)
    check_coverage(protocol, errors)
    return errors


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_academic.py PATH_TO_ACADEMIC_PROTOCOL.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / "academic-protocol.schema.json"
    try:
        protocol = load_json(path)
        schema = load_json(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    try:
        errors = validate_academic(protocol, schema)
    except SchemaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
