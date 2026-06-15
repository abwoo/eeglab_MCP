"""Research workflow handlers for the EEGLAB MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    from .runtime import matlab, matlab_string, _matlab_identifier, _maybe_init
    from .official_alignment import OFFICIAL_PLUGIN_MATRIX
    from .workflows import (
        event_semantics_audit,
        light_erp_parameters,
        method_preflight_workflow,
        parse_tool_result,
        project_plan,
        qc_report_from_payloads,
        protocol_export_payload,
        recommend_workflow,
        structured_payload,
        workflow_error,
        workflow_success,
    )
    from .handlers_data import _eeglab_history, _eeglab_info
    from .handlers_events_erp import (
        _eeglab_epoch,
        _eeglab_erp_analysis,
        _eeglab_get_events,
    )
    from .handlers_preprocessing import _eeglab_filter
    from .handlers_data import _eeglab_init, _eeglab_load_data, _eeglab_save_data
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, matlab_string, _matlab_identifier, _maybe_init
    from official_alignment import OFFICIAL_PLUGIN_MATRIX
    from workflows import (
        event_semantics_audit,
        light_erp_parameters,
        method_preflight_workflow,
        parse_tool_result,
        project_plan,
        qc_report_from_payloads,
        protocol_export_payload,
        recommend_workflow,
        structured_payload,
        workflow_error,
        workflow_success,
    )
    from handlers_data import _eeglab_history, _eeglab_info
    from handlers_events_erp import (
        _eeglab_epoch,
        _eeglab_erp_analysis,
        _eeglab_get_events,
    )
    from handlers_preprocessing import _eeglab_filter
    from handlers_data import _eeglab_init, _eeglab_load_data, _eeglab_save_data


async def _eeglab_qc_report(args: dict) -> Any:
    """Generate a workflow-shaped QC report from the current EEG dataset."""
    steps: list[dict[str, Any]] = []

    info = parse_tool_result(await _eeglab_info({}))
    steps.append(
        {
            "name": "eeglab_info",
            "status": info.get("status", "success"),
            "code": info.get("code"),
        }
    )
    if info.get("status") == "error":
        return structured_payload(
            workflow_error(
                "eeglab_qc_report",
                "eeglab_info",
                info,
                parameters={},
                steps=steps,
            )
        )

    events = parse_tool_result(await _eeglab_get_events({}))
    steps.append(
        {
            "name": "eeglab_get_events",
            "status": events.get("status", "success"),
            "code": events.get("code"),
        }
    )

    history = parse_tool_result(await _eeglab_history({}))
    steps.append(
        {
            "name": "eeglab_history",
            "status": history.get("status", "success"),
            "code": history.get("code"),
        }
    )

    payload = qc_report_from_payloads(info, events, history)
    payload["steps"] = steps
    return structured_payload(payload)


async def _eeglab_workflow_recommend(args: dict) -> Any:
    """Recommend an EEG workflow without changing MATLAB state."""
    return structured_payload(recommend_workflow(args))


async def _eeglab_project_plan(args: dict) -> Any:
    """Create a research-grade project plan without changing MATLAB state."""
    return structured_payload(project_plan(args))


async def _eeglab_protocol_export(args: dict) -> Any:
    """Render and optionally write a reproducible protocol file."""
    try:
        return structured_payload(protocol_export_payload(args))
    except (OSError, ValueError) as exc:
        payload = {
            "status": "error",
            "code": ("protocol_export_failed" if isinstance(exc, OSError) else "invalid_output_path"),
            "error": str(exc),
            "next_step": "Use a writable .md/.json/.txt output_path or omit output_path to receive protocol_text only.",
        }
        return structured_payload(
            workflow_error(
                "eeglab_protocol_export",
                "write_protocol_file",
                payload,
                parameters={
                    "output_path": args.get("output_path", ""),
                    "format": args.get("format", "markdown"),
                },
                steps=[
                    {"name": "render_protocol", "status": "success"},
                    {"name": "write_protocol_file", "status": "error"},
                ],
            )
        )


async def _eeglab_event_semantics_audit(args: dict) -> Any:
    """Classify event roles before epoching."""
    return structured_payload(event_semantics_audit(args))


async def _eeglab_method_preflight(args: dict) -> Any:
    """Evaluate official EEGLAB/SCCN method gates without MATLAB execution."""
    return structured_payload(method_preflight_workflow(args))


async def _eeglab_plugin_check(args: dict) -> Any:
    """Probe local EEGLAB plugin/function availability."""
    requested = args.get("plugins") or list(OFFICIAL_PLUGIN_MATRIX)
    plugins = [str(item).strip() for item in requested if str(item).strip()]
    if not plugins:
        plugins = list(OFFICIAL_PLUGIN_MATRIX)

    matrix_by_lower = {name.lower(): (name, spec) for name, spec in OFFICIAL_PLUGIN_MATRIX.items()}
    matrix_by_lower["bids"] = (
        "EEG-BIDS",
        OFFICIAL_PLUGIN_MATRIX["EEG-BIDS"],
    )
    matrix_by_lower["eeg-bids"] = (
        "EEG-BIDS",
        OFFICIAL_PLUGIN_MATRIX["EEG-BIDS"],
    )
    plugin_aliases = {
        "hed": "HEDTools",
        "hedtools": "HEDTools",
        "fileio": "File-IO",
        "file-io": "File-IO",
        "biosig": "BIOSIG",
        "mff": "MFF-matlab-io",
        "mff-matlab-io": "MFF-matlab-io",
        "nwb": "NWB-io",
        "nwb-io": "NWB-io",
        "bva": "BVA-io",
        "brainvision": "BVA-io",
        "bva-io": "BVA-io",
    }
    for alias, canonical in plugin_aliases.items():
        if canonical in OFFICIAL_PLUGIN_MATRIX:
            matrix_by_lower[alias] = (
                canonical,
                OFFICIAL_PLUGIN_MATRIX[canonical],
            )

    normalized_requests: list[tuple[str, str, dict[str, Any]]] = []
    for plugin in plugins:
        matrix_item = matrix_by_lower.get(plugin.lower())
        if matrix_item:
            canonical, spec = matrix_item
            normalized_requests.append((plugin, canonical, spec))
        else:
            normalized_requests.append(
                (
                    plugin,
                    plugin,
                    {
                        "support_level": "out_of_scope",
                        "functions": [plugin],
                        "claim_ids": [],
                        "dependent_profiles": [],
                        "url": "",
                        "next_step_if_missing": "This plugin is not in the official MCP plugin matrix; add it to the matrix before making support claims.",
                    },
                )
            )

    matlab_checks: list[str] = []
    for requested_name, canonical_name, spec in normalized_requests:
        key = canonical_name.lower().replace("-", "_")
        functions = spec.get("functions", [requested_name])
        function_cell = "{" + ", ".join(matlab_string(fn) for fn in functions) + "}"
        plugin_field = _matlab_identifier(f"plugin_{key}")
        matlab_checks.append(f"""
funcs = {function_cell};
available = false;
found = {{}};
for fi = 1:length(funcs)
    if exist(funcs{{fi}}, 'file') == 2 || exist(funcs{{fi}}, 'file') == 6
        available = true;
        found{{end+1}} = funcs{{fi}};
    end
end
result.plugins.{plugin_field}.requested = {matlab_string(requested_name)};
result.plugins.{plugin_field}.canonical_name = {matlab_string(canonical_name)};
result.plugins.{plugin_field}.functions_checked = funcs;
result.plugins.{plugin_field}.available = available;
result.plugins.{plugin_field}.found_functions = found;
""")

    code = f"""
{_maybe_init()}
result.plugins = struct();
{''.join(matlab_checks)}
result.checked_plugins = fieldnames(result.plugins);
"""

    raw = await matlab.execute(code)
    if raw.get("status") == "error":
        payload = {
            "status": "error",
            "code": raw.get("code", "plugin_check_failed"),
            "error": raw.get("error", "MATLAB/EEGLAB plugin check failed."),
            "next_step": raw.get(
                "next_step",
                "Confirm MATLAB_EXEC works, EEGLAB_PATH is correct, and required plugins are on the EEGLAB path.",
            ),
            "details": raw,
        }
        return structured_payload(
            workflow_error(
                "eeglab_plugin_check",
                "matlab_plugin_probe",
                payload,
                parameters={"plugins": plugins},
                steps=[{"name": "matlab_plugin_probe", "status": "error"}],
            )
        )

    plugin_payload = raw.get("plugins", {})
    matrix_payload: dict[str, Any] = {}
    missing = []
    available = []
    if isinstance(plugin_payload, dict):
        for item in plugin_payload.values():
            if isinstance(item, dict) and item.get("available"):
                available.append(item.get("canonical_name") or item.get("requested"))
            elif isinstance(item, dict):
                missing.append(item.get("canonical_name") or item.get("requested"))
            if isinstance(item, dict):
                canonical_name = str(item.get("canonical_name") or item.get("requested") or "")
                spec = OFFICIAL_PLUGIN_MATRIX.get(canonical_name)
                if not spec and canonical_name.lower() in matrix_by_lower:
                    _, spec = matrix_by_lower[canonical_name.lower()]
                if spec:
                    item.update(
                        {
                            "support_level": spec.get("support_level", ""),
                            "claim_ids": spec.get("claim_ids", []),
                            "dependent_profiles": spec.get("dependent_profiles", []),
                            "official_url": spec.get("url", ""),
                            "next_step_if_missing": (
                                "" if item.get("available") else spec.get("next_step_if_missing", "")
                            ),
                        }
                    )
                matrix_payload[canonical_name] = {
                    "available": bool(item.get("available")),
                    "support_level": item.get("support_level", "out_of_scope"),
                    "claim_ids": item.get("claim_ids", []),
                    "dependent_profiles": item.get("dependent_profiles", []),
                    "functions_checked": item.get("functions_checked", []),
                    "found_functions": item.get("found_functions", []),
                    "next_step_if_missing": item.get("next_step_if_missing", ""),
                }

    return structured_payload(
        workflow_success(
            "eeglab_plugin_check",
            steps=[{"name": "matlab_plugin_probe", "status": "success"}],
            parameters={"plugins": plugins},
            outputs={"plugins": plugin_payload, "plugin_matrix": matrix_payload},
            summary={
                "available": [item for item in available if item],
                "missing": [item for item in missing if item],
                "plugin_dependent_gates": {
                    name: {
                        "support_level": spec.get("support_level", ""),
                        "dependent_profiles": spec.get("dependent_profiles", []),
                        "claim_ids": spec.get("claim_ids", []),
                    }
                    for name, spec in OFFICIAL_PLUGIN_MATRIX.items()
                },
                "recommended_next_step": "Install or add missing executable/gated plugins to the EEGLAB path; keep indexed-only plugins as guidance unless a dedicated workflow exists.",
            },
        )
    )


async def _eeglab_erp_light_workflow(args: dict) -> Any:
    """Run a lightweight ERP workflow and return structured progress/results."""
    steps: list[dict[str, Any]] = []
    try:
        parameters = light_erp_parameters(args)
    except ValueError as exc:
        payload = {
            "status": "error",
            "code": "invalid_output_path",
            "error": str(exc),
            "next_step": "Use output_dir for directories and output_filename for a simple .set filename.",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters={},
                steps=steps,
            )
        )

    data_path = Path(parameters["data_path"])
    output_path = Path(parameters["output_path"])
    if not data_path.exists():
        payload = {
            "status": "error",
            "code": "dataset_not_found",
            "error": f"数据文件不存在: {data_path}",
            "next_step": "传入存在的本地 EEG 数据文件绝对路径。",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters=parameters,
                steps=steps,
            )
        )
    if data_path.resolve() == output_path.resolve():
        payload = {
            "status": "error",
            "code": "refuse_overwrite_input",
            "error": "轻量 ERP workflow 不允许覆盖原始输入数据。",
            "next_step": "把 output_dir 或 output_filename 指向新的临时/结果路径。",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters=parameters,
                steps=steps,
            )
        )

    os.makedirs(parameters["output_dir"], exist_ok=True)

    async def run_step(step_name: str, fn: Any, step_args: dict[str, Any]) -> dict[str, Any]:
        result = parse_tool_result(await fn(step_args))
        steps.append(
            {
                "name": step_name,
                "status": result.get("status", "success"),
                "code": result.get("code"),
            }
        )
        return result

    results: dict[str, dict[str, Any]] = {}
    preflight_steps = [
        ("eeglab_init", _eeglab_init, {}),
        ("eeglab_load_data", _eeglab_load_data, {"filepath": parameters["data_path"]}),
        ("eeglab_info", _eeglab_info, {}),
        ("eeglab_get_events", _eeglab_get_events, {}),
    ]

    for step_name, fn, step_args in preflight_steps:
        result = await run_step(step_name, fn, step_args)
        results[step_name] = result
        if result.get("status") == "error":
            return structured_payload(
                workflow_error(
                    "eeglab_erp_light_workflow",
                    step_name,
                    result,
                    parameters=parameters,
                    steps=steps,
                )
            )

    info_payload = results.get("eeglab_info", {})
    requested_channels = parameters.get("channels", [])
    available_channels = info_payload.get("channel_labels") or []
    if requested_channels and available_channels:
        effective_channels = [channel for channel in requested_channels if channel in available_channels]
        missing_channels = [channel for channel in requested_channels if channel not in available_channels]
        if not effective_channels:
            effective_channels = [available_channels[0]]
            parameters["channel_fallback"] = {
                "requested_channels": requested_channels,
                "effective_channels": effective_channels,
                "missing_channels": missing_channels,
                "reason": "requested channels were not present in the dataset; using the first available channel for smoke-test ERP summary",
            }
    else:
        effective_channels = requested_channels
        missing_channels = []
    parameters["effective_channels"] = effective_channels
    if missing_channels and "channel_fallback" not in parameters:
        parameters["channel_fallback"] = {
            "requested_channels": requested_channels,
            "effective_channels": effective_channels,
            "missing_channels": missing_channels,
            "reason": "some requested channels were not present and were skipped",
        }

    analysis_steps = [
        (
            "eeglab_filter",
            _eeglab_filter,
            {
                "filter_type": "bandpass",
                "low_cutoff": parameters["low_cutoff"],
                "high_cutoff": parameters["high_cutoff"],
            },
        ),
        (
            "eeglab_epoch",
            _eeglab_epoch,
            {
                "event_types": parameters["event_types"],
                "pre_stimulus": parameters["epoch_window"][0],
                "post_stimulus": parameters["epoch_window"][1],
                "baseline_start": parameters["baseline_window"][0] / 1000,
                "baseline_end": parameters["baseline_window"][1] / 1000,
            },
        ),
        (
            "eeglab_erp_analysis",
            _eeglab_erp_analysis,
            {
                "channels": effective_channels,
                "time_window": parameters["time_window"],
                "peak_detection": True,
                "conditions": parameters["event_types"],
            },
        ),
        (
            "eeglab_save_data",
            _eeglab_save_data,
            {"filepath": parameters["output_path"]},
        ),
    ]

    for step_name, fn, step_args in analysis_steps:
        result = await run_step(step_name, fn, step_args)
        results[step_name] = result
        if result.get("status") == "error":
            return structured_payload(
                workflow_error(
                    "eeglab_erp_light_workflow",
                    step_name,
                    result,
                    parameters=parameters,
                    steps=steps,
                )
            )

    save_payload = results.get("eeglab_save_data", {})
    erp_payload = results.get("eeglab_erp_analysis", {})
    events_payload = results.get("eeglab_get_events", {})
    epoch_payload = results.get("eeglab_epoch", {})

    payload = workflow_success(
        "eeglab_erp_light_workflow",
        steps=steps,
        parameters=parameters,
        outputs={
            "processed_set": save_payload.get("saved_path", parameters["output_path"]),
            "processed_fdt": parameters["output_fdt_path"],
            "output_dir": parameters["output_dir"],
            "input_preserved": str(data_path.resolve()) != str(output_path.resolve()),
            "processed_set_exists": output_path.exists(),
            "processed_fdt_exists": Path(parameters["output_fdt_path"]).exists(),
        },
        summary={
            "nbchan": info_payload.get("nbchan"),
            "srate": info_payload.get("srate"),
            "pnts": info_payload.get("pnts"),
            "original_trials": info_payload.get("trials"),
            "num_events": events_payload.get("num_events"),
            "event_types": events_payload.get("event_types"),
            "epoched_trials": epoch_payload.get("trials"),
            "epoch_window_sec": parameters["epoch_window"],
            "baseline_window_ms": parameters["baseline_window"],
            "erp": erp_payload,
        },
    )
    return structured_payload(payload)
