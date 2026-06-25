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


async def _eeglab_generate_report(args: dict) -> Any:
    """Generate a standardized EEG research analysis report."""
    import json
    from datetime import datetime

    output_path = args.get("output_path", "")
    fmt = args.get("format", "markdown")

    if not output_path:
        return structured_payload(
            workflow_error(
                "eeglab_generate_report",
                "validation",
                {
                    "status": "error",
                    "code": "missing_output_path",
                    "error": "output_path is required.",
                    "next_step": "Provide a valid output file path (e.g., /path/to/report.md or /path/to/report.html).",
                },
                parameters=args,
                steps=[],
            )
        )

    # Build report data from args
    title = args.get("title", "EEG Analysis Report")
    date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
    author = args.get("author", "EEGLAB MCP Agent")
    abstract = args.get("abstract", "No abstract provided.")
    recording = args.get("recording", {})
    preprocessing = args.get("preprocessing", {})
    analysis = args.get("analysis", {})
    figures = args.get("figures", [])
    results = args.get("results", {})
    discussion = args.get("discussion", "No discussion provided.")
    limitations = args.get("limitations", [])
    gate_results = args.get("gate_results", {})
    override_used = args.get("override_used", False)
    override_reason = args.get("override_reason", "")
    appendix = args.get("appendix", {})

    if fmt == "html":
        report = _generate_html_report(
            title, date, author, abstract, recording, preprocessing,
            analysis, figures, results, discussion, limitations,
            gate_results, override_used, override_reason, appendix
        )
    else:
        report = _generate_markdown_report(
            title, date, author, abstract, recording, preprocessing,
            analysis, figures, results, discussion, limitations,
            gate_results, override_used, override_reason, appendix
        )

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        return structured_payload(
            workflow_success(
                "eeglab_generate_report",
                steps=[{"name": "generate_report", "status": "success"}],
                parameters={"output_path": output_path, "format": fmt},
                outputs={"report_path": output_path, "format": fmt},
                summary={"report_generated": True},
            )
        )
    except OSError as exc:
        return structured_payload(
            workflow_error(
                "eeglab_generate_report",
                "write_file",
                {
                    "status": "error",
                    "code": "write_failed",
                    "error": str(exc),
                    "next_step": "Check the output path is writable and the directory exists.",
                },
                parameters={"output_path": output_path, "format": fmt},
                steps=[{"name": "generate_report", "status": "success"}, {"name": "write_file", "status": "error"}],
            )
        )


def _generate_markdown_report(
    title, date, author, abstract, recording, preprocessing,
    analysis, figures, results, discussion, limitations,
    gate_results, override_used, override_reason, appendix
) -> str:
    """Generate Markdown report."""
    sections = []

    # Title
    sections.append(f"# {title}\n\n**Date:** {date}\n**Author:** {author}\n**Software:** EEGLAB MCP Agent")

    # Abstract
    sections.append(f"## Abstract\n\n{abstract}")

    # Recording
    if recording:
        lines = ["## Recording And Acquisition\n", "| Parameter | Value |", "|-----------|-------|"]
        for key, value in recording.items():
            label = key.replace("_", " ").title()
            lines.append(f"| {label} | {value} |")
        sections.append("\n".join(lines))

    # Preprocessing
    if preprocessing:
        lines = ["## Preprocessing Parameters\n", "| Step | Parameters |", "|------|------------|"]
        for key, value in preprocessing.items():
            label = key.replace("_", " ").title()
            if isinstance(value, dict):
                value = ", ".join(f"{k}: {v}" for k, v in value.items())
            lines.append(f"| {label} | {value} |")
        sections.append("\n".join(lines))

    # Analysis
    if any(analysis.values()):
        lines = ["## Analysis Parameters\n"]
        for analysis_type, params in analysis.items():
            if params:
                lines.append(f"### {analysis_type.replace('_', ' ').title()}\n")
                lines.append("| Parameter | Value |")
                lines.append("|-----------|-------|")
                for key, value in params.items():
                    lines.append(f"| {key} | {value} |")
                lines.append("")
        sections.append("\n".join(lines))

    # Figures
    if figures:
        lines = ["## Figures\n"]
        for i, fig in enumerate(figures, 1):
            fig_path = fig.get("path", "")
            fig_caption = fig.get("caption", f"Figure {i}")
            fig_description = fig.get("description", "")
            lines.append(f"### Figure {i}: {fig_caption}\n")
            if fig_description:
                lines.append(f"{fig_description}\n")
            if fig_path:
                lines.append(f"![{fig_caption}]({fig_path})\n")
        sections.append("\n".join(lines))

    # Results
    if results:
        lines = ["## Results\n"]
        for key, value in results.items():
            lines.append(f"### {key.replace('_', ' ').title()}\n")
            if isinstance(value, dict):
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                for k, v in value.items():
                    lines.append(f"| {k} | {v} |")
            else:
                lines.append(str(value))
            lines.append("")
        sections.append("\n".join(lines))

    # Discussion
    sections.append(f"## Discussion\n\n{discussion}")

    # Limitations
    lines = ["## Limitations\n"]
    if limitations:
        for lim in limitations:
            lines.append(f"- {lim}")
    else:
        lines.append("- No specific limitations noted.")
    lines.append("")
    lines.append("**Official Gate Status:**\n")
    if gate_results:
        for claim_id, status in gate_results.items():
            lines.append(f"- {claim_id}: {status}")
    else:
        lines.append("- Gate coverage not provided.")
    if override_used:
        lines.append(f"\n**Override Applied:**\n\n- Reason: {override_reason}")
    lines.append("\n**Disclaimer:** These are EEG signal-processing results, not clinical conclusions. No anatomical certainty is claimed from missing montage/model data.")
    sections.append("\n".join(lines))

    # Appendix
    lines = ["## Appendix\n"]
    software = appendix.get("software", {})
    if software:
        lines.append("### Software And Versions\n")
        for key, value in software.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    plugins = appendix.get("plugins", {})
    if plugins:
        lines.append("### Plugin Status\n")
        for plugin, status in plugins.items():
            lines.append(f"- **{plugin}:** {status}")
        lines.append("")
    files = appendix.get("generated_files", [])
    if files:
        lines.append("### Generated Files\n")
        for file_info in files:
            if isinstance(file_info, dict):
                lines.append(f"- `{file_info.get('path', 'N/A')}`: {file_info.get('description', '')}")
            else:
                lines.append(f"- `{file_info}`")
        lines.append("")
    sections.append("\n".join(lines))

    return "\n\n".join(sections)


def _generate_html_report(
    title, date, author, abstract, recording, preprocessing,
    analysis, figures, results, discussion, limitations,
    gate_results, override_used, override_reason, appendix
) -> str:
    """Generate HTML report with proper formatting."""
    sections = []

    # Title
    sections.append(f"""<h1>{title}</h1>
<p><strong>Date:</strong> {date}<br>
<strong>Author:</strong> {author}<br>
<strong>Software:</strong> EEGLAB MCP Agent</p>""")

    # Abstract
    sections.append(f"<h2>Abstract</h2><p>{abstract}</p>")

    # Recording
    if recording:
        sections.append("<h2>Recording And Acquisition</h2>")
        sections.append("<table><tr><th>Parameter</th><th>Value</th></tr>")
        for key, value in recording.items():
            label = key.replace("_", " ").title()
            sections.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
        sections.append("</table>")

    # Preprocessing
    if preprocessing:
        sections.append("<h2>Preprocessing Parameters</h2>")
        sections.append("<table><tr><th>Step</th><th>Parameters</th></tr>")
        for key, value in preprocessing.items():
            label = key.replace("_", " ").title()
            if isinstance(value, dict):
                value = ", ".join(f"{k}: {v}" for k, v in value.items())
            sections.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
        sections.append("</table>")

    # Analysis
    if any(analysis.values()):
        sections.append("<h2>Analysis Parameters</h2>")
        for analysis_type, params in analysis.items():
            if params:
                sections.append(f"<h3>{analysis_type.replace('_', ' ').title()}</h3>")
                sections.append("<table><tr><th>Parameter</th><th>Value</th></tr>")
                for key, value in params.items():
                    sections.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
                sections.append("</table>")

    # Figures
    if figures:
        sections.append("<h2>Figures</h2>")
        for i, fig in enumerate(figures, 1):
            fig_path = fig.get("path", "")
            fig_caption = fig.get("caption", f"Figure {i}")
            fig_description = fig.get("description", "")
            sections.append(f"<h3>Figure {i}: {fig_caption}</h3>")
            if fig_description:
                sections.append(f"<p>{fig_description}</p>")
            if fig_path:
                sections.append(f'<img src="{fig_path}" alt="{fig_caption}" style="max-width: 100%;">')

    # Results
    if results:
        sections.append("<h2>Results</h2>")
        for key, value in results.items():
            sections.append(f"<h3>{key.replace('_', ' ').title()}</h3>")
            if isinstance(value, dict):
                sections.append("<table><tr><th>Metric</th><th>Value</th></tr>")
                for k, v in value.items():
                    sections.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
                sections.append("</table>")
            else:
                sections.append(f"<p>{value}</p>")

    # Discussion
    sections.append(f"<h2>Discussion</h2><p>{discussion}</p>")

    # Limitations
    sections.append("<h2>Limitations</h2><ul>")
    if limitations:
        for lim in limitations:
            sections.append(f"<li>{lim}</li>")
    else:
        sections.append("<li>No specific limitations noted.</li>")
    sections.append("</ul>")
    sections.append("<p><strong>Official Gate Status:</strong></p><ul>")
    if gate_results:
        for claim_id, status in gate_results.items():
            sections.append(f"<li>{claim_id}: {status}</li>")
    else:
        sections.append("<li>Gate coverage not provided.</li>")
    sections.append("</ul>")
    if override_used:
        sections.append(f"<p><strong>Override Applied:</strong></p><p>Reason: {override_reason}</p>")
    sections.append('<p><strong>Disclaimer:</strong> These are EEG signal-processing results, not clinical conclusions. No anatomical certainty is claimed from missing montage/model data.</p>')

    # Appendix
    sections.append("<h2>Appendix</h2>")
    software = appendix.get("software", {})
    if software:
        sections.append("<h3>Software And Versions</h3><ul>")
        for key, value in software.items():
            sections.append(f"<li><strong>{key}:</strong> {value}</li>")
        sections.append("</ul>")
    plugins = appendix.get("plugins", {})
    if plugins:
        sections.append("<h3>Plugin Status</h3><ul>")
        for plugin, status in plugins.items():
            sections.append(f"<li><strong>{plugin}:</strong> {status}</li>")
        sections.append("</ul>")
    files = appendix.get("generated_files", [])
    if files:
        sections.append("<h3>Generated Files</h3><ul>")
        for file_info in files:
            if isinstance(file_info, dict):
                sections.append(f"<li><code>{file_info.get('path', 'N/A')}</code>: {file_info.get('description', '')}</li>")
            else:
                sections.append(f"<li><code>{file_info}</code></li>")
        sections.append("</ul>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; margin: 20px 0; display: block; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
{"".join(sections)}
</body>
</html>"""
