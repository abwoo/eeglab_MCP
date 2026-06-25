"""Central tool registry metadata for the EEGLAB MCP server.

This module is intentionally lightweight: it owns stable tool identity and
research metadata, while the executable MCP ``Tool`` schemas still live beside
their current handlers until the server is decomposed further.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

try:
    from .official_alignment import TOOL_TO_PROFILE
except ImportError:  # pragma: no cover - direct script execution support
    from official_alignment import TOOL_TO_PROFILE


LEGACY_LOW_LEVEL_COUNT = 39
RESEARCH_WORKFLOW_COUNT = 9
TOTAL_EXPOSED_TOOL_COUNT = LEGACY_LOW_LEVEL_COUNT + RESEARCH_WORKFLOW_COUNT


@dataclass(frozen=True)
class ToolSpec:
    """Stable identity and research-policy metadata for one MCP tool."""

    name: str
    category: str
    handler: str
    input_schema: str
    output_schema: str
    annotations: str
    risk_level: str
    method_profile: str
    eeglab_function_family: str
    read_write_effect: str
    docs_id: str
    eval_ids: tuple[str, ...] = ()


def _risk(name: str, default: str = "standard") -> str:
    return "high" if name in TOOL_TO_PROFILE else default


def _profile(name: str) -> str:
    return TOOL_TO_PROFILE.get(name, "")


def _spec(
    name: str,
    category: str,
    handler: str,
    *,
    eeglab_function_family: str,
    read_write_effect: str,
    docs_id: str,
    eval_ids: Iterable[str] = (),
    risk_level: str | None = None,
    output_schema: str = "tool_definition",
    annotations: str = "tool_definition",
) -> ToolSpec:
    return ToolSpec(
        name=name,
        category=category,
        handler=handler,
        input_schema="tool_definition",
        output_schema=output_schema,
        annotations=annotations,
        risk_level=risk_level or _risk(name),
        method_profile=_profile(name),
        eeglab_function_family=eeglab_function_family,
        read_write_effect=read_write_effect,
        docs_id=docs_id,
        eval_ids=tuple(eval_ids),
    )


LEGACY_LOW_LEVEL_TOOL_SPECS: tuple[ToolSpec, ...] = (
    _spec(
        "eeglab_init",
        "data",
        "_eeglab_init",
        eeglab_function_family="eeglab/addpath",
        read_write_effect="initializes MATLAB/EEGLAB session state",
        docs_id="tools:data",
        eval_ids=("1",),
    ),
    _spec(
        "eeglab_load_data",
        "data",
        "_eeglab_load_data",
        eeglab_function_family="pop_loadset/pop_biosig/import",
        read_write_effect="loads EEG into MCP MATLAB state",
        docs_id="tools:data",
        eval_ids=("1", "4"),
    ),
    _spec(
        "eeglab_save_data",
        "data",
        "_eeglab_save_data",
        eeglab_function_family="pop_saveset",
        read_write_effect="writes derivative .set output",
        docs_id="tools:data",
        eval_ids=("5",),
    ),
    _spec(
        "eeglab_import_bids",
        "study",
        "_eeglab_import_bids",
        eeglab_function_family="pop_importbids/STUDY",
        read_write_effect="loads BIDS/STUDY state",
        docs_id="tools:study",
        eval_ids=("8", "14"),
    ),
    _spec(
        "eeglab_info",
        "data",
        "_eeglab_info",
        eeglab_function_family="EEG structure inspection/eeg_checkset",
        read_write_effect="read-only recording metadata",
        docs_id="tools:data",
        eval_ids=("1", "11"),
    ),
    _spec(
        "eeglab_history",
        "data",
        "_eeglab_history",
        eeglab_function_family="EEG.history",
        read_write_effect="read-only provenance inspection",
        docs_id="tools:data",
        eval_ids=("1", "47"),
    ),
    _spec(
        "eeglab_filter",
        "preprocessing",
        "_eeglab_filter",
        eeglab_function_family="pop_eegfiltnew/pop_cleanline",
        read_write_effect="modifies EEG signal in memory",
        docs_id="tools:preprocessing",
        eval_ids=("2", "3"),
    ),
    _spec(
        "eeglab_resample",
        "preprocessing",
        "_eeglab_resample",
        eeglab_function_family="pop_resample",
        read_write_effect="modifies EEG sampling/data points in memory",
        docs_id="tools:preprocessing",
    ),
    _spec(
        "eeglab_reref",
        "preprocessing",
        "_eeglab_reref",
        eeglab_function_family="pop_reref",
        read_write_effect="modifies EEG reference/rank in memory",
        docs_id="tools:preprocessing",
        eval_ids=("2", "3"),
    ),
    _spec(
        "eeglab_select_channels",
        "preprocessing",
        "_eeglab_select_channels",
        eeglab_function_family="pop_select",
        read_write_effect="modifies channel set in memory",
        docs_id="tools:preprocessing",
    ),
    _spec(
        "eeglab_interpolate_channels",
        "preprocessing",
        "_eeglab_interpolate_channels",
        eeglab_function_family="pop_interp",
        read_write_effect="modifies channel data in memory",
        docs_id="tools:preprocessing",
    ),
    _spec(
        "eeglab_edit_channels",
        "preprocessing",
        "_eeglab_edit_channels",
        eeglab_function_family="pop_chanedit/channel metadata",
        read_write_effect="modifies channel metadata in memory",
        docs_id="tools:preprocessing",
        eval_ids=("27",),
    ),
    _spec(
        "eeglab_clean_line_noise",
        "preprocessing",
        "_eeglab_clean_line_noise",
        eeglab_function_family="cleanline/line-noise cleanup",
        read_write_effect="modifies EEG signal in memory",
        docs_id="tools:preprocessing",
        eval_ids=("2", "3", "28", "38"),
    ),
    _spec(
        "eeglab_clean_rawdata",
        "preprocessing",
        "_eeglab_clean_rawdata",
        eeglab_function_family="pop_clean_rawdata/ASR",
        read_write_effect="modifies EEG signal/channel segments in memory",
        docs_id="tools:preprocessing",
        eval_ids=("3", "15", "19"),
    ),
    _spec(
        "eeglab_run_ica",
        "ica_artifact",
        "_eeglab_run_ica",
        eeglab_function_family="pop_runica",
        read_write_effect="adds ICA weights to EEG state",
        docs_id="tools:ica",
        eval_ids=("5", "9"),
    ),
    _spec(
        "eeglab_classify_ica",
        "ica_artifact",
        "_eeglab_classify_ica",
        eeglab_function_family="pop_iclabel/ICLabel",
        read_write_effect="adds ICLabel classifications to EEG state",
        docs_id="tools:ica",
        eval_ids=("5", "15"),
    ),
    _spec(
        "eeglab_flag_components",
        "ica_artifact",
        "_eeglab_flag_components",
        eeglab_function_family="pop_icflag/ICLabel",
        read_write_effect="adds component rejection flags",
        docs_id="tools:ica",
        eval_ids=("5",),
    ),
    _spec(
        "eeglab_remove_components",
        "ica_artifact",
        "_eeglab_remove_components",
        eeglab_function_family="pop_subcomp",
        read_write_effect="removes ICA components from EEG data in memory",
        docs_id="tools:ica",
        eval_ids=("5",),
    ),
    _spec(
        "eeglab_reject_epochs",
        "events_erp",
        "_eeglab_reject_epochs",
        eeglab_function_family="pop_eegthresh/pop_rejtrend",
        read_write_effect="removes or flags epochs in memory",
        docs_id="tools:erp",
    ),
    _spec(
        "eeglab_get_events",
        "events_erp",
        "_eeglab_get_events",
        eeglab_function_family="EEG.event/EEG.urevent",
        read_write_effect="read-only event inspection",
        docs_id="tools:events",
        eval_ids=("1", "6", "13"),
    ),
    _spec(
        "eeglab_epoch",
        "events_erp",
        "_eeglab_epoch",
        eeglab_function_family="pop_epoch/pop_rmbase",
        read_write_effect="converts/updates EEG epochs in memory",
        docs_id="tools:erp",
        eval_ids=("2", "6", "18"),
    ),
    _spec(
        "eeglab_erp_analysis",
        "events_erp",
        "_eeglab_erp_analysis",
        eeglab_function_family="ERP averaging/stat summaries",
        read_write_effect="computes ERP outputs from EEG state",
        docs_id="tools:erp",
        eval_ids=("2",),
    ),
    _spec(
        "eeglab_sort_epochs",
        "events_erp",
        "_eeglab_sort_epochs",
        eeglab_function_family="epoch metadata sorting",
        read_write_effect="reorders/labels epochs in memory",
        docs_id="tools:erp",
    ),
    _spec(
        "eeglab_average_erp",
        "events_erp",
        "_eeglab_average_erp",
        eeglab_function_family="ERP averaging",
        read_write_effect="computes ERP averages",
        docs_id="tools:erp",
    ),
    _spec(
        "eeglab_spectral",
        "frequency_timefreq",
        "_eeglab_spectral",
        eeglab_function_family="pop_spectopo/spectral summaries",
        read_write_effect="computes spectral outputs",
        docs_id="tools:frequency",
        eval_ids=("3", "17", "29"),
    ),
    _spec(
        "eeglab_timefreq",
        "frequency_timefreq",
        "_eeglab_timefreq",
        eeglab_function_family="pop_newtimef/ERSP/ITC",
        read_write_effect="computes time-frequency outputs",
        docs_id="tools:timefreq",
        eval_ids=("6",),
    ),
    _spec(
        "eeglab_connectivity",
        "frequency_timefreq",
        "_eeglab_connectivity",
        eeglab_function_family="coherence/PLV summaries",
        read_write_effect="computes connectivity outputs",
        docs_id="tools:connectivity",
        eval_ids=("30",),
    ),
    _spec(
        "eeglab_topoplot",
        "visualization",
        "_eeglab_topoplot",
        eeglab_function_family="pop_topoplot/topoplot",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
        eval_ids=("7", "27"),
    ),
    _spec(
        "eeglab_plot_erp",
        "visualization",
        "_eeglab_plot_erp",
        eeglab_function_family="pop_ploterp",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
    ),
    _spec(
        "eeglab_plot_timefreq",
        "visualization",
        "_eeglab_plot_timefreq",
        eeglab_function_family="pop_newtimef plotting",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
        eval_ids=("6",),
    ),
    _spec(
        "eeglab_plot_components",
        "visualization",
        "_eeglab_plot_components",
        eeglab_function_family="pop_topoplot/component plots",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
    ),
    _spec(
        "eeglab_plot_psd",
        "visualization",
        "_eeglab_plot_psd",
        eeglab_function_family="pop_spectopo/PSD plots",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
    ),
    _spec(
        "eeglab_plot_connectivity",
        "visualization",
        "_eeglab_plot_connectivity",
        eeglab_function_family="connectivity matrix visualization",
        read_write_effect="writes figure output",
        docs_id="tools:visualization",
    ),
    _spec(
        "eeglab_source_localization",
        "source",
        "_eeglab_source_localization",
        eeglab_function_family="DIPFIT/pop_multifit",
        read_write_effect="adds source model results to EEG state",
        docs_id="tools:source",
        eval_ids=("9", "16", "20", "35"),
    ),
    _spec(
        "eeglab_source_settings",
        "source",
        "_eeglab_source_settings",
        eeglab_function_family="DIPFIT/pop_dipfit_settings",
        read_write_effect="adds source model settings to EEG state",
        docs_id="tools:source",
        eval_ids=("9", "16", "35"),
    ),
    _spec(
        "eeglab_study_create",
        "study",
        "_eeglab_study_create",
        eeglab_function_family="pop_studywizard/pop_importbids/STUDY",
        read_write_effect="creates STUDY/ALLEEG state",
        docs_id="tools:study",
        eval_ids=("8", "14"),
    ),
    _spec(
        "eeglab_study_design",
        "study",
        "_eeglab_study_design",
        eeglab_function_family="std_makedesign",
        read_write_effect="modifies STUDY design state",
        docs_id="tools:study",
        eval_ids=("8", "21"),
    ),
    _spec(
        "eeglab_study_statistics",
        "study",
        "_eeglab_study_statistics",
        eeglab_function_family="pop_statparams/pop_stat",
        read_write_effect="computes STUDY statistics",
        docs_id="tools:study",
        eval_ids=("8", "21"),
    ),
    _spec(
        "eeglab_pipeline",
        "workflow",
        "_eeglab_pipeline",
        eeglab_function_family="bundled pop_ preprocessing pipeline",
        read_write_effect="modifies EEG state and writes derivatives",
        docs_id="tools:pipeline",
        eval_ids=("10",),
    ),
)


RESEARCH_WORKFLOW_TOOL_SPECS: tuple[ToolSpec, ...] = (
    _spec(
        "eeglab_qc_report",
        "workflow",
        "_eeglab_qc_report",
        eeglab_function_family="MCP workflow over info/events/history",
        read_write_effect="read-only QC synthesis",
        docs_id="workflows:quick_qc",
        eval_ids=("1", "10", "12", "22"),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_erp_light_workflow",
        "workflow",
        "_eeglab_erp_light_workflow",
        eeglab_function_family="MCP workflow over load/filter/epoch/ERP/save",
        read_write_effect="writes derivative ERP output",
        docs_id="workflows:safe_erp",
        eval_ids=("2",),
        output_schema="workflow_output",
    ),
    _spec(
        "eeglab_workflow_recommend",
        "workflow",
        "_eeglab_workflow_recommend",
        eeglab_function_family="MCP research planner",
        read_write_effect="read-only recommendation",
        docs_id="workflows:planning",
        eval_ids=("11", "12", "17", "24", "26", "37", "39", "43", "44"),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_project_plan",
        "workflow",
        "_eeglab_project_plan",
        eeglab_function_family="MCP research planner",
        read_write_effect="read-only project plan",
        docs_id="workflows:planning",
        eval_ids=(
            "11",
            "14",
            "16",
            "17",
            "22",
            "23",
            "26",
            "34",
            "37",
            "40",
            "42",
            "43",
            "44",
            "45",
            "49",
            "50",
            "54",
            "55",
            "56",
        ),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_protocol_export",
        "workflow",
        "_eeglab_protocol_export",
        eeglab_function_family="MCP protocol renderer",
        read_write_effect="may write protocol artifact only",
        docs_id="workflows:protocol",
        eval_ids=(
            "17",
            "25",
            "31",
            "32",
            "36",
            "37",
            "40",
            "41",
            "42",
            "44",
            "46",
            "47",
            "48",
            "49",
            "50",
            "51",
            "52",
            "53",
            "54",
            "55",
            "56",
        ),
        risk_level="standard",
        output_schema="workflow_output",
    ),
    _spec(
        "eeglab_plugin_check",
        "workflow",
        "_eeglab_plugin_check",
        eeglab_function_family="MATLAB function/plugin availability probes",
        read_write_effect="read-only environment probe",
        docs_id="workflows:plugin_doctor",
        eval_ids=(
            "15",
            "19",
            "31",
            "32",
            "33",
            "40",
            "43",
            "44",
            "45",
            "46",
            "49",
            "51",
            "52",
            "53",
            "54",
            "55",
        ),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_event_semantics_audit",
        "workflow",
        "_eeglab_event_semantics_audit",
        eeglab_function_family="MCP event semantics classifier",
        read_write_effect="read-only marker classification",
        docs_id="workflows:event_semantics",
        eval_ids=("2", "6", "13", "18", "23", "34", "46", "48"),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_method_preflight",
        "workflow",
        "_eeglab_method_preflight",
        eeglab_function_family="MCP official method gate evaluator",
        read_write_effect="read-only method preflight",
        docs_id="workflows:method_preflight",
        eval_ids=(
            "2",
            "3",
            "5",
            "6",
            "8",
            "9",
            "10",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "34",
            "35",
            "36",
            "38",
            "39",
            "40",
            "41",
            "42",
            "43",
            "44",
            "45",
            "46",
            "47",
            "48",
            "49",
            "50",
            "51",
            "52",
            "53",
            "54",
            "55",
        ),
        risk_level="read_only",
        output_schema="workflow_output",
        annotations="read_only",
    ),
    _spec(
        "eeglab_generate_report",
        "workflow",
        "_eeglab_generate_report",
        eeglab_function_family="MCP report generator",
        read_write_effect="writes report artifact",
        docs_id="workflows:report",
        risk_level="standard",
        output_schema="workflow_output",
    ),
)


TOOL_SPECS: tuple[ToolSpec, ...] = LEGACY_LOW_LEVEL_TOOL_SPECS + RESEARCH_WORKFLOW_TOOL_SPECS
TOOL_REGISTRY: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}

LEGACY_LOW_LEVEL_TOOL_NAMES: frozenset[str] = frozenset(spec.name for spec in LEGACY_LOW_LEVEL_TOOL_SPECS)
RESEARCH_WORKFLOW_TOOL_NAMES: frozenset[str] = frozenset(spec.name for spec in RESEARCH_WORKFLOW_TOOL_SPECS)
EXPOSED_TOOL_NAMES: frozenset[str] = frozenset(TOOL_REGISTRY)


def get_tool_spec(name: str) -> ToolSpec:
    """Return one registry spec by tool name."""
    return TOOL_REGISTRY[name]


def registry_summary() -> dict[str, int]:
    """Return stable public tool counts for docs and verification."""
    return {
        "legacy_low_level": len(LEGACY_LOW_LEVEL_TOOL_NAMES),
        "research_workflow": len(RESEARCH_WORKFLOW_TOOL_NAMES),
        "total_exposed": len(EXPOSED_TOOL_NAMES),
    }


def validate_registry() -> list[str]:
    """Validate registry self-consistency without importing the MCP server."""
    errors: list[str] = []
    if len(TOOL_REGISTRY) != len(TOOL_SPECS):
        errors.append("tool registry contains duplicate names")
    if len(LEGACY_LOW_LEVEL_TOOL_NAMES) != LEGACY_LOW_LEVEL_COUNT:
        errors.append(f"expected {LEGACY_LOW_LEVEL_COUNT} legacy low-level tools")
    if len(RESEARCH_WORKFLOW_TOOL_NAMES) != RESEARCH_WORKFLOW_COUNT:
        errors.append(f"expected {RESEARCH_WORKFLOW_COUNT} research workflow tools")
    if len(EXPOSED_TOOL_NAMES) != TOTAL_EXPOSED_TOOL_COUNT:
        errors.append(f"expected {TOTAL_EXPOSED_TOOL_COUNT} exposed tools")
    for spec in TOOL_SPECS:
        for field in (
            "name",
            "category",
            "handler",
            "input_schema",
            "output_schema",
            "annotations",
            "risk_level",
            "eeglab_function_family",
            "read_write_effect",
            "docs_id",
        ):
            if not getattr(spec, field):
                errors.append(f"{spec.name} missing registry field {field}")
        if spec.risk_level == "high" and not spec.method_profile:
            errors.append(f"{spec.name} high-risk tool missing method profile")
    return errors


def validate_tool_definitions(tools: Iterable[Any]) -> list[str]:
    """Validate exposed MCP Tool definitions against registry identity."""
    tool_names = [tool.name for tool in tools]
    tool_set = set(tool_names)
    errors = validate_registry()
    duplicates = sorted(name for name in tool_set if tool_names.count(name) > 1)
    if duplicates:
        errors.append(f"duplicate MCP tool definitions: {duplicates}")
    missing = sorted(EXPOSED_TOOL_NAMES - tool_set)
    extra = sorted(tool_set - EXPOSED_TOOL_NAMES)
    if missing:
        errors.append(f"registered tools missing MCP definitions: {missing}")
    if extra:
        errors.append(f"MCP definitions missing registry entries: {extra}")
    return errors


def validate_handler_map(handlers: Mapping[str, Any]) -> list[str]:
    """Validate call_tool handler coverage against registry identity."""
    handler_names = set(handlers)
    errors = validate_registry()
    missing = sorted(EXPOSED_TOOL_NAMES - handler_names)
    extra = sorted(handler_names - EXPOSED_TOOL_NAMES)
    if missing:
        errors.append(f"registered tools missing handlers: {missing}")
    if extra:
        errors.append(f"handlers missing registry entries: {extra}")
    for name, spec in TOOL_REGISTRY.items():
        handler = handlers.get(name)
        actual = getattr(handler, "__name__", "") if handler is not None else ""
        if handler is not None and actual and actual != spec.handler:
            errors.append(f"{name} handler mismatch: registry={spec.handler} actual={actual}")
    return errors
