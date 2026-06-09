"""High-level research workflow helpers for EEGLAB MCP tools."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.types import TextContent


LIMITATIONS = [
    "This workflow reports EEG signal-processing outputs, not clinical or diagnostic conclusions.",
    "Results depend on local EEGLAB plugins, channel metadata, event coding, and acquisition quality.",
    "Recording/acquisition metadata may be incomplete unless it was preserved in the imported EEG file or BIDS sidecars.",
    "Light workflows are smoke-tested entry points and do not replace study-specific preprocessing decisions.",
]


def text_payload(payload: dict[str, Any]) -> list[TextContent]:
    """Return a JSON text MCP payload."""
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def structured_payload(payload: dict[str, Any]) -> tuple[list[TextContent], dict[str, Any]]:
    """Return text JSON plus structuredContent for MCP clients that support it."""
    return text_payload(payload), payload


def parse_tool_result(result: Any) -> dict[str, Any]:
    """Parse the first TextContent JSON item returned by a tool call."""
    if isinstance(result, tuple):
        result = result[0]
    if not result:
        return {"status": "error", "code": "empty_tool_result", "error": "tool returned no content"}
    text = result[0].text if hasattr(result[0], "text") else ""
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "code": "non_json_tool_result",
            "error": f"tool returned non-JSON text: {exc}",
            "details": {"text_preview": text[:1200]},
        }


def workflow_error(
    workflow: str,
    step: str,
    payload: dict[str, Any],
    *,
    parameters: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a workflow-shaped error response."""
    return {
        "status": "error",
        "code": payload.get("code", "workflow_step_failed"),
        "error": payload.get("error", f"{step} failed"),
        "next_step": payload.get("next_step", "Inspect the failed step details and rerun with corrected inputs."),
        "workflow": workflow,
        "steps": steps,
        "parameters": parameters,
        "outputs": {},
        "summary": {"failed_step": step},
        "limitations": LIMITATIONS,
        "details": {"step": step, "result": payload},
    }


def safe_output_filename(name: Any, *, default: str) -> str:
    """Return a safe leaf filename for a workflow output."""
    filename = str(name or default).strip()
    if not filename:
        filename = default
    if not filename.lower().endswith(".set"):
        filename += ".set"
    if Path(filename).name != filename or filename in {".", ".."} or any(sep in filename for sep in ("/", "\\")):
        raise ValueError("output_filename must be a filename inside output_dir, not a path")
    if os.path.splitdrive(filename)[0]:
        raise ValueError("output_filename must not include a drive prefix")
    return filename


def workflow_success(
    workflow: str,
    *,
    steps: list[dict[str, Any]],
    parameters: dict[str, Any],
    outputs: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a workflow-shaped success response."""
    return {
        "status": "success",
        "workflow": workflow,
        "steps": steps,
        "parameters": parameters,
        "outputs": outputs,
        "summary": summary,
        "limitations": LIMITATIONS,
    }


def qc_report_from_payloads(info: dict[str, Any], events: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    """Build a QC report from existing low-level tool payloads."""
    recording = info.get("recording") or {}
    missing_locations = []
    channel_labels = info.get("channel_labels") or []
    if info.get("has_channel_locations") is False:
        missing_locations = channel_labels

    risks: list[str] = []
    provenance_hints: list[str] = []
    if not info.get("num_events"):
        risks.append("No events were reported; event-locked analyses may not be possible.")
    elif not info.get("has_urevent_links", False):
        provenance_hints.append("Event urevent links are absent; preserve event latencies/counts when transforming epochs.")
    if info.get("has_channel_locations") is False:
        risks.append("Channel locations appear missing; topography/source workflows need channel locations.")
    elif info.get("channel_location_coverage", 1) < 1:
        risks.append("Some channel locations are missing; topography/source workflows may be incomplete.")
    if not info.get("ica_computed", False):
        risks.append("ICA weights are absent; component-level artifact review is not available yet.")
    if info.get("srate") and info["srate"] < 128:
        risks.append("Sampling rate is low for high-frequency analyses.")
    if not info.get("processing_history_available", False):
        provenance_hints.append("EEGLAB processing history is empty; report all steps applied in this session explicitly.")
    if not recording.get("has_comments", False):
        provenance_hints.append("Dataset comments/recording notes are absent; record acquisition context outside the .set file if needed.")
    if not recording.get("filename") and not info.get("filename"):
        provenance_hints.append("Source filename is missing from EEG metadata; keep the absolute input path in reports.")

    return workflow_success(
        "eeglab_qc_report",
        steps=[
            {"name": "eeglab_info", "status": info.get("status", "success")},
            {"name": "eeglab_get_events", "status": events.get("status", "success")},
            {"name": "eeglab_history", "status": history.get("status", "success")},
        ],
        parameters={},
        outputs={},
        summary={
            "recording": {
                "data_shape": recording.get("data_shape"),
                "sampling_rate_hz": recording.get("sampling_rate_hz", info.get("srate")),
                "channel_count": recording.get("channel_count", info.get("nbchan")),
                "trials": recording.get("trials", info.get("trials")),
                "points_per_epoch": recording.get("points_per_epoch", info.get("pnts")),
                "epoch_duration_sec": recording.get("epoch_duration_sec", info.get("duration_sec")),
                "total_data_duration_sec": recording.get("total_data_duration_sec"),
                "setname": recording.get("setname", info.get("setname")),
                "filename": recording.get("filename", info.get("filename")),
                "filepath": recording.get("filepath", info.get("filepath")),
                "saved_state": recording.get("saved_state", info.get("saved")),
                "has_comments": recording.get("has_comments", False),
                "has_etc_metadata": recording.get("has_etc_metadata", False),
            },
            "nbchan": info.get("nbchan"),
            "srate": info.get("srate"),
            "pnts": info.get("pnts"),
            "trials": info.get("trials"),
            "duration_sec": info.get("duration_sec"),
            "event_types": events.get("event_types", info.get("event_types", [])),
            "event_counts": events.get("event_counts", info.get("event_counts", {})),
            "event_latency_range_sec": info.get("event_latency_range_sec"),
            "has_urevent_links": info.get("has_urevent_links", False),
            "num_urevents": info.get("num_urevents", 0),
            "channel_location_coverage": info.get("channel_location_coverage"),
            "channels_with_locations": info.get("channels_with_locations"),
            "channels_missing_locations": info.get("channels_missing_locations"),
            "ica_computed": info.get("ica_computed", False),
            "ica_classified": info.get("ica_classified", False),
            "missing_channel_locations": missing_locations,
            "risk_hints": risks,
            "provenance_hints": provenance_hints,
            "history_available": bool(history.get("history") and history.get("history") != "无操作历史记录"),
        },
    )


def recommend_workflow(args: dict[str, Any]) -> dict[str, Any]:
    """Recommend an adaptive, project-level, non-destructive EEG workflow plan."""
    requested_analysis_type = args.get("analysis_type", "auto")
    event_types = args.get("event_types", [])
    data_shape = args.get("data_shape")
    has_channel_locations = args.get("has_channel_locations")

    if requested_analysis_type != "auto":
        analysis_type = requested_analysis_type
    elif event_types:
        analysis_type = "erp"
    elif data_shape == "epoched":
        analysis_type = "erp"
    else:
        analysis_type = "resting"

    research_goal = args.get("research_goal", "")
    project_scale = args.get("project_scale", "unknown")
    stage = args.get("stage", "planning")
    event_types = args.get("event_types", [])
    srate = args.get("srate")
    has_ica = args.get("has_ica", False)

    common = ["eeglab_init", "eeglab_load_data", "eeglab_info recording/channel/event audit", "eeglab_qc_report"]
    parameters: dict[str, Any] = {
        "analysis_type_requested": requested_analysis_type,
        "analysis_type_resolved": analysis_type,
        "research_goal": research_goal,
        "project_scale": project_scale,
        "stage": stage,
        "event_types": event_types,
        "srate": srate,
        "has_ica": has_ica,
        "data_shape": data_shape,
        "has_channel_locations": has_channel_locations,
    }
    base_hints = [
        "Preserve the raw dataset; write transformed outputs to a new path.",
        "Report acquisition/recording facts before analysis: sampling rate, duration, channel count, montage/channel-location coverage, reference, event labels/counts, and processing history.",
        "Audit event latencies and labels before event-locked analyses.",
    ]
    required_user_decisions: list[str] = []
    clarifying_questions: list[str] = []
    default_assumptions: list[str] = []

    if not research_goal:
        required_user_decisions.append("primary research goal or hypothesis")
        clarifying_questions.append(
            "What is the primary research goal: ERP, resting-state spectrum/connectivity, time-frequency, ICA cleanup, source localization, or group/STUDY analysis?"
        )
        default_assumptions.append(
            f"No research_goal was supplied; using analysis_type_resolved={analysis_type} from event/data-shape hints."
        )
    if project_scale == "unknown":
        required_user_decisions.append("project scale and grouping")
        clarifying_questions.append("Is this single-subject, multi-subject, BIDS/STUDY, or exploratory QC work?")
        default_assumptions.append("Project scale is unknown; start with single-subject provenance/QC before group-level assumptions.")
    if analysis_type in {"erp", "timefreq"} and not event_types:
        required_user_decisions.append("event labels and task conditions")
        clarifying_questions.append("Which event labels define the conditions/epochs, and what epoch/baseline windows match the study design?")
        default_assumptions.append("No event labels were supplied; inspect events and avoid event-locked analysis until labels are confirmed.")
    if has_channel_locations is False:
        required_user_decisions.append("montage/channel-location repair")
        clarifying_questions.append("Can you provide the cap montage/channel-location file, or should analysis avoid topography/source outputs?")
    if srate is None:
        required_user_decisions.append("sampling rate and acquisition details")
        clarifying_questions.append("What sampling rate, reference, amplifier/cap montage, and acquisition filters were used if not preserved in the file?")

    if analysis_type == "erp":
        steps = common + [
            "eeglab_filter bandpass 0.1-40 Hz or study-specific cutoffs",
            "optional eeglab_clean_line_noise",
            "optional ICA review" if has_ica else "optional eeglab_run_ica + eeglab_classify_ica",
            "eeglab_epoch with explicit event_types",
            "eeglab_erp_analysis",
            "eeglab_save_data to a new output path",
        ]
        hints = base_hints + ["Use event audit first; ERP is not meaningful without validated event labels."]
        if not event_types:
            hints.append("No event_types were supplied; inspect events before epoching.")
    elif analysis_type == "resting":
        steps = common + [
            "eeglab_filter highpass 0.5/1 Hz and lowpass 45/80 Hz as appropriate",
            "eeglab_clean_line_noise",
            "optional conservative eeglab_clean_rawdata",
            "eeglab_reref",
            "eeglab_spectral",
        ]
        hints = base_hints + ["Avoid event-locked interpretations for resting-state outputs."]
    elif analysis_type == "timefreq":
        steps = common + [
            "inspect events and epoch windows",
            "eeglab_filter with study-specific high-frequency ceiling",
            "eeglab_epoch",
            "eeglab_timefreq with explicit cycles/freq_range/baseline",
        ]
        hints = base_hints + ["Time-frequency settings should be justified by the frequencies of interest."]
    elif analysis_type == "ica":
        steps = common + [
            "filter for ICA, commonly highpass 1 Hz",
            "remove/interpolate clearly bad channels when justified",
            "eeglab_run_ica",
            "eeglab_classify_ica",
            "review before eeglab_remove_components",
        ]
        hints = base_hints + ["Do not automatically remove components without reporting thresholds and classes."]
    elif analysis_type == "study":
        steps = common + ["organize BIDS/datasets", "eeglab_study_create", "eeglab_study_design", "eeglab_study_statistics"]
        hints = base_hints + ["Run stable single-subject preprocessing before group-level STUDY statistics."]
    else:
        steps = common + ["confirm ICA and channel locations", "eeglab_source_settings", "eeglab_source_localization"]
        hints = base_hints + ["Source localization requires correct channel locations and DIPFIT resources."]

    if srate and srate > 500:
        hints.append("Consider resampling for computational efficiency after confirming analysis requirements.")
    if has_channel_locations is False:
        hints.append("Channel locations are missing; load or repair montage metadata before topography/source workflows.")
    if data_shape == "epoched" and analysis_type in {"ica", "resting"}:
        hints.append("The data appears epoched; confirm this is appropriate before ICA or resting-state spectral analysis.")

    project_phases = [
        "0_project_intake: define hypothesis, project scale, subject/session structure, data format, and required outputs",
        "1_recording_provenance_audit: preserve raw files; inspect sampling rate, data shape, duration, channel montage, reference, event markers, BIDS/comments, and history",
        "2_qc_gate_before_processing: verify loadability, event integrity, channel-location coverage, missing metadata, and plugin prerequisites",
        "3_single_subject_preprocessing: apply transparent filtering, line-noise cleanup, rereferencing, bad-channel handling, ICA/ICLabel when justified, and save named intermediates",
        "4_analysis_branch: run ERP, resting-state spectral/connectivity, time-frequency, source, or STUDY workflow according to validated design",
        "5_output_and_reporting: save processed datasets/figures/tables, report exact parameters and limitations, and avoid clinical claims",
        "6_project_evolution: turn repeated failures/decisions into updated protocol notes, eval prompts, and skill guidance after review",
    ]
    qc_gates = [
        "raw_input_preserved",
        "recording_metadata_reported",
        "channel_location_coverage_checked",
        "event_labels_and_latencies_checked",
        "processing_history_or_session_steps_recorded",
        "analysis_branch_matches_study_design",
        "destructive_steps_write_new_outputs",
        "artifact_rejection_thresholds_reported",
        "outputs_and_limitations_reported",
    ]
    adaptive_decision_rules = [
        "If research_goal is missing, ask for it; if unavailable, infer a conservative first-pass path from events and data_shape.",
        "If event_types are present, ERP/time-frequency branches are candidates; if events are absent, prefer resting-state QC/spectral analysis.",
        "If data_shape is epoched, avoid resting-state or ICA assumptions until the original continuous data or study design is confirmed.",
        "If channel locations are incomplete, avoid topography/source localization until montage metadata is repaired.",
        "If ICA is absent, run ICA only after continuous-data suitability, filtering, rank/reference, and plugin availability are checked.",
        "For multi-subject or BIDS projects, stabilize single-subject preprocessing before STUDY/group statistics.",
    ]
    self_evolution_hooks = [
        "Capture missing metadata, failed tools, plugin gaps, and parameter decisions in the session report.",
        "After a project pattern repeats, update workflow references/evals so future agents ask the right questions earlier.",
        "Do not silently change scientific defaults; record each default, rationale, and condition under which it should be revised.",
        "Prefer adding eval prompts for new research patterns before treating them as supported workflows.",
    ]

    return workflow_success(
        "eeglab_workflow_recommend",
        steps=[{"name": step, "status": "recommended"} for step in steps],
        parameters=parameters,
        outputs={},
        summary={
            "analysis_type_requested": requested_analysis_type,
            "analysis_type_resolved": analysis_type,
            "project_phases": project_phases,
            "recommended_steps": steps,
            "hints": hints,
            "required_user_decisions": required_user_decisions,
            "clarifying_questions": clarifying_questions,
            "default_assumptions": default_assumptions,
            "qc_gates": qc_gates,
            "adaptive_decision_rules": adaptive_decision_rules,
            "self_evolution_hooks": self_evolution_hooks,
            "minimum_report_fields": [
                "input_path",
                "output_path",
                "sampling_rate_hz",
                "duration_sec",
                "channel_count",
                "channel_location_coverage",
                "reference",
                "event_labels_and_counts",
                "filter_cutoffs",
                "rereference",
                "epoch_and_baseline_windows",
                "artifact_rejection_or_ica_decisions",
                "software_and_plugin_limitations",
            ],
        },
    )


def light_erp_parameters(args: dict[str, Any]) -> dict[str, Any]:
    """Normalize light ERP workflow parameters."""
    output_dir = str(Path(args["output_dir"]).resolve())
    output_filename = safe_output_filename(args.get("output_filename"), default="light_erp_processed.set")
    output_path = Path(output_dir) / output_filename
    return {
        "data_path": str(Path(args["data_path"]).resolve()),
        "output_dir": output_dir,
        "output_filename": output_filename,
        "output_path": str(output_path),
        "output_fdt_path": str(output_path.with_suffix(".fdt")),
        "low_cutoff": args.get("low_cutoff", 0.5),
        "high_cutoff": args.get("high_cutoff", 40.0),
        "event_types": args.get("event_types", ["target", "standard"]),
        "epoch_window": args.get("epoch_window", [-0.2, 0.8]),
        "baseline_window": args.get("baseline_window", [-200, 0]),
        "channels": args.get("channels", ["Cz"]),
        "time_window": args.get("time_window", [250, 450]),
    }
