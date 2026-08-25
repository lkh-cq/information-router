#!/usr/bin/env python3
"""Validate high-value RoutePlan schema and semantic invariants using stdlib only."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


LANES = {
    "orientation",
    "direct",
    "alias",
    "topology",
    "contradiction",
    "long-tail",
    "resource",
    "citation",
}
MODES = {"lookup", "discover", "verify", "synthesize", "reproduce", "monitor"}
STAKES = {"low", "medium", "high"}
FRESHNESS = {"historical", "as_of", "current", "recurring"}
MODALITIES = {
    "web",
    "literature",
    "code",
    "data",
    "standards",
    "patents",
    "registries",
    "local_files",
}
BLOCK_STATUS = {"planned", "executed", "blocked", "skipped"}
OUTPUTS = {
    "quick_answer",
    "search_plan",
    "evidence_map",
    "audit",
    "reproduction_package",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_keys(value: Any, keys: set[str], path: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return False
    missing = sorted(keys - set(value))
    if missing:
        errors.append(f"{path} missing required keys: {', '.join(missing)}")
    return not missing


def nonempty_string(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def string_list(value: Any, path: str, errors: list[str], *, nonempty: bool = False) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return
    if nonempty and not value:
        errors.append(f"{path} must contain at least one item")
    for index, item in enumerate(value):
        nonempty_string(item, f"{path}[{index}]", errors)


def optional_date(value: Any, path: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        errors.append(f"{path} must be an ISO date or null")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path} must be an ISO date")


def validate_profile(profile: Any, errors: list[str]) -> None:
    required = {
        "goal",
        "mode",
        "domain",
        "stakes",
        "freshness",
        "modalities",
        "constraints",
        "must_preserve",
    }
    if not require_keys(profile, required, "request_profile", errors):
        return
    nonempty_string(profile["goal"], "request_profile.goal", errors)
    nonempty_string(profile["domain"], "request_profile.domain", errors)
    if profile["mode"] not in MODES:
        errors.append(f"request_profile.mode must be one of {sorted(MODES)}")
    if profile["stakes"] not in STAKES:
        errors.append(f"request_profile.stakes must be one of {sorted(STAKES)}")

    freshness = profile["freshness"]
    if require_keys(freshness, {"kind"}, "request_profile.freshness", errors):
        if freshness["kind"] not in FRESHNESS:
            errors.append(f"request_profile.freshness.kind must be one of {sorted(FRESHNESS)}")
        optional_date(freshness.get("as_of"), "request_profile.freshness.as_of", errors)

    modalities = profile["modalities"]
    if not isinstance(modalities, list) or not modalities:
        errors.append("request_profile.modalities must be a non-empty array")
    else:
        unknown = sorted(set(modalities) - MODALITIES)
        if unknown:
            errors.append(f"request_profile.modalities contains unknown values: {unknown}")
        if len(modalities) != len(set(modalities)):
            errors.append("request_profile.modalities must be unique")

    constraints = profile["constraints"]
    constraint_keys = {"languages", "geographies", "prohibited_sources", "required_sources"}
    if require_keys(constraints, constraint_keys, "request_profile.constraints", errors):
        for key in constraint_keys:
            string_list(constraints[key], f"request_profile.constraints.{key}", errors)
        optional_date(constraints.get("date_from"), "request_profile.constraints.date_from", errors)
        optional_date(constraints.get("date_to"), "request_profile.constraints.date_to", errors)

    preserve = profile["must_preserve"]
    preserve_keys = {"entities", "contexts", "relations", "exclusions"}
    if require_keys(preserve, preserve_keys, "request_profile.must_preserve", errors):
        for key in preserve_keys:
            string_list(preserve[key], f"request_profile.must_preserve.{key}", errors)


def validate_plan(plan: Any) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "request_profile",
        "lanes",
        "query_blocks",
        "stop_rules",
        "output_contract",
    }
    if not require_keys(plan, required, "<root>", errors):
        return errors
    if plan["schema_version"] != "0.1.0":
        errors.append("schema_version must equal '0.1.0'")
    validate_profile(plan["request_profile"], errors)

    lanes = plan["lanes"]
    lane_names: list[str] = []
    lane_required = {
        "name",
        "trigger",
        "objective",
        "source_classes",
        "completion_condition",
        "residual_risk",
    }
    if not isinstance(lanes, list) or not lanes:
        errors.append("lanes must be a non-empty array")
        lanes = []
    for index, lane in enumerate(lanes):
        path = f"lanes[{index}]"
        if not require_keys(lane, lane_required, path, errors):
            continue
        if lane["name"] not in LANES:
            errors.append(f"{path}.name must be one of {sorted(LANES)}")
        else:
            lane_names.append(lane["name"])
        for key in ("trigger", "objective", "completion_condition", "residual_risk"):
            nonempty_string(lane[key], f"{path}.{key}", errors)
        string_list(lane["source_classes"], f"{path}.source_classes", errors, nonempty=True)
    if len(lane_names) != len(set(lane_names)):
        errors.append("lanes must not contain duplicate names")

    blocks = plan["query_blocks"]
    block_ids: list[str] = []
    block_lanes: list[str] = []
    block_required = {
        "id",
        "lane",
        "objective",
        "concepts",
        "source_classes",
        "must_preserve",
        "status",
    }
    if not isinstance(blocks, list) or not blocks:
        errors.append("query_blocks must be a non-empty array")
        blocks = []
    for index, block in enumerate(blocks):
        path = f"query_blocks[{index}]"
        if not require_keys(block, block_required, path, errors):
            continue
        block_id = block["id"]
        if not isinstance(block_id, str) or not block_id.startswith("QB-"):
            errors.append(f"{path}.id must start with 'QB-'")
        else:
            block_ids.append(block_id)
        if block["lane"] not in LANES:
            errors.append(f"{path}.lane must be one of {sorted(LANES)}")
        else:
            block_lanes.append(block["lane"])
        nonempty_string(block["objective"], f"{path}.objective", errors)
        concepts = block["concepts"]
        if not isinstance(concepts, dict) or not concepts:
            errors.append(f"{path}.concepts must be a non-empty object")
        else:
            for key, values in concepts.items():
                string_list(values, f"{path}.concepts.{key}", errors, nonempty=True)
        string_list(block["source_classes"], f"{path}.source_classes", errors, nonempty=True)
        string_list(block["must_preserve"], f"{path}.must_preserve", errors)
        if block["status"] not in BLOCK_STATUS:
            errors.append(f"{path}.status must be one of {sorted(BLOCK_STATUS)}")
    if len(block_ids) != len(set(block_ids)):
        errors.append("query block IDs must be unique")

    for lane in lane_names:
        if lane not in block_lanes:
            errors.append(f"selected lane {lane!r} has no query block")
    for lane in block_lanes:
        if lane not in lane_names:
            errors.append(f"query block references unselected lane {lane!r}")

    known_ids = set(block_ids)
    groups = plan.get("parallel_groups", [])
    if not isinstance(groups, list):
        errors.append("parallel_groups must be an array")
    else:
        for index, group in enumerate(groups):
            if not isinstance(group, list) or len(group) < 2:
                errors.append(f"parallel_groups[{index}] must contain at least two block IDs")
                continue
            unknown = sorted(set(group) - known_ids)
            if unknown:
                errors.append(
                    f"parallel_groups[{index}] references unknown blocks: {', '.join(unknown)}"
                )

    stop_keys = {"sentinel_recovery", "marginal_yield", "coverage", "contradictions", "provenance"}
    stop_rules = plan["stop_rules"]
    if require_keys(stop_rules, stop_keys, "stop_rules", errors):
        for key in stop_keys:
            nonempty_string(stop_rules[key], f"stop_rules.{key}", errors)
    if plan["output_contract"] not in OUTPUTS:
        errors.append(f"output_contract must be one of {sorted(OUTPUTS)}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_route.py PATH_TO_ROUTE_PLAN.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).resolve()
    try:
        plan = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_plan(plan)
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
