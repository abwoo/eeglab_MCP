"""Write gate test cases for the MATLAB port of the method gates.

For every requirement check, build random contexts from the keys that check
reads and record what the Python gate decides. run_eegmcp_gate_tests.m
replays the cases against eegmcp_check_requirement and eegmcp_preflight_eval,
so the MATLAB gates cannot drift from eeglab_mcp_server/official_alignment.py.

Usage: python matlab/tests/generate_gate_cases.py OUTPUT.json
"""

from __future__ import annotations

import inspect
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eeglab_mcp_server import official_alignment as oa

GENERIC = [
    True,
    False,
    "",
    "  ",
    "x",
    "complete",
    "continuous",
    "edf",
    "data.set",
    "bids",
    "preserved",
    "multi_subject",
    1,
    0,
    2.5,
    None,
    [],
    {},
    ["a"],
    ["a", "b"],
    {"k": True},
    {"k": False},
]
POOLS = {
    "roles": [
        [],
        ["condition"],
        ["boundary"],
        ["boundary", "impedance"],
        [" Stimulus "],
        {"S1": "condition"},
        {"S1": "boundary"},
        "x",
    ],
    "plugins": [[], ["iclabel"], ["BIOSIG"], ["pop_loadbv"], ["eeg-bids"], ["limo"], ["amica"], "iclabel"],
    "missing": [
        "reference;line_freq",
        ["impedance"],
        {"task_name": True},
        {"task_name": False},
        "",
        [],
        "acquisition_filters, montage",
    ],
    "sidecars": [
        ["sub-01_eeg.json", "sub-01_channels.tsv", "electrodes.tsv", "coordsystem.json"],
        ["x_eeg.json"],
        {"eeg": "sub_eeg.json"},
        [],
    ],
    "columns": [["onset", "duration"], ["Onset", " duration "], ["onset"], []],
    "coverage": [1, 1.0, 0.5, "complete", True, False],
}
KEY_POOLS = {
    "event_roles": "roles",
    "marker_roles": "roles",
    "plugins_available": "plugins",
    "available_plugins": "plugins",
    "documented_missing_fields": "missing",
    "missing_metadata_documented": "missing",
    "sidecars": "sidecars",
    "sidecar_paths": "sidecars",
    "events_tsv_columns": "columns",
    "event_columns": "columns",
    "channel_location_coverage": "coverage",
}
HELPER_KEYS = {
    "_event_roles": ["event_roles", "marker_roles"],
    "_plugins_include": ["plugins_available", "available_plugins"],
    "_field_recorded_or_documented_missing": ["documented_missing_fields", "missing_metadata_documented"],
    "_sidecars_include": ["sidecars", "sidecar_paths"],
}


def check_keys() -> dict[str, list[str]]:
    """Context keys each check reads, taken from the Python source."""
    source = inspect.getsource(oa._check_requirement)
    blocks = re.split(r'\n    if check == "', source)[1:]
    keys: dict[str, list[str]] = {}
    for block in blocks:
        name, body = block.split('"', 1)
        literals = set(re.findall(r'"([A-Za-z_][\w.\-]*)"', body))
        for helper, helper_keys in HELPER_KEYS.items():
            if helper in body:
                literals.update(helper_keys)
        if "_plugins_include" in body or "format_plugins" in body:
            literals.update(f"plugin_{item.lower()}_available" for item in list(literals))
        keys[name] = sorted(literals)
    # Checks that call other checks also read those checks' keys.
    for block in blocks:
        name, body = block.split('"', 1)
        for nested in re.findall(r'_check_requirement\("(\w+)"', body):
            keys[name] = sorted(set(keys[name]) | set(keys[nested]))
    return keys


def random_context(rng: random.Random, keys: list[str]) -> dict:
    context = {}
    for key in keys:
        if rng.random() < 0.4:
            context[key] = rng.choice(POOLS.get(KEY_POOLS.get(key, ""), GENERIC))
    return context


def main() -> None:
    rng = random.Random(20261008)
    keys = check_keys()
    all_keys = sorted({key for value in keys.values() for key in value})
    check_cases = []
    for check, check_key_list in keys.items():
        for _ in range(60):
            context = random_context(rng, check_key_list)
            check_cases.append({"check": check, "context": context, "expected": oa._check_requirement(check, context)})
        check_cases.append({"check": check, "context": {}, "expected": oa._check_requirement(check, {})})

    preflight_cases = []
    for profile_id, profile in oa.METHOD_PROFILES.items():
        profile_keys = sorted({k for req in profile["requirements"] for k in keys.get(req["check"], [])})
        for index in range(12):
            context = random_context(rng, profile_keys or all_keys[:5])
            args = {
                "method": profile_id if index % 2 else "",
                "tool_name": "" if index % 2 or not profile["tool_names"] else profile["tool_names"][0],
                "context": context,
                "strictness": rng.choice(["hard", "advisory"]),
                "override_reason": rng.choice(["", "", "user accepted the risk"]),
            }
            if not args["method"] and not args["tool_name"]:
                args["method"] = profile_id
            result = oa.evaluate_method_preflight(args)
            preflight_cases.append(
                {
                    **args,
                    "gate_status": result["gate_status"],
                    "method_profile_id": result["method_profile_id"],
                    "missing_ids": [req["id"] for req in result["missing_requirements"]],
                }
            )
    preflight_cases.append(
        {
            "method": "not_a_method",
            "tool_name": "",
            "context": {},
            "strictness": "hard",
            "override_reason": "",
            "gate_status": "unknown_method",
            "method_profile_id": "",
            "missing_ids": [],
        }
    )

    Path(sys.argv[1]).write_text(json.dumps({"checks": check_cases, "preflight": preflight_cases}, indent=1))
    print(f"wrote {len(check_cases)} check cases and {len(preflight_cases)} preflight cases")


if __name__ == "__main__":
    main()
