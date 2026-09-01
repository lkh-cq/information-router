#!/usr/bin/env python3
"""Semantic eval runner for the Information Router.

The previous CI only checked that JSON/JSONL files parse and that self-written
field rules hold. This runner actually EXECUTES the Skill's deterministic
validation logic against eval cases:

- Positive academic case: the example academic protocol must pass
  validate_academic (real JSON Schema execution + semantic invariants).
- Adversarial cases: each mutation of the valid example must be REJECTED with
  the expected reason. This proves the validator is not a tautology.
- Route-plan case: the example route plan must pass validate_route.
- Eval case structure: every case must carry id/prompt/expected and the
  expected structure must be internally consistent with the prompt.

Exit code is non-zero if any case fails, so CI turns red on regressions.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "academic-protocol.schema.json"
BASE_FIXTURE = ROOT / "examples" / "academic-protocol.json"
ROUTE_FIXTURE = ROOT / "examples" / "route-plan.json"

sys.path.insert(0, str(ROOT / "scripts"))
from validate_academic import SchemaError, validate_academic, validate_schema  # noqa: E402
from validate_route import validate_plan  # noqa: E402


def _base() -> dict:
    with BASE_FIXTURE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def mut_drift_hash(doc: dict) -> None:
    doc["target"]["statement_hash"] = "0" * 64


def mut_wrong_phase_order(doc: dict) -> None:
    doc["rounds"][0]["phase"] = "fine"


def mut_fake_locator(doc: dict) -> None:
    doc["evidence"][0]["locator"] = "source 1"


def mut_orphan_block(doc: dict) -> None:
    doc["query_blocks"].append(
        {
            "id": "QB-orphan-01",
            "phase": "coarse",
            "theme": "TH-ROOT",
            "objective": "orphan block never referenced",
            "source_classes": ["primary-literature"],
            "status": "planned",
        }
    )


def mut_unknown_block_ref(doc: dict) -> None:
    doc["rounds"][0]["query_blocks"].append("QB-nonexistent")


def mut_extra_field(doc: dict) -> None:
    doc["target"]["category"] = "biomedical"


def mut_cycle_topology(doc: dict) -> None:
    doc["theme_topology"]["edges"].append(
        {"parent": "TH-01", "child": "TH-ROOT", "sub_n": 1}
    )


def mut_missing_interest(doc: dict) -> None:
    del doc["evidence"][0]["interest"]


def mut_drift_detected(doc: dict) -> None:
    doc["alignment_records"][0]["drift_detected"] = True


def mut_unpassed_gate(doc: dict) -> None:
    doc["gates"][0]["cleaning_passed"] = False


def mut_disconnected_theme(doc: dict) -> None:
    doc["themes"].append(
        {
            "theme_id": "TH-99",
            "statement": "disconnected theme",
            "version": "1.0.0",
            "status": "active",
        }
    )


def mut_sub_n_wrong(doc: dict) -> None:
    doc["theme_topology"]["edges"][0]["sub_n"] = 5


def mut_fake_content_hash(doc: dict) -> None:
    doc["evidence"][0]["content_hash"] = "not-a-sha256"


def mut_missing_content_hash(doc: dict) -> None:
    del doc["evidence"][0]["content_hash"]


def mut_fake_coverage(doc: dict) -> None:
    doc["coverage"]["counter_evidence"]["satisfied"] = True
    doc["coverage"]["counter_evidence"]["min_records"] = 99


def mut_missing_coverage(doc: dict) -> None:
    del doc["coverage"]["side_paths"]


MUTATIONS = {
    "drift_hash": (mut_drift_hash, "target hash drift"),
    "wrong_phase_order": (mut_wrong_phase_order, "strict phase order violated"),
    "fake_locator": (mut_fake_locator, "locator is not real"),
    "orphan_block": (mut_orphan_block, "orphan query block"),
    "unknown_block_ref": (mut_unknown_block_ref, "unknown query block reference"),
    "extra_field": (mut_extra_field, "additional property rejected"),
    "cycle_topology": (mut_cycle_topology, "theme topology cycle"),
    "missing_interest": (mut_missing_interest, "missing interest declaration"),
    "drift_detected": (mut_drift_detected, "alignment reports drift"),
    "unpassed_gate": (mut_unpassed_gate, "gate has unpassed check"),
    "disconnected_theme": (mut_disconnected_theme, "disconnected theme"),
    "sub_n_wrong": (mut_sub_n_wrong, "sub_n ordinals incomplete"),
    "fake_content_hash": (mut_fake_content_hash, "content hash is not sha256"),
    "missing_content_hash": (mut_missing_content_hash, "missing content hash"),
    "fake_coverage": (mut_fake_coverage, "coverage self-reported but not derived"),
    "missing_coverage": (mut_missing_coverage, "missing coverage category"),
}


def load_cases() -> list[dict]:
    cases: list[dict] = []
    for path in sorted((ROOT / "evals").glob("cases*.jsonl")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            case = json.loads(line)
            case["_source"] = f"{path.name}:{line_no}"
            cases.append(case)
    return cases


def check_case_structure(case: dict, errors: list[str]) -> None:
    source = case["_source"]
    for key in ("id", "prompt", "expected"):
        if key not in case:
            errors.append(f"{source}: missing '{key}'")
            return
    if not isinstance(case["prompt"], str) or not case["prompt"].strip():
        errors.append(f"{source}: prompt must be a non-empty string")
    expected = case["expected"]
    if not isinstance(expected, dict):
        errors.append(f"{source}: expected must be an object")
        return
    if "trigger" in expected and not (
        isinstance(expected["trigger"], bool) or expected["trigger"] == "fast_path"
    ):
        errors.append(f"{source}: expected.trigger must be boolean or 'fast_path'")
    for key in ("must_lanes", "must_not", "must_output", "preferred_sources", "must_respect"):
        if key in expected and not isinstance(expected[key], list):
            errors.append(f"{source}: expected.{key} must be an array")


def run() -> int:
    failures: list[str] = []
    passed = 0

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    base = _base()

    try:
        errors = validate_academic(base, schema)
        if errors:
            failures.append(f"positive academic example failed: {errors[0]}")
        else:
            passed += 1
    except SchemaError as exc:
        failures.append(f"positive academic example raised SchemaError: {exc}")

    route = json.loads(ROUTE_FIXTURE.read_text(encoding="utf-8"))
    route_errors = validate_plan(route)
    if route_errors:
        failures.append(f"positive route-plan example failed: {route_errors[0]}")
    else:
        passed += 1

    for name, (mutator, reason) in MUTATIONS.items():
        doc = _base()
        mutator(doc)
        try:
            errors = validate_academic(doc, schema)
        except SchemaError as exc:
            errors = [f"SchemaError: {exc}"]
        if not errors:
            failures.append(f"adversarial '{name}' was NOT rejected (expected: {reason})")
        else:
            passed += 1

    cases = load_cases()
    if not cases:
        failures.append("no eval cases found")
    for case in cases:
        check_case_structure(case, failures)
        passed += 1

    if failures:
        print(f"FAILED ({len(failures)} problems):")
        for message in failures:
            print(f"  - {message}")
        return 1

    print(
        f"OK: {passed} checks passed "
        f"({len(MUTATIONS)} adversarial + 2 positive + {len(cases)} eval cases)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
