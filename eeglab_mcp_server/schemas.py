"""Tool schema metadata and validation helpers for EEGLAB MCP."""

from __future__ import annotations

import math
from typing import Any

from mcp.types import Tool, ToolAnnotations

try:
    from .official_alignment import HIGH_RISK_TOOL_NAMES
    from .tool_registry import TOOL_REGISTRY
except ImportError:  # pragma: no cover - direct script execution support
    from official_alignment import HIGH_RISK_TOOL_NAMES
    from tool_registry import TOOL_REGISTRY


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
    "required": [
        "status",
        "workflow",
        "steps",
        "parameters",
        "outputs",
        "summary",
        "limitations",
    ],
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
                    "data_path": {
                        "type": "string",
                        "description": "Input EEG dataset path, usually a .set file.",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for processed output files.",
                    },
                    "low_cutoff": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Bandpass low cutoff in Hz.",
                    },
                    "high_cutoff": {
                        "type": "number",
                        "default": 40.0,
                        "description": "Bandpass high cutoff in Hz.",
                    },
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
                        "enum": [
                            "auto",
                            "erp",
                            "resting",
                            "timefreq",
                            "ica",
                            "study",
                            "source",
                        ],
                        "description": "Target analysis family. Use auto when the user has not specified a goal; the tool will infer a conservative first-pass branch.",
                    },
                    "research_goal": {
                        "type": "string",
                        "description": "User-stated research goal, hypothesis, or analysis question. Leave blank only when it is genuinely unknown.",
                    },
                    "project_scale": {
                        "type": "string",
                        "enum": [
                            "unknown",
                            "single_subject",
                            "multi_subject",
                            "bids_study",
                            "exploratory_qc",
                        ],
                        "description": "Expected study scale and organization.",
                    },
                    "stage": {
                        "type": "string",
                        "enum": [
                            "planning",
                            "inspection",
                            "preprocessing",
                            "analysis",
                            "group",
                            "reporting",
                        ],
                        "description": "Current project stage so the recommendation can emphasize the right QC gate.",
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known event labels, if available.",
                    },
                    "srate": {
                        "type": "number",
                        "description": "Sampling rate in Hz, if known.",
                    },
                    "has_ica": {
                        "type": "boolean",
                        "description": "Whether ICA weights already exist.",
                    },
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
        Tool(
            name="eeglab_project_plan",
            title="EEGLAB Research Project Plan",
            description=(
                "Create a complete research-grade EEG analysis plan from the user's goal, data shape, event semantics, "
                "project scale, montage state, and plugin constraints. Use this before preprocessing, ICA, source, or "
                "group/STUDY work when the project needs a reproducible protocol rather than a single tool call. "
                "This tool does not run MATLAB or change data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "research_goal": {
                        "type": "string",
                        "description": "Primary hypothesis, research question, or analysis objective. Leave blank only when unknown.",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": [
                            "auto",
                            "erp",
                            "resting",
                            "timefreq",
                            "ica",
                            "study",
                            "source",
                            "connectivity",
                            "segment_qc",
                        ],
                        "description": "Requested analysis family. Use auto when the user has not committed to a method.",
                    },
                    "project_scale": {
                        "type": "string",
                        "enum": [
                            "unknown",
                            "single_subject",
                            "multi_subject",
                            "bids_study",
                            "exploratory_qc",
                        ],
                        "description": "Study organization and expected level of inference.",
                    },
                    "data_format": {
                        "type": "string",
                        "description": "Observed file format or container, for example .set, BrainVision, EDF/BDF, CNT, MFF, NWB, or BIDS.",
                    },
                    "data_shape": {
                        "type": "string",
                        "enum": ["unknown", "continuous_or_single_trial", "epoched"],
                        "description": "Whether the available EEG data are continuous/single-trial or already epoched.",
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known marker labels or candidate event types.",
                    },
                    "event_semantics": {
                        "type": "object",
                        "description": "Mapping from event label to meaning, such as condition, boundary, impedance, or segment marker.",
                    },
                    "srate": {
                        "type": "number",
                        "description": "Sampling rate in Hz, if known.",
                    },
                    "subject_count": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Number of subjects expected in the project.",
                    },
                    "session_count": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Number of sessions/runs per subject, if known.",
                    },
                    "has_channel_locations": {
                        "type": "boolean",
                        "description": "Whether channel-location metadata are complete enough for topography/source claims.",
                    },
                    "has_behavioral_log": {
                        "type": "boolean",
                        "description": "Whether external behavioral/event logs are available for condition-level interpretation.",
                    },
                    "has_continuous_raw": {
                        "type": "boolean",
                        "description": "Whether the original continuous raw recording is available, not only epoched derivatives.",
                    },
                    "required_outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Expected deliverables such as cleaned .set, ERP tables, spectra, figures, protocol, or group statistics.",
                    },
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Research project plan",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_protocol_export",
            title="EEGLAB Protocol Export",
            description=(
                "Export a study protocol from current assumptions, parameters, QC gates, steps, outputs, limitations, "
                "and official EEGLAB reference anchors. Use when a plan needs a Markdown or JSON protocol for a lab notebook, "
                "methods section draft, or reproducibility handoff. It writes a file only when output_path is supplied."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "json"],
                        "default": "markdown",
                        "description": "Protocol serialization format.",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional file path for the exported protocol. Omit for structured/text content only.",
                    },
                    "research_goal": {
                        "type": "string",
                        "description": "Study goal or hypothesis to record.",
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Analysis family or branch being documented.",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Exact preprocessing/analysis parameters to preserve.",
                    },
                    "gate_results": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Optional compact official gate summaries from upstream workflow tools.",
                    },
                    "source_claim_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional explicit official claim IDs to anchor the protocol report.",
                    },
                    "report_fields": {
                        "type": "object",
                        "description": "Optional report field matrix coverage grouped by official reporting sections.",
                    },
                    "override_used": {
                        "type": "boolean",
                        "description": "Record whether the workflow proceeded under an explicit override.",
                    },
                    "override_reason": {
                        "type": "string",
                        "description": "Explicit user-approved reason for any override.",
                    },
                    "blocked_requirements_acknowledged": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Critical requirements acknowledged when proceeding under override.",
                    },
                    "missing_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known missing requirements that should still be reported in the protocol.",
                    },
                    "qc_gates": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "QC gates that must be checked before analysis-ready claims.",
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Planned or completed workflow steps.",
                    },
                    "outputs": {
                        "type": "object",
                        "description": "Expected or produced output files/tables/figures.",
                    },
                    "limitations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known limitations and blocked interpretations.",
                    },
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Protocol export",
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_plugin_check",
            title="EEGLAB Plugin Check",
            description=(
                "Check whether important EEGLAB plugins/functions are reachable in the local MATLAB/EEGLAB path, including "
                "clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, MFF, NWB, BVA, HEDTools, LIMO, SIFT, and NSG-related functions. Use before plugin-dependent "
                "ICA cleanup, ASR, source, BIDS/STUDY, import/export, event annotation, or connectivity workflows."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "plugins": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional plugin/function groups to probe. Defaults to the official plugin matrix, including clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, MFF, NWB, BVA, HEDTools, LIMO, SIFT, and NSGportal.",
                    }
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Plugin check",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_event_semantics_audit",
            title="EEGLAB Event Semantics Audit",
            description=(
                "Classify event labels as candidate triggers, task conditions, boundaries, impedance/QC annotations, or "
                "segment markers before epoching. Use this when marker meanings are ambiguous, when BrainVision/EDF events "
                "mix task and metadata markers, or when only start/end segment markers are available. This tool does not edit events."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event labels observed in the data.",
                    },
                    "event_counts": {
                        "type": "object",
                        "description": "Mapping of event label to observed count.",
                    },
                    "event_descriptions": {
                        "type": "object",
                        "description": "Optional user/lab-provided mapping of event label to meaning.",
                    },
                    "boundary_markers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels known to indicate boundaries, run starts/ends, or pauses rather than analysis events.",
                    },
                    "condition_markers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels confirmed as task conditions or analysis triggers.",
                    },
                    "segment_markers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels used only to pair start/end recording or task-block segments.",
                    },
                    "exclude_markers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels to exclude from derived analysis event tables.",
                    },
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Event semantics audit",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        ),
        Tool(
            name="eeglab_method_preflight",
            title="EEGLAB Official Method Preflight",
            description=(
                "Evaluate official EEGLAB/SCCN method gates before high-risk processing. Use this before epoching, "
                "clean_rawdata/ASR, ICA/ICLabel, component removal, source/DIPFIT, staged BIDS/STUDY work, "
                "BIDS/acquisition provenance checks, or one-click pipelines. "
                "It does not run MATLAB; it returns gate_status, missing requirements, source claim IDs, and safe next steps."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "Method family such as acquisition_metadata, bids_metadata, bids_import, import_plugins, data_export, hed_event_annotation, history_scripting, event_script_modification, study_create, study_design, study_statistics, study, epoch, timefreq, clean_rawdata, run_ica, iclabel, source, derivative_processing, or pipeline.",
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Optional MCP tool name to map to a method profile, for example eeglab_epoch or eeglab_source_localization.",
                    },
                    "context": {
                        "type": "object",
                        "description": "Known facts used for gate checks: raw_input_preserved, derivative_output_planned, source/export format, event/channel mapping, HED schema, event modification rules, urevent status, reference/montage, power_line_frequency, BIDS sidecars, event_roles, data_shape, plugins_available, has_ica, has_channel_locations, output_dir, rank_reference_reviewed, and related fields.",
                    },
                    "strictness": {
                        "type": "string",
                        "enum": ["hard", "advisory"],
                        "default": "hard",
                        "description": "hard blocks missing critical requirements unless override_reason is supplied; advisory reports gaps without blocking.",
                    },
                    "override_reason": {
                        "type": "string",
                        "description": "Explicit user-approved reason for proceeding despite blocked official gates.",
                    },
                },
                "required": [],
            },
            outputSchema=WORKFLOW_OUTPUT_SCHEMA,
            annotations=ToolAnnotations(
                title="Official method preflight",
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

TOOL_DESCRIPTION_APPENDIX: dict[str, str] = {
    "eeglab_init": "Official pattern: starts EEGLAB with eeglab nogui. Preconditions: MATLAB can resolve EEGLAB. Modifies MATLAB path/session, not EEG data. Common failures: MATLAB unavailable or EEGLAB_PATH wrong.",
    "eeglab_load_data": "Official pattern: wraps pop_loadset/pop_biosig/pop_loadbv-style import depending on file type, then eeg_checkset. Preconditions: local readable dataset and sidecars when needed. Modifies in-memory EEG. Common failures: missing .fdt/.eeg sidecar or unsupported format.",
    "eeglab_save_data": "Official pattern: wraps pop_saveset. Preconditions: EEG is loaded. Writes a derivative .set/.fdt; do not overwrite raw inputs unless explicitly approved. Common failures: invalid output path or missing EEG.",
    "eeglab_import_bids": "Official pattern: uses EEGLAB BIDS import/STUDY path such as pop_importbids. Preconditions: BIDS-like folder and plugin support. Modifies ALLEEG/STUDY/EEG in MATLAB. Common failures: invalid BIDS layout or missing BIDS tools.",
    "eeglab_info": "Official pattern: inspects EEG structure fields and eeg_checkset-compatible metadata. Preconditions: EEG is loaded. Read-only. Common failures: no current EEG dataset.",
    "eeglab_history": "Official pattern: reads EEG.history, where EEGLAB usually records pop_ command history. Preconditions: EEG is loaded. Read-only. Common failures: empty or imported history.",
    "eeglab_filter": "Official pattern: wraps pop_eegfiltnew or equivalent EEGLAB filtering. Preconditions: continuous/epoched suitability and justified cutoffs. Modifies in-memory EEG. Common failures: invalid cutoff order or overly aggressive filter settings.",
    "eeglab_resample": "Official pattern: wraps pop_resample. Preconditions: EEG is loaded and target sample rate is justified. Modifies in-memory EEG. Common failures: nonpositive sample rate.",
    "eeglab_reref": "Official pattern: wraps pop_reref. Preconditions: reference policy is known and channel labels are valid for channel reference. Modifies in-memory EEG. Common failures: missing reference channel or inappropriate rank assumptions.",
    "eeglab_select_channels": "Official pattern: wraps pop_select for channel inclusion/exclusion. Preconditions: channel labels are known. Modifies in-memory EEG. Common failures: mixing include and exclude lists or absent labels.",
    "eeglab_interpolate_channels": "Official pattern: wraps pop_interp. Preconditions: bad-channel list and channel locations are available. Modifies in-memory EEG. Common failures: missing montage/channel locations.",
    "eeglab_edit_channels": "Official pattern: wraps pop_chanedit-style channel metadata edits. Preconditions: channel-location file or rename map is valid. Modifies channel metadata. Common failures: wrong montage file or incomplete label mapping.",
    "eeglab_clean_line_noise": "Official pattern: line-noise cleanup around 50/60 Hz. Preconditions: local mains frequency and data shape are known. Modifies in-memory EEG. Common failures: plugin/function unavailable or wrong line frequency.",
    "eeglab_clean_rawdata": "Official pattern: wraps clean_rawdata/pop_clean_rawdata for bad channels, bad segments, and ASR. Preconditions: continuous raw data and documented thresholds. Modifies in-memory EEG. Common failures: plugin missing or aggressive thresholds removing too much data.",
    "eeglab_run_ica": "Official pattern: wraps pop_runica/runica or Picard. Preconditions: suitable continuous data, rank/reference considered, bad channels addressed. Modifies ICA fields. Common failures: plugin missing, rank mismatch, insufficient data.",
    "eeglab_classify_ica": "Official pattern: wraps ICLabel/pop_iclabel. Preconditions: ICA weights exist and ICLabel is installed. Modifies component classification metadata. Common failures: no ICA or missing ICLabel dependencies.",
    "eeglab_flag_components": "Official pattern: uses ICLabel probability classes to mark candidate components. Preconditions: ICLabel classifications exist. Modifies rejection flags, not data removal. Common failures: thresholds too broad or missing classifications.",
    "eeglab_remove_components": "Official pattern: wraps pop_subcomp. Preconditions: reviewed component list or explicit threshold. Modifies in-memory EEG by subtracting components. Common failures: removing brain components or ambiguous auto thresholds.",
    "eeglab_reject_epochs": "Official pattern: wraps EEGLAB epoch rejection methods. Preconditions: epoched data and documented thresholds. Modifies in-memory EEG. Common failures: continuous data or overly strict thresholds.",
    "eeglab_get_events": "Official pattern: reads EEG.event/urevent. Preconditions: EEG is loaded. Read-only. Common failures: missing markers or ambiguous event semantics.",
    "eeglab_epoch": "Official pattern: wraps pop_epoch and baseline correction. Preconditions: validated task-condition markers and epoch/baseline windows. Modifies in-memory EEG into epoched data. Common failures: no matching events or baseline outside epoch.",
    "eeglab_erp_analysis": "Official pattern: derives ERP summaries from epoched EEG. Preconditions: event semantics, baseline, and channel choices are valid. Read-only analysis output. Common failures: continuous data or missing channels.",
    "eeglab_sort_epochs": "Official pattern: sorts epochs by event/condition metadata. Preconditions: epoched data and condition labels. Modifies epoch order/metadata. Common failures: absent condition field.",
    "eeglab_average_erp": "Official pattern: averages ERP by condition/channel from epoched data. Preconditions: valid epochs and condition labels. Read-only analysis output. Common failures: no trials after rejection.",
    "eeglab_spectral": "Official pattern: spectral analysis via EEGLAB spectopo-style functions. Preconditions: suitable continuous/epoch data and frequency range. Read-only analysis output. Common failures: frequency range above Nyquist or unsuitable epochs.",
    "eeglab_timefreq": "Official pattern: time-frequency via newtimef/pop_newtimef-style ERSP/ITC. Preconditions: event-locked epochs, baseline, channels, and frequency/cycle choices. Read-only analysis output. Common failures: missing epochs or too-short windows.",
    "eeglab_connectivity": "Official pattern: connectivity estimates such as coherence/PLV. Preconditions: channels, frequency range, and artifact policy are defined. Read-only analysis output. Common failures: missing channels or overinterpreting sensor-level connectivity.",
    "eeglab_topoplot": "Official pattern: wraps topoplot/pop_topoplot. Preconditions: channel locations and valid time/frequency selection. Writes figure output. Common failures: missing montage or invalid output path.",
    "eeglab_plot_erp": "Official pattern: wraps EEGLAB ERP plotting. Preconditions: ERP/epoched data and requested channels exist. Writes figure output. Common failures: missing channels or no condition averages.",
    "eeglab_plot_timefreq": "Official pattern: wraps time-frequency plotting. Preconditions: valid time-frequency settings and channel. Writes figure output. Common failures: no current epoched data or bad output path.",
    "eeglab_plot_components": "Official pattern: plots ICA components/topographies. Preconditions: ICA exists and channel locations help interpretation. Writes figure output. Common failures: no ICA or missing montage.",
    "eeglab_source_localization": "Official pattern: wraps DIPFIT settings and multifit for equivalent dipoles. Preconditions: ICA, correct channel locations, head model resources, and DIPFIT. Modifies dipfit fields. Common failures: missing DIPFIT/montage or no ICA.",
    "eeglab_source_settings": "Official pattern: wraps pop_dipfit_settings. Preconditions: DIPFIT resources and coordinate assumptions are known. Modifies source model settings. Common failures: missing template files or wrong montage.",
    "eeglab_study_create": "Official pattern: wraps pop_importbids/pop_studywizard/pop_study. Preconditions: multiple datasets or BIDS layout with stable single-subject processing. Modifies STUDY/ALLEEG. Common failures: inconsistent metadata or missing BIDS tools.",
    "eeglab_study_design": "Official pattern: wraps std_makedesign. Preconditions: STUDY exists and design variables are known. Modifies STUDY design. Common failures: missing subject/condition metadata.",
    "eeglab_study_statistics": "Official pattern: wraps STUDY statistical parameter/stat calls. Preconditions: valid design, precomputed measures, alpha/correction policy. Read/write STUDY state. Common failures: missing measures or invalid correction assumptions.",
    "eeglab_pipeline": "Official pattern: chains pop_ preprocessing/analysis functions into a standardized derivative workflow. Preconditions: user accepts defaults and output path is separate from raw data. High risk because many decisions are bundled. Common failures: missing plugins/events or unsuitable defaults.",
    "eeglab_qc_report": "Research workflow: combines info/events/history into a QC gate. Preconditions: EEG loaded. Read-only. Common failures: no EEG or incomplete acquisition metadata.",
    "eeglab_erp_light_workflow": "Research workflow: conservative smoke ERP using load/filter/epoch/ERP/save. Preconditions: official preflight gates, validated ERP event labels, and separate output directory. Writes derivative files. Common failures: wrong event labels or absent requested channels.",
    "eeglab_workflow_recommend": "Research workflow: non-destructive recommender for analysis branch, QC gates, and limitations. Preconditions: pass known facts when available. Read-only. Common failures: insufficient goal/event/montage facts.",
    "eeglab_project_plan": "Research workflow: project-level protocol planner. Preconditions: goal/design facts if available. Read-only. Common failures: unresolved event semantics or missing montage/behavioral log constraints.",
    "eeglab_protocol_export": "Research workflow: protocol serializer to Markdown/JSON. Preconditions: steps/parameters/QC gates should be reviewed. May write one protocol file. Common failures: invalid output path.",
    "eeglab_plugin_check": "Research workflow: probes plugin/function availability in MATLAB/EEGLAB. Preconditions: MATLAB and EEGLAB can start. Read-only. Common failures: missing plugin path or unavailable MATLAB.",
    "eeglab_event_semantics_audit": "Research workflow: classifies markers before epoching. Preconditions: event labels/counts or user semantics. Read-only. Common failures: no condition-level event remains after excluding boundaries/QC markers.",
    "eeglab_method_preflight": "Official alignment workflow: evaluates EEGLAB/SCCN claim-map gates before high-risk processing. Preconditions: pass available method context. Read-only. Common failures: unmapped method or missing critical prerequisites.",
}

READ_ONLY_TOOLS = {
    "eeglab_info",
    "eeglab_history",
    "eeglab_get_events",
    "eeglab_workflow_recommend",
    "eeglab_qc_report",
    "eeglab_project_plan",
    "eeglab_plugin_check",
    "eeglab_event_semantics_audit",
    "eeglab_method_preflight",
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


def _derivative_output_label(read_write_effect: str) -> str:
    """Summarize derivative expectations from the registry read/write effect."""
    effect = read_write_effect.lower()
    if "read-only" in effect:
        return "no data derivative unless the caller exports a report or figure"
    if "writes derivative" in effect:
        return "yes, writes a derivative output"
    if "writes figure" in effect:
        return "yes, writes a derivative figure artifact"
    if "may write" in effect:
        return "optional report/protocol derivative only"
    if any(
        token in effect
        for token in (
            "modifies",
            "adds",
            "removes",
            "creates",
            "converts",
            "updates",
            "loads",
        )
    ):
        return "data-changing; save results only as a separate derivative"
    if "computes" in effect:
        return "analysis derivative only when exported"
    return "not classified; record output handling in the report"


def _tool_contract_appendix(tool_name: str) -> str:
    """Build the model-facing official contract from the central registry."""
    spec = TOOL_REGISTRY.get(tool_name)
    if spec is None:
        return ""
    method_profile = spec.method_profile or "none"
    if spec.risk_level == "high":
        preflight = (
            f"required through eeglab_method_preflight method={method_profile} "
            "before execution unless an explicit override reason is recorded"
        )
    elif spec.risk_level == "read_only":
        preflight = "not required for execution; use for planning gates when scientific claims depend on it"
    else:
        preflight = "use when project gates or downstream interpretation depend on this step"
    return (
        "Tool contract: "
        f"EEGLAB function family: {spec.eeglab_function_family}. "
        f"Official method profile: {method_profile}. "
        f"Risk level: {spec.risk_level}. "
        f"Preflight: {preflight}. "
        f"Read/write effect: {spec.read_write_effect}. "
        f"Derivative output: {_derivative_output_label(spec.read_write_effect)}."
    )


def annotate_tools(tools: list[Tool]) -> list[Tool]:
    """Add MCP title/annotation metadata without changing tool names."""
    for tool in tools:
        tool.title = tool.title or TOOL_TITLES.get(tool.name, tool.name.replace("_", " ").title())
        if tool.name in HIGH_RISK_TOOL_NAMES:
            properties = dict(tool.inputSchema.get("properties", {}))
            properties.setdefault(
                "override_gate",
                {
                    "description": "Set true only when the user explicitly accepts missing official preflight requirements.",
                    "default": False,
                },
            )
            properties.setdefault(
                "override_reason",
                {
                    "description": "Required when override_gate is true; records why blocked official gates are being bypassed.",
                },
            )
            properties.setdefault(
                "method_context",
                {
                    "description": "Known facts for official preflight, such as data_shape, event_roles, plugins_available, source/export format, event/channel mapping, HED schema, event modification rules, urevent status, has_ica, has_channel_locations, output_dir, rank_reference_reviewed, and design variables.",
                },
            )
            tool.inputSchema = {**tool.inputSchema, "properties": properties}
        appendix = TOOL_DESCRIPTION_APPENDIX.get(tool.name)
        if appendix:
            description = tool.description or ""
            if appendix not in description:
                tool.description = f"{description} {appendix}".strip()
        contract = _tool_contract_appendix(tool.name)
        if contract:
            description = tool.description or ""
            if contract not in description:
                tool.description = f"{description} {contract}".strip()
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
            _require_present(
                arguments,
                "ref_channel",
                "ref_type 为 channel 时需要 ref_channel",
                errors,
            )

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

    elif name == "eeglab_project_plan":
        _positive_number(arguments, "srate", errors)
        _positive_integer(arguments, "subject_count", errors)
        _positive_integer(arguments, "session_count", errors)

    elif name == "eeglab_protocol_export":
        if "qc_gates" in arguments and _is_present(arguments, "qc_gates") is False:
            errors.append("eeglab_protocol_export 的 qc_gates 不能为空数组")
        if "steps" in arguments and _is_present(arguments, "steps") is False:
            errors.append("eeglab_protocol_export 的 steps 不能为空数组")
        for field in (
            "gate_results",
            "source_claim_ids",
            "blocked_requirements_acknowledged",
            "missing_requirements",
        ):
            if field in arguments and _is_present(arguments, field) is False:
                errors.append(f"eeglab_protocol_export 的 {field} 不能为空数组")
        if arguments.get("override_used") is True and not _is_present(arguments, "override_reason"):
            errors.append("eeglab_protocol_export 使用 override 时必须提供 override_reason")

    elif name == "eeglab_plugin_check":
        if "plugins" in arguments and _is_present(arguments, "plugins") is False:
            errors.append("eeglab_plugin_check 的 plugins 不能为空数组")

    elif name == "eeglab_method_preflight":
        if not _is_present(arguments, "method") and not _is_present(arguments, "tool_name"):
            errors.append("eeglab_method_preflight 需要 method 或 tool_name")

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

    if name in HIGH_RISK_TOOL_NAMES:
        if arguments.get("override_gate") is True and not _is_present(arguments, "override_reason"):
            errors.append("override_gate 为 true 时必须提供 override_reason")

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
