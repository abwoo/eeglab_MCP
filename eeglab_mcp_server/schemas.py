"""Tool schema metadata and validation helpers for EEGLAB MCP."""

from __future__ import annotations

import math
from typing import Any

from mcp.types import Tool, ToolAnnotations


REQUIRED_ARGUMENTS: dict[str, list[str]] = {
    "eeglab_load_data": ["filepath"],
    "eeglab_save_data": ["filepath"],
    "eeglab_import_bids": ["bids_path"],
    "eeglab_filter": ["filter_type"],
    "eeglab_resample": ["new_srate"],
    "eeglab_reref": ["ref_type"],
    "eeglab_edit_channels": ["action"],
    "eeglab_sort_epochs": ["sort_by"],
    "eeglab_topoplot": ["output_path"],
    "eeglab_plot_erp": ["channels", "output_path"],
    "eeglab_plot_timefreq": ["channel", "output_path"],
    "eeglab_plot_components": ["output_path"],
    "eeglab_pipeline": ["pipeline_type", "data_path"],
    "eeglab_erp_light_workflow": ["data_path", "output_dir"],
}


WORKFLOW_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "workflow": {"type": "string"},
        "steps": {"type": "array"},
        "parameters": {"type": "object"},
        "outputs": {"type": "object"},
        "summary": {"type": "object"},
        "limitations": {"type": "array"},
    },
    "required": ["status", "workflow", "steps", "parameters", "outputs", "summary", "limitations"],
}


def workflow_tools() -> list[Tool]:
    """Return high-level research workflow tools."""
    return [
        Tool(
            name="eeglab_qc_report",
            title="EEGLAB QC Report",
            description=(
                "Generate a lightweight quality-control report for the currently loaded EEG dataset. "
                "Use after eeglab_load_data to summarize recording dimensions, event provenance, channel-location "
                "coverage, ICA status, processing history, and basic risks before choosing preprocessing steps. "
                "This tool does not transform data."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="QC report",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_erp_light_workflow",
            title="EEGLAB Light ERP Workflow",
            description=(
                "Run a conservative light ERP workflow on a local dataset: load, inspect, filter, epoch, "
                "compute ERP summary, and save a processed copy. Use this for smoke-tested ERP preprocessing "
                "when you need explicit parameters and temp/output files. It modifies only the in-memory EEG "
                "state and writes to the requested output directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {"type": "string", "description": "Input EEG dataset path, usually a .set file."},
                    "output_dir": {"type": "string", "description": "Directory for processed output files."},
                    "low_cutoff": {"type": "number", "default": 0.5, "description": "Bandpass low cutoff in Hz."},
                    "high_cutoff": {"type": "number", "default": 40.0, "description": "Bandpass high cutoff in Hz."},
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["target", "standard"],
                        "description": "Event labels to epoch around.",
                    },
                    "epoch_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-0.2, 0.8],
                        "description": "Epoch window in seconds.",
                    },
                    "baseline_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-200, 0],
                        "description": "Baseline window in milliseconds.",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["Cz"],
                        "description": "Channels for ERP summary.",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [250, 450],
                        "description": "ERP summary window in milliseconds.",
                    },
                    "output_filename": {
                        "type": "string",
                        "default": "light_erp_processed.set",
                        "description": "Processed .set filename to write inside output_dir.",
                    },
                },
                "required": ["data_path", "output_dir"],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Light ERP workflow",
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_workflow_recommend",
            title="EEGLAB Workflow Recommendation",
            description=(
                "Recommend EEG analysis steps from analysis type, event labels, sampling rate, ICA state, "
                "data shape, and channel-location availability. Use this before destructive preprocessing "
                "when the user wants a reproducible research plan that records acquisition/provenance, "
                "processing choices, and analysis outputs. This tool does not run MATLAB or change data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["auto", "erp", "resting", "timefreq", "ica", "study", "source"],
                        "description": "Target analysis family. Use auto when the user has not specified a goal; the tool will infer a conservative first-pass branch.",
                    },
                    "research_goal": {
                        "type": "string",
                        "description": "User-stated research goal, hypothesis, or analysis question. Leave blank only when it is genuinely unknown.",
                    },
                    "project_scale": {
                        "type": "string",
                        "enum": ["unknown", "single_subject", "multi_subject", "bids_study", "exploratory_qc"],
                        "description": "Expected study scale and organization.",
                    },
                    "stage": {
                        "type": "string",
                        "enum": ["planning", "inspection", "preprocessing", "analysis", "group", "reporting"],
                        "description": "Current project stage so the recommendation can emphasize the right QC gate.",
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known event labels, if available.",
                    },
                    "srate": {"type": "number", "description": "Sampling rate in Hz, if known."},
                    "has_ica": {"type": "boolean", "description": "Whether ICA weights already exist."},
                    "data_shape": {
                        "type": "string",
                        "enum": ["continuous_or_single_trial", "epoched"],
                        "description": "Whether the loaded data appears continuous/single-trial or already epoched.",
                    },
                    "has_channel_locations": {
                        "type": "boolean",
                        "description": "Whether all channels have usable location metadata for topography/source workflows.",
                    },
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Workflow recommendation",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        ),
    ]


TOOL_TITLES: dict[str, str] = {
    "eeglab_init": "Initialize EEGLAB",
    "eeglab_load_data": "Load EEG Data",
    "eeglab_save_data": "Save EEG Data",
    "eeglab_info": "Inspect EEG Metadata",
    "eeglab_history": "Read EEG History",
    "eeglab_filter": "Filter EEG",
    "eeglab_epoch": "Epoch EEG",
    "eeglab_erp_analysis": "ERP Analysis",
    "eeglab_get_events": "Inspect Events",
    "eeglab_pipeline": "Run Pipeline",
}

READ_ONLY_TOOLS = {
    "eeglab_info",
    "eeglab_history",
    "eeglab_get_events",
    "eeglab_workflow_recommend",
    "eeglab_qc_report",
}

DESTRUCTIVE_TOOLS = {
    "eeglab_filter",
    "eeglab_resample",
    "eeglab_reref",
    "eeglab_select_channels",
    "eeglab_interpolate_channels",
    "eeglab_edit_channels",
    "eeglab_clean_line_noise",
    "eeglab_clean_rawdata",
    "eeglab_remove_components",
    "eeglab_reject_epochs",
    "eeglab_epoch",
    "eeglab_pipeline",
}


def annotate_tools(tools: list[Tool]) -> list[Tool]:
    """Add MCP title/annotation metadata without changing tool names."""
    for tool in tools:
        tool.title = tool.title or TOOL_TITLES.get(tool.name, tool.name.replace("_", " ").title())
        if tool.annotations is None:
            read_only = tool.name in READ_ONLY_TOOLS
            tool.annotations = ToolAnnotations(
                title=tool.title,
                readOnlyHint=read_only,
                destructiveHint=tool.name in DESTRUCTIVE_TOOLS,
                idempotentHint=read_only,
                openWorldHint=False,
            )
    return tools


def missing_required(name: str, arguments: dict[str, Any]) -> list[str]:
    """Check required arguments controlled by the server rather than SDK validation."""
    missing: list[str] = []
    for field in REQUIRED_ARGUMENTS.get(name, []):
        value = arguments.get(field)
        if field not in arguments or value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def json_type_matches(value: Any, schema_type: str) -> bool:
    """Check a small JSON Schema type subset used by this server."""
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    return True


def _is_blank(value: Any) -> bool:
    """Return whether a supplied argument is unusably empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _is_present(arguments: dict[str, Any], field: str) -> bool:
    return field in arguments and not _is_blank(arguments[field])


def _require_present(arguments: dict[str, Any], field: str, message: str, errors: list[str]) -> None:
    if not _is_present(arguments, field):
        errors.append(message)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _positive_number(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field in arguments and arguments[field] is not None:
        value = arguments[field]
        if not _finite_number(value) or value <= 0:
            errors.append(f"{field} 必须是大于 0 的有限数值")


def _probability(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field in arguments and arguments[field] is not None:
        value = arguments[field]
        if not _finite_number(value) or value < 0 or value > 1:
            errors.append(f"{field} 必须在 0 到 1 之间")


def _ascending_pair(
    arguments: dict[str, Any],
    field: str,
    errors: list[str],
    *,
    allow_equal: bool = False,
) -> None:
    if field not in arguments or arguments[field] is None:
        return
    value = arguments[field]
    if not isinstance(value, list) or len(value) != 2:
        return
    first, second = value
    if not (_finite_number(first) and _finite_number(second)):
        errors.append(f"{field} 必须只包含有限数值")
    elif allow_equal:
        if first > second:
            errors.append(f"{field} 起始值必须小于或等于结束值")
    elif first >= second:
        errors.append(f"{field} 起始值必须小于结束值")


def _probability_pair(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in arguments or arguments[field] is None:
        return
    value = arguments[field]
    if not isinstance(value, list) or len(value) != 2:
        return
    _ascending_pair(arguments, field, errors, allow_equal=True)
    if all(_finite_number(item) for item in value) and (value[0] < 0 or value[1] > 1):
        errors.append(f"{field} 概率范围必须在 0 到 1 之间")


def _positive_integer_list(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in arguments or arguments[field] is None:
        return
    value = arguments[field]
    if not isinstance(value, list):
        return
    bad = [item for item in value if not isinstance(item, int) or isinstance(item, bool) or item < 1]
    if bad:
        errors.append(f"{field} 的索引必须是从 1 开始的正整数")


def _positive_integer(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field in arguments and arguments[field] is not None:
        value = arguments[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            errors.append(f"{field} 必须是大于 0 的整数")


def _string_mapping(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in arguments or arguments[field] is None:
        return
    value = arguments[field]
    if not isinstance(value, dict):
        return
    bad = [key for key, mapped in value.items() if _is_blank(key) or _is_blank(mapped)]
    if bad:
        errors.append(f"{field} 必须是非空字符串到非空字符串的映射")


def _safe_leaf_filename(arguments: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in arguments or arguments[field] is None:
        return
    filename = str(arguments[field]).strip()
    if not filename:
        errors.append(f"{field} 不能为空")
        return
    if filename in {".", ".."} or any(separator in filename for separator in ("/", "\\")) or ":" in filename:
        errors.append(f"{field} 只能是输出目录内的文件名，不能包含目录、驱动器或路径分隔符")


def validate_arguments(schema: dict[str, Any], arguments: dict[str, Any]) -> list[str]:
    """Validate the schema subset that matters before generating MATLAB code."""
    errors: list[str] = []
    properties = schema.get("properties", {})

    for field, field_schema in properties.items():
        if field not in arguments or arguments[field] is None:
            continue

        value = arguments[field]
        schema_type = field_schema.get("type")
        if schema_type and not json_type_matches(value, schema_type):
            errors.append(f"{field} 必须是 {schema_type}")
            continue
        if schema_type in {"number", "integer"} and not _finite_number(value):
            errors.append(f"{field} 必须是有限数值")
            continue

        enum_values = field_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"{field} 必须是以下值之一: {', '.join(map(str, enum_values))}")

        minimum = field_schema.get("minimum")
        if minimum is not None and _finite_number(value) and value < minimum:
            errors.append(f"{field} 必须大于或等于 {minimum}")
        maximum = field_schema.get("maximum")
        if maximum is not None and _finite_number(value) and value > maximum:
            errors.append(f"{field} 必须小于或等于 {maximum}")
        exclusive_minimum = field_schema.get("exclusiveMinimum")
        if exclusive_minimum is not None and _finite_number(value) and value <= exclusive_minimum:
            errors.append(f"{field} 必须大于 {exclusive_minimum}")
        exclusive_maximum = field_schema.get("exclusiveMaximum")
        if exclusive_maximum is not None and _finite_number(value) and value >= exclusive_maximum:
            errors.append(f"{field} 必须小于 {exclusive_maximum}")

        if schema_type == "array" and isinstance(value, list):
            min_items = field_schema.get("minItems")
            max_items = field_schema.get("maxItems")
            if min_items is not None and len(value) < min_items:
                errors.append(f"{field} 至少需要 {min_items} 个元素")
            if max_items is not None and len(value) > max_items:
                errors.append(f"{field} 最多允许 {max_items} 个元素")

            item_type = field_schema.get("items", {}).get("type")
            if item_type:
                bad_items = [item for item in value if not json_type_matches(item, item_type)]
                if bad_items:
                    errors.append(f"{field} 的所有元素必须是 {item_type}")

    return errors


def validate_tool_contracts(name: str, arguments: dict[str, Any]) -> list[str]:
    """Validate cross-field tool contracts that JSON Schema cannot express here."""
    errors: list[str] = []

    if name == "eeglab_filter":
        filter_type = arguments.get("filter_type")
        if filter_type == "bandpass":
            _require_present(arguments, "low_cutoff", "bandpass 需要 low_cutoff", errors)
            _require_present(arguments, "high_cutoff", "bandpass 需要 high_cutoff", errors)
        elif filter_type == "highpass":
            _require_present(arguments, "low_cutoff", "highpass 需要 low_cutoff", errors)
        elif filter_type == "lowpass":
            _require_present(arguments, "high_cutoff", "lowpass 需要 high_cutoff", errors)
        elif filter_type == "notch":
            _require_present(arguments, "notch_freq", "notch 需要 notch_freq", errors)
        for field in ("low_cutoff", "high_cutoff", "notch_freq"):
            _positive_number(arguments, field, errors)
        if _is_present(arguments, "low_cutoff") and _is_present(arguments, "high_cutoff"):
            if arguments["low_cutoff"] >= arguments["high_cutoff"]:
                errors.append("low_cutoff 必须小于 high_cutoff")

    elif name == "eeglab_resample":
        _positive_number(arguments, "new_srate", errors)

    elif name == "eeglab_reref":
        if arguments.get("ref_type") == "channel":
            _require_present(arguments, "ref_channel", "ref_type 为 channel 时需要 ref_channel", errors)

    elif name == "eeglab_select_channels":
        has_channels = _is_present(arguments, "channels")
        has_exclude = _is_present(arguments, "exclude_channels")
        if has_channels == has_exclude:
            errors.append("channels 和 exclude_channels 必须且只能指定一个")

    elif name == "eeglab_edit_channels":
        action = arguments.get("action")
        if action == "load_loc":
            _require_present(arguments, "loc_file", "action 为 load_loc 时需要 loc_file", errors)
        elif action == "rename":
            _require_present(arguments, "rename_map", "action 为 rename 时需要 rename_map", errors)
            _string_mapping(arguments, "rename_map", errors)

    elif name == "eeglab_run_ica":
        _positive_integer(arguments, "pca_components", errors)
        _positive_integer(arguments, "max_steps", errors)

    elif name == "eeglab_flag_components":
        for field in (
            "brain_range",
            "muscle_range",
            "eye_range",
            "heart_range",
            "line_noise_range",
            "channel_noise_range",
            "other_range",
        ):
            _probability_pair(arguments, field, errors)

    elif name == "eeglab_remove_components":
        has_indices = _is_present(arguments, "component_indices")
        has_threshold = _is_present(arguments, "auto_remove_brain_threshold")
        if has_indices == has_threshold:
            errors.append("component_indices 和 auto_remove_brain_threshold 必须且只能指定一个")
        _positive_integer_list(arguments, "component_indices", errors)
        _probability(arguments, "auto_remove_brain_threshold", errors)

    elif name == "eeglab_reject_epochs":
        _ascending_pair(arguments, "threshold", errors)
        _positive_number(arguments, "jp_threshold", errors)

    elif name == "eeglab_erp_analysis":
        _ascending_pair(arguments, "time_window", errors)

    elif name == "eeglab_spectral":
        _ascending_pair(arguments, "freq_range", errors)

    elif name == "eeglab_timefreq":
        _ascending_pair(arguments, "freq_range", errors)
        _ascending_pair(arguments, "baseline", errors, allow_equal=True)

    elif name == "eeglab_connectivity":
        _ascending_pair(arguments, "freq_range", errors)

    elif name == "eeglab_topoplot":
        if _is_present(arguments, "time_point") and _is_present(arguments, "time_window"):
            errors.append("time_point 和 time_window 只能指定一个")
        _ascending_pair(arguments, "time_window", errors)

    elif name == "eeglab_study_create":
        has_bids = _is_present(arguments, "bids_path")
        has_datasets = _is_present(arguments, "dataset_paths")
        if has_bids == has_datasets:
            errors.append("bids_path 和 dataset_paths 必须且只能指定一个")

    elif name == "eeglab_study_statistics":
        _probability(arguments, "alpha", errors)

    elif name == "eeglab_workflow_recommend":
        _positive_number(arguments, "srate", errors)

    elif name in {"eeglab_pipeline", "eeglab_erp_light_workflow"}:
        highpass_field = "highpass" if name == "eeglab_pipeline" else "low_cutoff"
        lowpass_field = "lowpass" if name == "eeglab_pipeline" else "high_cutoff"
        _positive_number(arguments, highpass_field, errors)
        _positive_number(arguments, lowpass_field, errors)
        if _is_present(arguments, highpass_field) and _is_present(arguments, lowpass_field):
            if arguments[highpass_field] >= arguments[lowpass_field]:
                errors.append(f"{highpass_field} 必须小于 {lowpass_field}")
        _ascending_pair(arguments, "epoch_window", errors)
        _ascending_pair(arguments, "baseline_window", errors, allow_equal=True)
        if name == "eeglab_erp_light_workflow":
            if "event_types" in arguments and _is_present(arguments, "event_types") is False:
                errors.append("eeglab_erp_light_workflow 需要至少一个 event_types 值")
            if "channels" in arguments and _is_present(arguments, "channels") is False:
                errors.append("eeglab_erp_light_workflow 需要至少一个 channels 值")
            _ascending_pair(arguments, "time_window", errors)
            _safe_leaf_filename(arguments, "output_filename", errors)
        else:
            _positive_number(arguments, "burst_criterion", errors)

    return errors


def validate_analysis_windows(
    *,
    epoch_window: list[Any] | None = None,
    baseline_window_ms: list[Any] | None = None,
    time_window_ms: list[Any] | None = None,
) -> list[str]:
    """Validate common EEG analysis windows."""
    errors: list[str] = []
    if epoch_window is not None:
        if len(epoch_window) != 2:
            errors.append("epoch_window 必须包含 2 个元素")
        elif epoch_window[0] >= epoch_window[1]:
            errors.append("epoch_window 起始值必须小于结束值")

    if baseline_window_ms is not None:
        if len(baseline_window_ms) != 2:
            errors.append("baseline_window 必须包含 2 个元素")
        elif baseline_window_ms[0] > baseline_window_ms[1]:
            errors.append("baseline_window 起始值必须小于或等于结束值")
        elif epoch_window is not None and len(epoch_window) == 2:
            epoch_ms = [epoch_window[0] * 1000, epoch_window[1] * 1000]
            if baseline_window_ms[0] < epoch_ms[0] or baseline_window_ms[1] > epoch_ms[1]:
                errors.append("baseline_window 必须落在 epoch_window 范围内")

    if time_window_ms is not None:
        if len(time_window_ms) != 2:
            errors.append("time_window 必须包含 2 个元素")
        elif time_window_ms[0] >= time_window_ms[1]:
            errors.append("time_window 起始值必须小于结束值")

    return errors


def client_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return schema for MCP clients while keeping strict checks in call_tool."""
    cleaned = dict(schema)
    properties = {}
    for name, prop_schema in schema.get("properties", {}).items():
        prop = dict(prop_schema)
        prop.pop("type", None)
        prop.pop("items", None)
        prop.pop("enum", None)
        prop.pop("minItems", None)
        prop.pop("maxItems", None)
        properties[name] = prop
    cleaned["properties"] = properties
    cleaned["required"] = []
    return cleaned
